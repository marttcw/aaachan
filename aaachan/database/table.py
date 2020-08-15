import psycopg2

class Table():
    def __init__(self, conn, cursor):
        self.__conn = conn
        self.__cursor = cursor

    def delete_db(self) -> None:
        self.__cursor.execute("DROP TABLE IF EXISTS posts_files;")
        self.__cursor.execute("DROP TABLE IF EXISTS bans;")
        self.__cursor.execute("DROP TABLE IF EXISTS reports;")
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
                    "files_types    text            NOT NULL,"+\
                    "files_limit    int             NOT NULL,"+\
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
                    "ts_op          timestamp       NOT NULL,"+\
                    "ts_bump        timestamp       NOT NULL,"+\
                    "ip_address     text            NOT NULL,"+\
                    "CONSTRAINT fk_board_id "+\
                        "FOREIGN KEY(board_id) "+\
                            "REFERENCES boards(id) "+\
                            "ON DELETE CASCADE"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS posts("+\
                    "id             serial          PRIMARY KEY,"+\
                    "thread_id      int             NOT NULL,"+\
                    "post_id        bigint          NOT NULL,"+\
                    "title          varchar(256)    NOT NULL,"+\
                    "content        text            NOT NULL,"+\
                    "ts             timestamp       NOT NULL,"+\
                    "ip_address     text            NOT NULL,"+\
                    "CONSTRAINT fk_thread_id "+\
                        "FOREIGN KEY(thread_id) "+\
                            "REFERENCES threads(id) "+\
                            "ON DELETE CASCADE"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS posts_files("+\
                    "id             serial          PRIMARY KEY,"+\
                    "thread_id      int,"+\
                    "post_id        int,"+\
                    "file_id        int             NOT NULL,"+\
                    "CONSTRAINT fk_thread_id "+\
                        "FOREIGN KEY(thread_id) "+\
                            "REFERENCES threads(id) "+\
                            "ON DELETE CASCADE,"+\
                    "CONSTRAINT fk_post_id "+\
                        "FOREIGN KEY(post_id) "+\
                            "REFERENCES posts(id) "+\
                            "ON DELETE CASCADE,"+\
                    "CONSTRAINT fk_file_id "+\
                        "FOREIGN KEY(file_id) "+\
                            "REFERENCES files(id) "+\
                            "ON DELETE CASCADE"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS bans("+\
                    "id             serial          PRIMARY KEY,"+\
                    "ip_address     text            NOT NULL,"+\
                    "reason         text            NOT NULL,"+\
                    "ts_start       timestamp       NOT NULL,"+\
                    "ts_end         timestamp"+\
                ");")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS reports("+\
                    "id             serial          PRIMARY KEY,"+\
                    "board_id       int             NOT NULL,"+\
                    "thread_id      int,"+\
                    "post_id        int,"+\
                    "reason         text            NOT NULL,"+\
                    "ts             timestamp       NOT NULL,"+\
                    "CONSTRAINT fk_board_id "+\
                        "FOREIGN KEY(board_id) "+\
                            "REFERENCES boards(id) "+\
                            "ON DELETE CASCADE,"+\
                    "CONSTRAINT fk_thread_id "+\
                        "FOREIGN KEY(thread_id) "+\
                            "REFERENCES threads(id) "+\
                            "ON DELETE CASCADE,"+\
                    "CONSTRAINT fk_post_id "+\
                        "FOREIGN KEY(post_id) "+\
                            "REFERENCES posts(id) "+\
                            "ON DELETE CASCADE"+\
                ");")
        self.__conn.commit()

