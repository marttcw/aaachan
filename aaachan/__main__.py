from flask import Flask, render_template, request, flash, redirect, url_for, session, send_from_directory
from flask_minify import minify
from werkzeug.utils import secure_filename

import os

from .database import Database
from .forms import SetupForm, NewBoardForm, LoginForm, NewThreadForm, NewPostForm
from .config import Config
from .sessions import Sessions

app = Flask(__name__)
db = Database()
config = Config()
sessions = Sessions()

new = True
allowed_extensions = ['png', 'jpg', 'jpeg', 'gif']

minify(app=app, html=True, js=True, cssless=True)

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    global new

    if new:
        form = SetupForm(request.form)
        if request.method == 'POST':
            if form.validate():
                db.create_db()
                db.new_admin(form.admin_username.data,
                        form.password.data)
                config.get()['site']['name'] = form.site_name.data
                config.write()

                flash('First setup accepted')
                new = False
                return redirect(url_for('admin_login'))
            else:
                flash('Setup not accepted')
        return render_template('setup.html', form=form)
    else:
        return redirect(url_for('index'))

@app.route('/new_board', methods=['GET', 'POST'])
def new_board():
    if not sessions.exists(session['id']):
        flash('Error')
        return redirect(url_for('index'))

    form = NewBoardForm(request.form)
    form.category.choices = db.get_categories_select()
    if request.method == 'POST':
        # Submitting form for new board
        if form.validate():
            if form.category.data == -1:
                if form.new_category.data.strip() == '':
                    flash('Need a name for the new category')
                    return render_template('new_board.html', form=form)
                else:
                    # Create category
                    cat_id = db.new_category(form.new_category.data)
            else:
                cat_id = int(form.category.data)

            # Create new board
            db.new_board(form.directory.data,
                    form.name.data,
                    form.description.data,
                    form.btype.data,
                    cat_id,
                    form.nswf.data)
            flash('New board created')
            return redirect(url_for('new_board'))
        else:
            flash('Board not accepted')
            return render_template('new_board.html', form=form)
    else:
        return render_template('new_board.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if sessions.exists(session['id']):
        return render_template('dashboard.html')
    else:
        flash('Error')
        return redirect(url_for('index'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'id' in session:
        if sessions.exists(session['id']):
            return redirect(url_for('dashboard'))

    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            if db.verify_user(form.username.data,
                    form.password.data):
                flash('Logged in')
                session['id'] = sessions.add(form.username.data)
                return redirect(url_for('dashboard'))
            else:
                flash('Error')
        else:
            flash('Error')

    return render_template('admin_login.html', form=form)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/board/<board_dir>/thread/<thread_id>/new_post', methods=['POST'])
def new_post(board_dir: str, thread_id: int):
    board_info = db.get_board(board_dir)
    if not board_info['exists']:
        flash('Board does not exists')
        return redirect(url_for('index'))

    form = NewPostForm()
    if form.validate_on_submit():
        filename = ''
        title = ''
        if form.image.data:
            # If an image was to upload
            image = form.image.data
            if image.filename == '' or not allowed_file(image.filename):
                flash('Error: Invalid file')
                return redirect(url_for('thread', board_dir=board_dir, thread_id=thread_id))
            else:
                filename = secure_filename(image.filename)

                # Save image and insert into database
                image.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], filename
                ))

        if form.title.data:
            title = form.title.data

        # Any valid form
        valid, error_msg = db.new_post(board_dir,
                thread_id,
                title,
                form.content.data,
                filename)

        if valid:
            flash('New post')
        else:
            flash('Error no new post: '+error_msg)
    else:
        flash('Error, new post not accepted')
    return redirect(url_for('thread', board_dir=board_dir, thread_id=thread_id))

@app.route('/board/<board_dir>/new_thread', methods=['POST'])
def new_thread(board_dir: str):
    board_info = db.get_board(board_dir)
    if not board_info['exists']:
        flash('Board does not exists')
        return redirect(url_for('index'))

    form = NewThreadForm()
    if form.validate_on_submit():
        print("Title:", form.title.data)
        print("Options:", form.options.data)
        print("Content:", form.content.data)
        image = form.image.data
        if image.filename == '':
            flash('No file selected')
        elif not image or not allowed_file(image.filename):
            flash('Invalid file')
        else:
            flash('New Thread Created')
            filename = secure_filename(image.filename)

            # Save image and insert into database
            image.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename
            ))
            db.new_thread(board_dir,
                    form.title.data,
                    form.content.data,
                    filename)
            print("Image:", filename)
    else:
        flash('Error, new thread not accepted')
    return redirect(url_for('board', board_dir=board_dir))

@app.route('/board/<board_dir>/thread/<thread_id>', methods=['GET'])
def thread(board_dir: str, thread_id: int):
    board_info = db.get_board(board_dir)
    if not board_info['exists']:
        flash('Board does not exists')
        return redirect(url_for('index'))

    thread_posts = db.get_thread_posts(board_dir, thread_id)
    new_post_form = NewPostForm()
    return render_template('thread.html',
            board_dir=board_dir,
            board_name=board_info['name'],
            board_desc=board_info['description'],
            boards_list=db.get_boards(),
            thread_id=thread_id,
            thread_posts=thread_posts,
            new_post_form=new_post_form)

@app.route('/board/<board_dir>/', methods=['GET'])
def board(board_dir: str):
    board_info = db.get_board(board_dir)
    if not board_info['exists']:
        flash('Board does not exists')
        return redirect(url_for('index'))

    new_thread_form = NewThreadForm()

    threads_list = db.get_threads(board_dir)

    return render_template('board.html',
            board_dir=board_dir,
            board_name=board_info['name'],
            board_desc=board_info['description'],
            new_thread_form=new_thread_form,
            threads_list=threads_list,
            boards_list=db.get_boards())

@app.route('/uploads/<filename>')
def uploads(filename: str):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    if new:
        return redirect(url_for('setup'))
    else:
        return render_template('homepage.html', categories=db.get_boards())

def main():
    global new, allowed_extensions
    app.config.update(
            TESTING = True,
            SECRET_KEY = b'(ID()AJ#$2ASJD',
            UPLOAD_FOLDER = os.path.abspath('uploads/'),
            MAX_CONTENT_LENGTH = 2 * 1024 * 1024    # 2 MiB
    )
    db.open('localhost', 'aaachan-db', 'postgres', 'aaachan')

    config.read()
    if config.get()['site']['name'] != '':
        new = False
    else:
        # Only for testing
        db.delete_db()

    app.run(debug=True, host='0.0.0.0')
    db.close()

if __name__ == "__main__":
    main()

