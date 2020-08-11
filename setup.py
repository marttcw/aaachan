from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
        name='aaachan',
        version='0.0.1',
        description='Imageboard written in Python + Flask',
        long_description=long_description,
        long_description_content_type='text/markdown',
        python_requires='>=3.6',
        install_requires=[
            'Flask', 'Flask-Minify', 'psycopg2', 'wtforms'
        ],
        entry_points = {
              'console_scripts': [
                  'aaachan = aaachan.__main__:main'
              ],              
          }
)

