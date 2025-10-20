from flask import (
    Flask, 
    render_template, 
    send_from_directory, 
    redirect, 
    url_for,
    flash,
    request
)
from markdown import markdown
import os

app = Flask(__name__)
app.secret_key = "secret1"

def get_data_path():
    if app.config['TESTING']:
        return os.path.join(os.path.dirname(__file__), 'tests', 'data')
    else:
        return os.path.join(os.path.dirname(__file__), 'cms', 'data')


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
def save_file(file_name):
    data_path = get_data_path()
    file_path = f'{data_path}/{file_name}'
    content = request.form['content']

    with open(file_path, 'w') as f:
        f.write(content)

    flash(f'{file_name} has been updated.')
    return redirect(url_for('index'))

@app.route('/new', methods=['GET'])
def new_document():
    return render_template('new.html')

@app.route('/create', methods=['POST'])
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
    
    with open(file_path, 'w') as f:
        f.write('')
        flash(f'{file_name} has been created.')
        return redirect(url_for('index'))
    
@app.route('/<file_name>/delete', methods=['POST'])
def delete_file(file_name):
    data_path = get_data_path()
    file_path = f'{data_path}/{file_name}'

    if os.path.isfile(file_path):
        os.remove(file_path)
        flash(f"{file_name} has been deleted.")
    else:
        flash(f"{file_name} does not exist.")

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=8080)
