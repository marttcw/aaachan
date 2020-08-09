from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_minify import minify

from .database import Database
from .forms import SetupForm, NewBoardForm, LoginForm
from .config import Config
from .sessions import Sessions

app = Flask(__name__)
db = Database()
config = Config()
sessions = Sessions()

new = True

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
    if request.method == 'POST':
        # Submitting form for new board
        if form.validate():
            # Create new board
            db.new_board(form.directory.data,
                    form.name.data,
                    form.description.data,
                    form.btype.data)
            flash('New board created')
            return render_template('new_board.html', form=NewBoardForm())
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

@app.route('/board/<board_dir>/post', methods=['POST'])
def post(board_dir: str):
    return redirect(url_for('index'))

@app.route('/board/<board_dir>/', methods=['GET'])
def board(board_dir: str):
    board_info = db.get_board(board_dir)
    if not board_info['exists']:
        flash('Board does not exists')
        return redirect(url_for('index'))

    return render_template('board.html',
            board_dir=board_dir,
            board_name=board_info['name'],
            board_desc=board_info['description'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if new:
        return redirect(url_for('setup'))
    else:
        return render_template('homepage.html', boards=db.get_boards())

def main():
    global new
    app.config.update(
            TESTING = True,
            SECRET_KEY = b'(ID()AJ#$2ASJD'
    )
    db.open('localhost', 'zzzchan-db', 'postgres', 'zzzchan')

    config.read()
    #db.delete_db()
    if config.get()['site']['name'] != '':
        new = False

    app.run(debug=True)
    db.close()

if __name__ == "__main__":
    main()

