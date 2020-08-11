import psycopg2
from .login import Login
from .timestamp import Timestamp

PSYCOPGPREFIX = "psycopg2 msg: "

class Database():
    def __init__(self):
        self.__conn = None
        self.__cursor = None

    def open(self, host: str, dbname: str, user: str, password: str) -> None:
        try:
            self.__conn = psycopg2.connect(host=host,
                    database=dbname,
                    user=user,
                    password=password)

            print(PSYCOPGPREFIX+"Connecting to database at '{}'...".format(host))
            self.__cursor = self.__conn.cursor()
            print(PSYCOPGPREFIX+"Connected")
        except Exception as e:
            print(PSYCOPGPREFIX+" "+str(e))
            print(PSYCOPGPREFIX+"Unable to connect to the database.")

    # Only use this during development, never in production/release
    def delete_db(self) -> None:
        self.__cursor.execute("DROP TABLE IF EXISTS users;")
        self.__cursor.execute("DROP TABLE IF EXISTS posts;")
        self.__cursor.execute("DROP TABLE IF EXISTS threads;")
        self.__cursor.execute("DROP TABLE IF EXISTS files;")
        self.__cursor.execute("DROP TABLE IF EXISTS boards;")
        self.__cursor.execute("DROP TABLE IF EXISTS categories;")
        self.__conn.commit()

    def create_db(self) -> None:
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS users("+\
                    "id             serial          PRIMARY KEY,"+\
                    "name           varchar(64)     NOT NULL UNIQUE,"+\
                    "pass           text            NOT NULL,"+\
                    "salt           text            NOT NULL,"+\
                    "type           char(1)         NOT NULL"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS categories("+\
                    "id             serial          PRIMARY KEY,"+\
                    "name           text            NOT NULL UNIQUE"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS boards("+\
                    "id             serial          PRIMARY KEY,"+\
                    "directory      varchar(64)     NOT NULL UNIQUE,"+\
                    "name           varchar(128)    NOT NULL UNIQUE,"+\
                    "description    text            NOT NULL,"+\
                    "type           char(1)         NOT NULL,"+\
                    "next_id        bigint          NOT NULL,"+\
                    "nsfw           boolean         NOT NULL,"+\
                    "category_id    int             NOT NULL,"+\
                    "CONSTRAINT fk_category_id "+\
                        "FOREIGN KEY(category_id) "+\
                            "REFERENCES categories(id) "+\
                            "ON DELETE CASCADE"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS files("+\
                    "id             serial          PRIMARY KEY,"+\
                    "filepath       text            NOT NULL,"+\
                    "storepath      text            NOT NULL UNIQUE,"+\
                    "thumbpath      text"
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS threads("+\
                    "id             serial          PRIMARY KEY,"+\
                    "board_id       int             NOT NULL,"+\
                    "post_id        bigint          NOT NULL,"+\
                    "title          varchar(256)    NOT NULL,"+\
                    "content        text            NOT NULL,"+\
                    "file_id        int,"+\
                    "ts_op          timestamp       NOT NULL,"+\
                    "ts_bump        timestamp       NOT NULL,"+\
                    "CONSTRAINT fk_board_id "+\
                        "FOREIGN KEY(board_id) "+\
                            "REFERENCES boards(id) "+\
                            "ON DELETE CASCADE,"+\
                    "CONSTRAINT fk_file_id "+\
                        "FOREIGN KEY(file_id) "+\
                            "REFERENCES files(id) "+\
                            "ON DELETE CASCADE"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS posts("+\
                    "id             serial          PRIMARY KEY,"+\
                    "thread_id      int             NOT NULL,"+\
                    "post_id        bigint          NOT NULL,"+\
                    "title          varchar(256)    NOT NULL,"+\
                    "content        text            NOT NULL,"+\
                    "file_id        int,"+\
                    "ts             timestamp       NOT NULL,"+\
                    "CONSTRAINT fk_thread_id "+\
                        "FOREIGN KEY(thread_id) "+\
                            "REFERENCES threads(id) "+\
                            "ON DELETE CASCADE,"+\
                    "CONSTRAINT fk_file_id "+\
                        "FOREIGN KEY(file_id) "+\
                            "REFERENCES files(id) "+\
                            "ON DELETE CASCADE"+\
                ");")
        self.__conn.commit()
        print(PSYCOPGPREFIX+"Table created successfully")

    def new_admin(self, admin_username: str, admin_pass: str) -> None:
        db_pass = Login.generate(admin_pass)
        self.__cursor.execute("INSERT INTO users(name, pass, salt, type)"+\
                " VALUES (%s,%s,%s,%s)",
                (admin_username, db_pass['hashed'], db_pass['salt'], 'a'));
        self.__conn.commit()

    def verify_user(self, username: str, password: str) -> bool:
        self.__cursor.execute("SELECT pass, salt FROM users WHERE name = %s;", (username,))
        sql_list = self.__cursor.fetchall()
        if len(sql_list) == 0:
            return False
        else:
            got_pass = sql_list[0][0]
            got_salt = sql_list[0][1]
            return Login.match(got_pass, password, got_salt)

    def new_thread(self, board_directory: str, title: str, content: str,
            filepath: str, storepath: str, thumbpath: str) -> bool:
        # Fetch board information
        self.__cursor.execute("SELECT id, next_id FROM boards WHERE directory = %s;",
                (board_directory,))
        sql_list = self.__cursor.fetchall()
        if len(sql_list) == 0:
            return False
        board_id = sql_list[0][0]
        next_id = int(sql_list[0][1])

        # Insert file entry
        self.__cursor.execute("INSERT INTO"+\
                " files(filepath, storepath, thumbpath)"+\
                " VALUES (%s, %s, %s)"+\
                " RETURNING id;",
                (filepath, storepath, thumbpath))
        sql_list = self.__cursor.fetchall()
        if len(sql_list) == 0:
            return False
        file_id = sql_list[0][0]
        self.__conn.commit()

        # Insert new thread entry
        now_ts = Timestamp.now()
        self.__cursor.execute("INSERT INTO"+\
                " threads(board_id, post_id, title, content, file_id, ts_op, ts_bump)"+\
                " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (board_id, next_id, title, content, file_id, now_ts, now_ts))

        # Update next_id
        self.__cursor.execute("UPDATE boards SET next_id = %s WHERE id = %s;",
                (next_id + 1, board_id))
        self.__conn.commit()

    def new_post(self, board_directory: str, thread_id: int, title: str,
            content: str, filepath: str, storepath: str, thumbpath: str) -> (bool, str):
        # Fetch board information
        self.__cursor.execute("SELECT id, next_id FROM boards WHERE directory = %s;",
                (board_directory,))
        sql_list = self.__cursor.fetchall()
        if len(sql_list) == 0:
            return (False, "Cannot fetch board")
        board_id = sql_list[0][0]
        next_id = int(sql_list[0][1])

        # Fetch thread information
        self.__cursor.execute("SELECT threads.id FROM threads LEFT JOIN boards"+\
                " ON threads.board_id = boards.id"+\
                " WHERE threads.post_id = %s AND boards.directory = %s;",
                (thread_id, board_directory))
        sql_list = self.__cursor.fetchall()
        if len(sql_list) == 0:
            return (False, "Cannot fetch thread")
        thread_id_pk = sql_list[0][0]

        if filepath != '':
            # Insert file entry
            self.__cursor.execute("INSERT INTO"+\
                    " files(filepath, storepath, thumbpath)"+\
                    " VALUES (%s, %s, %s)"+\
                    " RETURNING id;",
                    (filepath, storepath, thumbpath))
            sql_list = self.__cursor.fetchall()
            if len(sql_list) == 0:
                return (False, "Cannot get file ID")
            file_id = sql_list[0][0]
            self.__conn.commit()
        else:
            file_id = None

        # Insert new post entry
        now_ts = Timestamp.now()
        self.__cursor.execute("INSERT INTO"+\
                " posts(thread_id, post_id, title, content, file_id, ts)"+\
                " VALUES (%s, %s, %s, %s, %s, %s)",
                (thread_id_pk, next_id, title, content, file_id, now_ts))

        # Update next_id
        self.__cursor.execute("UPDATE boards SET next_id = %s WHERE id = %s;",
                (next_id + 1, board_id))

        # Update thread bump timestamp
        self.__cursor.execute("UPDATE threads SET ts_bump = %s WHERE id = %s;",
                (now_ts, thread_id_pk))

        self.__conn.commit()

        return (True, "")

    def delete_thread(self, board_directory: str, thread_id: int) -> bool:
        pass

    def delete_post(self, board_directory: str, thread_id: int, post_id: int) -> bool:
        pass

    def get_thread_posts(self, board_directory: str, thread_id: int) -> list:
        self.__cursor.execute("SELECT"+\
                " threads.post_id, threads.title, threads.content,"+\
                " threads.ts_op, threads.ts_bump,"+\
                " files.filepath, files.storepath, files.thumbpath"+\
                " FROM threads"+\
                " INNER JOIN files"+\
                " ON threads.file_id = files.id"+\
                " LEFT JOIN boards"+\
                " ON threads.board_id = boards.id"+\
                " WHERE boards.directory = %s AND threads.post_id = %s"+\
                " ORDER BY threads.ts_bump DESC;",
                (board_directory, thread_id))
        sql_list = self.__cursor.fetchall()
        if len(sql_list) == 0:
            return []

        thread_op = sql_list[0]

        posts_list = [{
            'id': thread_op[0],
            'title': thread_op[1],
            'content': thread_op[2],
            'timestamp': thread_op[3],
            'filepath': thread_op[5],
            'storepath': thread_op[6],
            'thumbpath': thread_op[7],
        }]

        # Append to the posts_list with the following posts
        self.__cursor.execute("SELECT"+\
                    " posts.post_id, posts.title, posts.content,"+\
                    " posts.ts,"+\
                    " files.filepath, files.storepath, files.thumbpath"+\
                    " FROM"+\
                    " posts INNER JOIN threads"+\
                    " ON posts.thread_id = threads.id"+\
                    " LEFT JOIN files"+\
                    " ON posts.file_id = files.id"+\
                    " LEFT JOIN boards"+\
                    " ON threads.board_id = boards.id"+\
                    " WHERE threads.post_id = %s AND boards.directory = %s"+\
                    " ORDER BY posts.post_id ASC;",
                    (thread_id, board_directory))
        sql_list = self.__cursor.fetchall()

        for post in sql_list:
            posts_list.append({
                'id': post[0],
                'title': post[1],
                'content': post[2],
                'timestamp': post[3],
                'filepath': post[4],
                'storepath': post[5],
                'thumbpath': post[6],
            })

        return posts_list
    
    def get_threads(self, board_directory: str) -> list:
        self.__cursor.execute("SELECT"+\
                " threads.post_id, threads.title, threads.content,"+\
                " threads.ts_op, threads.ts_bump,"+\
                " files.filepath, files.storepath, files.thumbpath"+\
                " FROM threads INNER JOIN files"+\
                " ON threads.file_id = files.id"+\
                " LEFT JOIN boards"+\
                " ON threads.board_id = boards.id"+\
                " WHERE boards.directory = %s"+\
                " ORDER BY threads.ts_bump DESC;",
                (board_directory,))
        sql_list = self.__cursor.fetchall()
        if len(sql_list) == 0:
            return []

        threads_list = []

        for row in sql_list:
            threads_list.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'timestamp_op': row[3],
                'timestamp_bump': row[4],
                'filepath': row[5],
                'storepath': row[6],
                'thumbpath': row[7]
            })

        return threads_list

    def new_board(self, directory: str, name: str, description: str,
            btype: str, category_id: int, nsfw: bool) -> None:
        self.__cursor.execute("INSERT INTO boards(directory, name, description,"+\
                " type, next_id, category_id, nsfw)"+\
                " VALUES (%s,%s,%s,%s,%s,%s,%s);",
                (directory, name, description, btype, 1, category_id, nsfw))
        self.__conn.commit()

    def edit_board(self, directory: str, name: str, description: str,
            btype: str, category_id: int, nsfw: bool) -> None:
        self.__cursor.execute("UPDATE boards SET"+\
                " name = %s,"+\
                " description = %s,"+\
                " type = %s,"+\
                " category_id = %s,"+\
                " nsfw = %s"+\
                " WHERE directory = %s;",
                (name, description, btype, category_id, nsfw, directory))
        self.__conn.commit()

    def get_board(self, directory: str) -> dict:
        self.__cursor.execute("SELECT name, description, type, next_id, nsfw, category_id"+\
                " FROM boards WHERE directory = %s;",
                (directory,))
        sql_list = self.__cursor.fetchall()
        if len(sql_list) == 0:
            return {
                    'exists': False
            }
        else:
            board = sql_list[0]
            return {
                    'exists': True,
                    'name': board[0],
                    'description': board[1],
                    'type': board[2],
                    'next_id': board[3],
                    'nsfw': bool(board[4]),
                    'category_id': int(board[5])
            }

    def get_boards(self) -> list:
        self.__cursor.execute("SELECT boards.directory, boards.name, boards.nsfw,"+\
                    " categories.id, categories.name"+\
                " FROM boards INNER JOIN categories"+\
                " ON boards.category_id = categories.id"+\
                " ORDER BY categories.name ASC, boards.directory ASC;")
        sql_list = self.__cursor.fetchall()
        ret_list = []
        cur_cat_list = []
        prev_cat_id = -1
        for row in sql_list:
            cur_cat_id = int(row[3])
            if prev_cat_id != cur_cat_id:
                # Create category
                ret_list.append({
                    'name': row[4],
                    'boards': []
                })

            # Append board to current category
            ret_list[-1]['boards'].append({
                'dir': row[0],
                'name': row[1],
                'nsfw': bool(row[2])
            })

            prev_cat_id = cur_cat_id
        return ret_list

    def new_category(self, name: str) -> int:
        self.__cursor.execute("INSERT INTO categories(name) VALUES (%s);",
                (name,))
        self.__conn.commit()

        self.__cursor.execute("SELECT id FROM categories WHERE name = %s;",
                (name,))
        sql_list = self.__cursor.fetchall()
        if len(sql_list) == 0:
            return -1
        else:
            return int(sql_list[0][0])

    def get_categories_select(self) -> list:
        categories_list = [(-1, 'New Category')]

        self.__cursor.execute("SELECT id, name FROM categories ORDER BY name ASC;")
        sql_list = self.__cursor.fetchall()
        for row in sql_list:
            categories_list.append((
                int(row[0]), row[1]
            ))

        return categories_list

    def get_newest_ten(self) -> list:
        self.__cursor.execute("SELECT"+\
                " boards.directory, posts.ts, posts.content FROM posts"+\
                " LEFT JOIN threads ON posts.thread_id = threads.id"+\
                " LEFT JOIN boards ON threads.board_id = boards.id"+\
                " ORDER BY ts DESC FETCH FIRST 10 ROWS ONLY;")
        sql_list = self.__cursor.fetchall()
        newest_list = []
        for row in sql_list:
            newest_list.append({
                'directory': row[0],
                'timestamp': row[1],
                'content': row[2]
            })
        return newest_list

    def close(self) -> None:
        print(PSYCOPGPREFIX+"Closing session...")
        self.__cursor.close()
        self.__conn.close()

