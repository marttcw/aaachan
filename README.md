# aaachan - Anonymous Imageboard Software
Anonymous imageboard software written in Python + Flask and uses PostgreSQL for database

It has the basic imageboard features expected, such as boards for different
topics, image attachments, quoting, and moderation. It is anonymous and
requires no account to post and view.

## Features
* Support for non-JavaScript browsers
* Posting
  * No accounts required
  * Quoting
  * Multiple of files per post
* Moderation
  * Post reporting
* Pages
  * Dynamic page creation

## Requirements
* Python >= 3.6

### Dependencies
* [Flask](https://flask.palletsprojects.com/en/1.1.x/#) - Framework for web application
* [Flask-Minify](https://github.com/mrf345/flask_minify/) - Flask extension to minify request's response for html, css, and js
* [psycopg2](https://www.psycopg.org/) - PostgreSQL adapter for Python
* [wtforms](https://wtforms.readthedocs.io/en/2.3.x/) - Flexible form validation and rendering library for Python web development
* [flask-wtf](https://github.com/lepture/flask-wtf) - Simple integration of Flask and WTForms
* [Pillow](https://python-pillow.org/) - Pillow - PIL fork - Python Imaging Library
* [opencv-python](https://github.com/skvark/opencv-python) - Wrapper package for OpenCV python binding

### Optional
* [pytest](https://docs.pytest.org/en/stable/) - Python unit testing
* [Sphinx](https://www.sphinx-doc.org/en/master/) - Python documentation
  * [sphinx-autodoc-typehints](https://github.com/agronholm/sphinx-autodoc-typehints) - Documenting typehinting for Sphinx

### Additional Requirement
* Postgresql installed in your system

## Running

### Python Virtual Environment
* `python3 -m venv .venv`

### Installation
* Either: `pip install -r requirements.txt` or `pip install Flask Flask-Minify psycopg2 wtforms flask_wtf Pillow pytest sphinx sphinx-autodoc-typehints opencv-python`

### Running without installation

#### Using `flask run`
* `export FLASK_APP=aaachan`
* `flask run`

#### Directly as a package
* `python -m aaachan`

## Setup
* When the web server setups up the first time, it will just go straight to the `setup/` page

## Documentation
Uses [reStructuredText](https://docutils.sourceforge.io/rst.html) formatting for documentation

`:type` and `:rtype` are not necessary since the typehinting generation are generated by the sphinx-autodoc-typehints extension

### Generation
* `cd docs/`
* `make html`
* `cd build/html/`

