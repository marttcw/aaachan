from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_minify import minify
from .database import Database
from .forms import SetupForm, NewBoardForm, LoginForm
from .config import Config

app = Flask(__name__)
db = Database()
config = Config()

new = True

minify(app=app, html=True, js=True, cssless=True)

@app.route('/setup', methods=['GET', 'POST'])
def setup():
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
                return redirect(url_for('dashboard'))
            else:
                flash('Setup not accepted')
        return render_template('setup.html', form=form)
    else:
        return redirect(url_for('index'))

@app.route('/new_board', methods=['GET', 'POST'])
def new_board():
    form = NewBoardForm(request.form)
    if request.method == 'POST':
        # Submitting form for new board
        if form.validate():
            # Create new board
            db.new_board(form.directory.data,
                    form.name.data,
                    form.description.data)
            flash('New board created')
            return render_template('new_board.html', form=NewBoardForm())
        else:
            flash('Board not accepted')
            return render_template('new_board.html', form=form)
    else:
        return render_template('new_board.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            if db.verify_user(form.username.data,
                    form.password.data):
                flash('Passed')
                #TODO: Sessions manager
                #session['id'] = 
            else:
                flash('Error')
        else:
            flash('Error')

    return render_template('admin_login.html', form=form)

@app.route('/board/<board_dir>', methods=['GET'])
def board():
    return render_template('board.html', bdir=board_dir, bname=name)

@app.route('/', methods=['GET', 'POST'])
def index():
    print("new:", new)
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
    db.delete_db()
    #if config.get()['site']['name'] != '':
    #    new = False

    app.run(debug=True)
    db.close()

if __name__ == "__main__":
    main()

