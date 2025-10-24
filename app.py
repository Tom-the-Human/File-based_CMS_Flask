from flask import (
    Flask, 
    render_template, 
    send_from_directory, 
    redirect, 
    url_for,
    flash,
    request,
    session,
)
from functools import wraps
from markdown import markdown
import bcrypt
import os
import re
import yaml

app = Flask(__name__)
app.secret_key = "secret"
app.session = session

def get_data_path():
    if app.config['TESTING']:
        return os.path.join(os.path.dirname(__file__), 'tests', 'data')
    else:
        return os.path.join(os.path.dirname(__file__), 'cms', 'data')

def valid_file_type(file_name):
    parts = file_name.split('.')
    valid_extensions = ['txt', 'md', '']

    if len(parts) is 1:
        parts.append('txt')
    elif len(parts) > 2:
        flash("Invalid file name: use no more than 1 dot with 1 extension")
        return False
    elif parts[1] not in valid_extensions:
        flash("Invalid file type: only .txt and .md are supported")
        return False
    
    return True
    
def valid_credentials(username, password):
    credentials = load_user_credentials()

    if username in credentials:
        stored_password = credentials[username].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_password)
    else:
        return False

def load_user_credentials():
    filename = 'users.yml'
    root_dir = os.path.dirname(__file__)
    if app.config['TESTING']:
        credentials_path = os.path.join(root_dir, 'tests', filename)
    else:
        credentials_path = os.path.join(root_dir, "cms", filename)

    with open(credentials_path, 'r') as file:
        return yaml.safe_load(file)

def user_signed_in():
    return 'username' in session

def require_signed_in_user(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if user_signed_in():
            return func(*args, **kwargs)
        else:
            flash("You must be signed in to do that.")
            return redirect(url_for('sign_in_form'))
    return decorated

def get_next_available_File_name(file_path):
    if not os.path.exists(file_path):
        return file_path

    directory, file_name = os.path.split(file_path)
    stem, extension = os.path.splitext(file_name)

    match = re.match(r'^(.*?)(\s*\(\d+\))?$', stem)
    base = match.group(1)

    counter = 1
    while True:
        new_stem = f"{base}({counter})"
        new_file_name = new_stem + extension
        new_file_path = os.path.join(directory, new_file_name)

        if not os.path.exists(new_file_path):
            return new_file_path

        counter += 1

@app.route('/')
@app.route('/index')
def index():
    data_path = get_data_path()
    files = os.listdir(data_path)
    return render_template('index.html', files=files)

@app.route('/<file_name>')
def file_content(file_name):
    # deviates from LS solution, but outcome seems the same
    data_path = get_data_path()
    file_path = f'{data_path}/{file_name}'

    if not os.path.isfile(file_path):
        flash(f'{file_name} does not exist.')
        return redirect(url_for('index'))
    elif file_name.endswith('.md'):
        with open(file_path, 'r') as f:
            content = markdown(f.read())
            return render_template('markdown.html', content=markdown(content))

    return send_from_directory(data_path, file_name)

@app.route('/<file_name>/edit', methods=['GET'])
@require_signed_in_user
def edit_file_content(file_name):
    data_path = get_data_path()
    file_path = f'{data_path}/{file_name}'

    if not os.path.isfile(file_path):
        flash(f'{file_name} does not exist.')
        return redirect(url_for('index'))
    else:
        with open(file_path, 'r') as f:
         content = f.read()

    return render_template('edit.html', file_name=file_name, content=content)

@app.route('/<file_name>', methods=['POST'])
@require_signed_in_user
def save_file(file_name):
    data_path = get_data_path()
    file_path = f'{data_path}/{file_name}'
    content = request.form['content']

    with open(file_path, 'w') as f:
        f.write(content)

    flash(f'{file_name} has been updated.')
    return redirect(url_for('index'))

@app.route('/new', methods=['GET'])
@require_signed_in_user
def new_document():
    return render_template('new.html')

@app.route('/create', methods=['POST'])
@require_signed_in_user
def create_file():
    file_name = request.form.get('file_name', '').strip()
    data_path = get_data_path()
    file_path = f'{data_path}/{file_name}'

    if not file_name:
        flash("A name is required.")
        return render_template('new.html'), 422
    elif os.path.exists(file_path):
        flash(f'{file_name} already exists.')
        return render_template('new.html'), 422
    elif not valid_file_type(file_name):
        return render_template('new.html'), 422
    
    with open(file_path, 'w') as f:
        f.write('')
        flash(f'{file_name} has been created.')
        return redirect(url_for('index'))

@app.route('/<file_name>/duplicate', methods=['POST'])
@require_signed_in_user
def duplicate_file(file_name):
    data_path = get_data_path()
    file_path = f'{data_path}/{file_name}'

    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read()

        with open(get_next_available_File_name(file_path), 'w') as f:
            f.write(content)
            flash(f'{file_name} has been duplicated.')
            return redirect(url_for('index'))

@app.route('/<file_name>/delete', methods=['POST'])
@require_signed_in_user
def delete_file(file_name):
    data_path = get_data_path()
    file_path = f'{data_path}/{file_name}'

    if os.path.isfile(file_path):
        os.remove(file_path)
        flash(f"{file_name} has been deleted.")
    else:
        flash(f"{file_name} does not exist.")

    return redirect(url_for('index'))

@app.route('/users/signin', methods=['GET'])
def sign_in_form():
    return render_template('sign_in.html')

@app.route('/users/signin', methods=['POST'])
def validate_sign_in():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if valid_credentials(username, password):
        session['username'] = username
        flash('Sign in successful. Welcome!')
        return redirect(url_for('index'))
    else:
        flash("Invalid credentials")
        return render_template('sign_in.html'), 422

@app.route('/users/signout', methods=['POST'])
def sign_out():
    session.pop('username', None)
    flash("You have been signed out.")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=8080)
