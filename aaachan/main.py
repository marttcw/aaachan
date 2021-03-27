from aaachan import app

from flask import Flask, render_template, request, flash, redirect, url_for, session, send_from_directory, abort
from flask_minify import minify
from werkzeug.utils import secure_filename

import os, atexit, sys

from .database import Database
from .forms import SetupForm, NewBoardForm, LoginForm, NewThreadForm, NewPostForm, EditBoardForm, ReportForm, NewModForm
from .config import Config
from .sessions import Sessions
from .thumbnail import Thumbnail
from .processing import Processing
from .ip_sessions import IpSessions

db = Database()
config = Config()
sessions = Sessions()
thumbnail = Thumbnail()
ip_sessions = IpSessions()

new = True

minify(app=app, html=True, js=True, cssless=True)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(413)
def file_too_large(error):
    return render_template('413.html'), 413

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
    if 'id' not in session or not sessions.exists(session['id']):
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
                    form.nsfw.data,
                    form.files_types.data,
                    form.files_limit.data)
            flash('New board created')
            return redirect(url_for('new_board'))
        else:
            flash('Board not accepted')
            return render_template('new_board.html', form=form)
    else:
        return render_template('new_board.html', form=form)

@app.route('/edit_board/<board_dir>/', methods=['GET', 'POST'])
def edit_board(board_dir: str):
    if 'id' not in session or not sessions.exists(session['id']):
        flash('Error')
        return redirect(url_for('index'))

    form = EditBoardForm(request.form)
    form.category.choices = db.get_categories_select()
    if request.method == 'POST':
        # Submitting form for new board
        if form.validate():
            if form.category.data == -1:
                if form.new_category.data.strip() == '':
                    flash('Need a name for the new category')
                    return render_template('edit_board.html', form=form)
                else:
                    # Create category
                    cat_id = db.new_category(form.new_category.data)
            else:
                cat_id = int(form.category.data)

            # Edit board
            db.edit_board(board_dir,
                    form.name.data,
                    form.description.data,
                    form.btype.data,
                    cat_id,
                    form.nsfw.data,
                    form.files_types.data,
                    form.files_limit.data)
            flash('Board updated')
        else:
            flash('Board edit not accepted')
    else:
        board_info = db.get_board(board_dir)
        if board_info['exists']:
            # Fill in the data required to edit
            form.name.data = board_info['name']
            form.description.data = board_info['description']
            form.btype.data = board_info['type']
            form.nsfw.data = board_info['nsfw']
            form.category.data = board_info['category_id']
            form.files_types.data = board_info['files_types']
            form.files_limit.data = board_info['files_limit']
        else:
            flash('Board does not exists')
            return redirect(url_for('dashboard'))
    return render_template('edit_board.html',
            form=form,
            board_dir=board_dir)

@app.route('/edit_board', methods=['GET'])
def edit_board_overview():
    if 'id' in session and sessions.exists(session['id']):
        return render_template('edit_board_overview.html',
                categories=db.get_boards())
    else:
        flash('Error')
        return redirect(url_for('index'))

@app.route('/config_write')
def config_write():
    if 'id' in session and sessions.exists(session['id']):
        config.write()
        flash('Overwritten config file')
        return redirect(url_for('dashboard'))
    else:
        flash('Error')
        return redirect(url_for('index'))

@app.route('/create_mod', methods=['GET', 'POST'])
def create_mod():
    if 'id' in session and sessions.exists(session['id']):
        form = NewModForm(request.form)

        if request.method == 'POST':
            if form.validate():
                db.new_mod(form.username.data,
                        form.password.data)
                flash('New user "'+str(form.username.data)+'" created')
                return render_template('create_mod.html',
                        form=NewModForm())
            else:
                flash('Invalid form')

        return render_template('create_mod.html',
                form=form)
    else:
        flash('Error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'id' in session and sessions.exists(session['id']):
        return render_template('dashboard.html',
                utype=sessions.type(session['id']))
    else:
        flash('Error')
        return redirect(url_for('index'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'id' in session and sessions.exists(session['id']):
        return redirect(url_for('dashboard'))

    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            verified, utype = db.verify_user(form.username.data,
                    form.password.data)
            if verified:
                flash('Logged in')
                session['id'] = sessions.add(form.username.data, utype)
                return redirect(url_for('dashboard'))
            else:
                flash('Error')
        else:
            flash('Error')

    return render_template('admin_login.html', form=form)

@app.route('/logout')
def logout():
    if 'id' in session and sessions.exists(session['id']):
        sessions.remove(session['id'])
        session.pop('id', None)
        flash('Logged out')
    else:
        flash('Error')
    return redirect(url_for('index'))
    

def allowed_file(filename: str, allowed_extensions_str: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions_str.split(' ')

@app.route('/board/<board_dir>/thread/<thread_id>/new_post', methods=['POST'])
def new_post(board_dir: str, thread_id: int):
    board_info = db.get_board(board_dir)
    if not board_info['exists']:
        flash('Board does not exists')
        return redirect(url_for('index'))

    remote_ip_address = request.environ['REMOTE_ADDR']

    form = NewPostForm()
    if form.validate_on_submit():
        if form.name.data != '' or form.message.data != '':
            # Honeypot filled, redirect to main page with no comment
            return redirect(url_for('index'))
        if not ip_sessions.allow_post(remote_ip_address):
            flash('Error, you must wait '+\
                    ip_sessions.time_length_post(remote_ip_address)+\
                    ' till you can post')
            return redirect(url_for('thread', board_dir=board_dir, thread_id=thread_id))
        if not Processing().allowed_content(form.content.data):
            flash('Error, disallowed content')
            return redirect(url_for('thread', board_dir=board_dir, thread_id=thread_id))
        if len(form.files.data) > board_info['files_limit']:
            flash('Error: Too much files, limit: '+str(board_info['files_limit']))
            return redirect(url_for('thread', board_dir=board_dir, thread_id=thread_id))

        title = ''
        invalid_files = False
        files_list = []

        for fi in form.files.data:
            if allowed_file(fi.filename, board_info['files_types']):
                files_list.append(fi)
            elif fi.filename == '':
                break
            else:
                flash('Invalid file: '+fi.filename)
                invalid_files = True

        if not invalid_files:
            fdb_list = []
            prefix_num: int = 0

            for fi in files_list:
                filename = secure_filename(fi.filename)
                storepath = str(prefix_num) + '_' + Thumbnail().store_name(fi.filename)

                # Save image and insert into database
                fullstorepath = os.path.join(
                    app.config['UPLOAD_FOLDER'], storepath
                )
                fi.save(fullstorepath)

                # Generate and save thumbnail
                thumbpath, has_thumb, alt_thumb = thumbnail.generate(fullstorepath)

                if not has_thumb:
                    thumbpath = alt_thumb
                if thumbpath == '':
                    thumbpath = None

                fdb_list.append({
                    'filepath': filename,
                    'storepath': storepath,
                    'thumbpath': thumbpath
                })

                prefix_num += 1

            if form.title.data:
                title = form.title.data

            # Any valid form
            valid, error_msg = db.new_post(board_dir,
                    thread_id,
                    title,
                    form.content.data,
                    remote_ip_address,
                    fdb_list)

            if valid:
                ip_sessions.start_post_limit(remote_ip_address)
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

    remote_ip_address = request.environ['REMOTE_ADDR']

    form = NewThreadForm()
    if form.validate_on_submit():
        if form.name.data != '' or form.message.data != '':
            # Honeypot filled, redirect to main page with no comment
            return redirect(url_for('index'))
        if not ip_sessions.allow_thread(remote_ip_address):
            flash('Error, you must wait '+\
                    ip_sessions.time_length_thread(remote_ip_address)+\
                    ' till you can make a new thread')
            return redirect(url_for('board', board_dir=board_dir))
        if not Processing().allowed_content(form.content.data):
            flash('Error, disallowed content')
            return redirect(url_for('board', board_dir=board_dir))
        if len(form.files.data) > board_info['files_limit']:
            flash('Error: Too much files, limit: '+str(board_info['files_limit']))
            return redirect(url_for('board', board_dir=board_dir))

        invalid_files = False
        files_list = []

        for fi in form.files.data:
            if allowed_file(fi.filename, board_info['files_types']):
                files_list.append(fi)
            else:
                flash('Invalid file: '+fi.filename)
                invalid_files = True

        if files_list == []:
            flash('No file selected')
            invalid_files = True

        if not invalid_files:
            fdb_list = []
            prefix_num: int = 0

            for fi in files_list:
                filename = secure_filename(fi.filename)
                storepath = str(prefix_num) + '_' + Thumbnail().store_name(fi.filename)

                # Save image and insert into database
                fullstorepath = os.path.join(
                    app.config['UPLOAD_FOLDER'], storepath
                )
                fi.save(fullstorepath)

                # Generate and save thumbnail
                thumbpath, has_thumb, alt_thumb = thumbnail.generate(fullstorepath)

                if not has_thumb:
                    thumbpath = alt_thumb
                if thumbpath == '':
                    thumbpath = None

                fdb_list.append({
                    'filepath': filename,
                    'storepath': storepath,
                    'thumbpath': thumbpath
                })

                prefix_num += 1

            valid, error_msg = db.new_thread(board_dir,
                    form.title.data,
                    form.content.data,
                    remote_ip_address,
                    fdb_list)

            if valid:
                ip_sessions.start_thread_limit(remote_ip_address)
                flash('New Thread Created')
            else:
                flash('Error: '+error_msg)
    else:
        flash('Error, new thread not accepted')
    return redirect(url_for('board', board_dir=board_dir))

@app.route('/board/<board_dir>/thread/<thread_id>', methods=['GET'])
def thread(board_dir: str, thread_id: int):
    board_info = db.get_board(board_dir)
    if not board_info['exists']:
        flash('Board does not exists')
        return redirect(url_for('index'))

    # Posts in the thread
    thread_posts = db.get_thread_posts(board_dir, thread_id)
    post_map = {}
    quote_links = []
    for post in thread_posts:
        post['content'], quote_list = Processing().text_to_html(post['content'], post['id'])
        quote_links += quote_list
        post['quotes'] = set()
        post_map[str(post['id'])] = post

    # Link up quoting
    for link in quote_links:
        post_map[str(link['target'])]['quotes'].add(link['by'])

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
    for thread in threads_list:
        thread['content'], _ = Processing().text_to_html(thread['content'], thread['id'])

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

@app.route('/report/<board_dir>/<thread_id>/<post_id>/', methods=['GET', 'POST'])
def report_form(board_dir: str, thread_id: int, post_id: int):
    form = ReportForm(request.form)

    if request.method == "POST":
        if form.validate():
            sent, reason = db.new_report(board_dir,
                    thread_id,
                    post_id,
                    form.reason.data)

            if sent:
                flash('Report sent')
                return redirect(url_for('board', board_dir=board_dir))
            else:
                flash('Report not sent: '+reason)
        else:
            flash('Invalid form')
    return render_template('report.html',
            form=form,
            board_dir=board_dir,
            post_id=post_id)

@app.route('/reports_list/', methods=['GET', 'POST'])
def reports_list():
    if 'id' in session and sessions.exists(session['id']):
        return render_template('reports_list.html',
                reports_list=db.get_reports())
    else:
        abort(403)

@app.route('/', methods=['GET', 'POST'])
def index():
    if new:
        return redirect(url_for('setup'))
    else:
        return render_template('homepage.html',
                categories=db.get_boards(),
                site_name=config.get()['site']['name'])

@app.context_processor
def inject_global_vars():
    return dict(
            site_name = config.get()['site']['name']
    )

def close():
    db.close()

@app.before_first_request
def setup():
    global new, allowed_extensions
    app.config.update(
            TESTING = True,
            SECRET_KEY = b'(ID()AJ#$2ASJD',
            UPLOAD_FOLDER = os.path.abspath('uploads/'),
            MAX_CONTENT_LENGTH = 2 * 1024 * 1024    # 2 MiB
    )

    config.read()

    db_set = config.get()['database']

    opened = db.open(db_set['host'],
            db_set['name'],
            db_set['user'],
            db_set['pass'])

    if not opened:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with werkzeug server')
        func()

    if config.get()['site']['name'] != '':
        new = False
    else:
        # Only for testing
        db.delete_db()

    atexit.register(close)

def main():
    app.run(debug=True, host='0.0.0.0')

