from PIL import Image
from os.path import splitext, basename
from time import time
from cv2 import VideoCapture, imwrite

class Thumbnail():
    def __init__(self,
            postfix: str = '_thumb',
            max_size: tuple = (250, 250),
            alt_img_thumb: str = '',
            alt_vid_thumb: str = '',
            alt_aud_thumb: str = ''):
        self.__postfix = postfix
        self.__max_size = max_size
        self.__ftypes = {
                'image': ['png', 'jpg', 'jpeg', 'gif'],
                'video': ['webm', 'mp4', 'mkv'],
                'audio': ['ogg', 'mp3']
        }
        self.__alt_thumb = {
                'image': alt_img_thumb,
                'video': alt_vid_thumb,
                'audio': alt_aud_thumb
        }

    def __thumb(self, dest: str, src: str):
        image = Image.open(src)

        if not image.mode == 'RGB':
            image = image.convert('RGB')

        image.thumbnail(self.__max_size)
        image.save(dest)

    def generate(self, filepath: str) -> (str, bool, str):
        file_name, file_ext = splitext(filepath)
        new_filename = file_name+self.__postfix+'.jpg'
        has_thumb = False
        alt_thumb = ''
        cmp_ext = file_ext[1:]

        if cmp_ext in self.__ftypes['image']:
            self.__thumb(new_filename, filepath)
            has_thumb = True
        elif cmp_ext in self.__ftypes['video']:
            video_cap = VideoCapture(filepath)
            success, image = video_cap.read()
            if success:
                imwrite(new_filename, image)
                self.__thumb(new_filename, new_filename)
                has_thumb = True
            else:
                alt_thumb = self.__alt_thumb['video']
        elif cmp_ext in self.__ftypes['audio']:
            alt_thumb = self.__alt_thumb['audio']

        return (basename(new_filename), has_thumb, alt_thumb)

    @staticmethod
    def store_name(filename: str) -> str:
        _, file_ext = splitext(filename)
        return str(int(time()))+file_ext

