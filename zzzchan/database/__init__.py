import psycopg2
from .login import Login

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
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS posts("+\
                    "id             serial          PRIMARY KEY,"+\
                    "board_id       int,"+\
                    "post_id        bigint,"+\
                    "title          varchar(256)    NOT NULL,"+\
                    "content        text            NOT NULL,"+\
                    "filepath       text,"+\
                    "CONSTRAINT fk_board_id "+\
                        "FOREIGN KEY(board_id) "+\
                            "REFERENCES boards(id) "+\
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
        self.__cursor.execute("SELECT directory, name FROM boards;")
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

