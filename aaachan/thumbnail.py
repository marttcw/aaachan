from PIL import Image
from os.path import splitext, basename
from time import time

class Thumbnail():
    def __init__(self, postfix: str = '_thumb', max_size: tuple = (250, 250)):
        self.__postfix = postfix
        self.__max_size = max_size

    def generate(self, filepath: str) -> str:
        file_name, file_ext = splitext(filepath)
        new_filename = file_name+self.__postfix+'.jpg'

        image = Image.open(filepath)

        if not image.mode == 'RGB':
            image = image.convert('RGB')

        image.thumbnail(self.__max_size)
        image.save(new_filename)

        return basename(new_filename)

    @staticmethod
    def store_name(filename: str) -> str:
        _, file_ext = splitext(filename)
        return str(int(time()))+file_ext

