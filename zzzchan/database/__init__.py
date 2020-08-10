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
        self.__cursor.execute("DROP TABLE IF EXISTS boards;")
        self.__conn.commit()

    def create_db(self) -> None:
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS users("+\
                    "id             serial          PRIMARY KEY,"+\
                    "name           varchar(64)     NOT NULL,"+\
                    "pass           text            NOT NULL,"+\
                    "salt           text            NOT NULL,"+\
                    "type           char(1)         NOT NULL"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS boards("+\
                    "id             serial          PRIMARY KEY,"+\
                    "directory      varchar(64)     NOT NULL,"+\
                    "name           varchar(128)    NOT NULL,"+\
                    "description    text            NOT NULL,"+\
                    "type           char(1)         NOT NULL,"+\
                    "next_id        bigint          NOT NULL"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS threads("+\
                    "id             serial          PRIMARY KEY,"+\
                    "board_id       int,"+\
                    "post_id        bigint,"+\
                    "title          varchar(256)    NOT NULL,"+\
                    "content        text            NOT NULL,"+\
                    "filepath       text            NOT NULL,"+\
                    "ts_op          timestamp       NOT NULL,"+\
                    "ts_bump        timestamp       NOT NULL,"+\
                    "CONSTRAINT fk_board_id "+\
                        "FOREIGN KEY(board_id) "+\
                            "REFERENCES boards(id) "+\
                            "ON DELETE CASCADE"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS posts("+\
                    "id             serial          PRIMARY KEY,"+\
                    "thread_id      int,"+\
                    "post_id        bigint,"+\
                    "title          varchar(256)    NOT NULL,"+\
                    "content        text            NOT NULL,"+\
                    "filepath       text,"+\
                    "ts             timestamp       NOT NULL,"+\
                    "CONSTRAINT fk_thread_id "+\
                        "FOREIGN KEY(thread_id) "+\
                            "REFERENCES threads(id) "+\
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

    def new_thread(self, board_directory: str, title: str, content: str, filepath: str) -> bool:
        # Fetch board information
        self.__cursor.execute("SELECT id, next_id FROM boards WHERE directory = %s;",
                (board_directory,))
        sql_list = self.__cursor.fetchall()
        if len(sql_list) == 0:
            return False

        # Insert new thread entry
        board_id = sql_list[0][0]
        next_id = int(sql_list[0][1])
        now_ts = Timestamp.now()
        self.__cursor.execute("INSERT INTO"+\
                " threads(board_id, post_id, title, content, filepath, ts_op, ts_bump)"+\
                " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (board_id, next_id, title, content, filepath, now_ts, now_ts))

        # Update next_id
        self.__cursor.execute("UPDATE boards SET next_id = %s WHERE id = %s;",
                (next_id + 1, board_id))
        self.__conn.commit()

    def new_post(self, board_directory: str, thread_id: int, title: str,
            content: str, filepath: str) -> (bool, str):
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
        now_ts = Timestamp.now()

        # Insert new post entry
        self.__cursor.execute("INSERT INTO"+\
                " posts(thread_id, post_id, title, content, filepath, ts)"+\
                " VALUES (%s, %s, %s, %s, %s, %s)",
                (thread_id_pk, next_id, title, content, filepath, now_ts))

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
                " threads.filepath, threads.ts_op"+\
                " FROM threads INNER JOIN boards"+\
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
            'filepath': thread_op[3],
            'timestamp': thread_op[4]
        }]

        # Append to the posts_list with the following posts
        self.__cursor.execute("SELECT"+\
                    " posts.post_id, posts.title, posts.content,"+\
                    " posts.filepath, posts.ts"+\
                    " FROM"+\
                    " posts INNER JOIN threads"+\
                    " ON posts.thread_id = threads.id"+\
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
                'filepath': post[3],
                'timestamp': post[4]
            })

        return posts_list
    
    def get_threads(self, board_directory: str) -> list:
        self.__cursor.execute("SELECT"+\
                " threads.post_id, threads.title, threads.content,"+\
                " threads.filepath, threads.ts_op, threads.ts_bump"+\
                " FROM threads INNER JOIN boards"+\
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
                'filepath': row[3],
                'timestamp_op': row[4],
                'timestamp_bump': row[5]
            })

        return threads_list

    def new_board(self, directory: str, name: str, description: str, btype: str) -> None:
        self.__cursor.execute("INSERT INTO boards(directory, name, description, type, next_id)"+\
                " VALUES (%s,%s,%s,%s,%s)",
                (directory, name, description, btype, 1));
        self.__conn.commit()

    def get_board(self, directory: str) -> dict:
        self.__cursor.execute("SELECT name, description FROM boards WHERE directory = %s;", (directory,))
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
                    'description': board[1]
            }

    def get_boards(self) -> list:
        self.__cursor.execute("SELECT directory, name FROM boards ORDER BY directory ASC;")
        sql_list = self.__cursor.fetchall()
        ret_list = []
        for row in sql_list:
            ret_list.append({
                'dir': row[0],
                'name': row[1]
            })
        return ret_list

    def close(self) -> None:
        print(PSYCOPGPREFIX+"Closing session...")
        self.__cursor.close()
        self.__conn.close()

