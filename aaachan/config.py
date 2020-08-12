import configparser

INI_FNAME = 'config.ini'

class Config():
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__config['site'] = {
                'name': '',
                'description': ''
        }
        self.__config['database'] = {
                'host': 'localhost',
                'name': 'aaachan-db',
                'user': 'postgres',
                'pass': 'aaachan'
        }

    def write(self):
        with open(INI_FNAME, 'w') as configfile:
            self.__config.write(configfile)

    def read(self):
        self.__config.read(INI_FNAME)

    def get(self):
        return self.__config

