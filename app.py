from flask import (
    Flask, 
    render_template, 
    send_from_directory, 
    redirect, 
    url_for,
    flash
)
from markdown import markdown
import os

app = Flask(__name__)
app.secret_key = "secret1"
root = os.path.abspath(os.path.dirname(__file__))

@app.route('/')
@app.route('/index')
def index():
    data = os.listdir(os.path.join(root, 'cms', 'data'))
    return render_template('index.html', data=data)

@app.route('/<file_name>')
def file_content(file_name):
    # deviates from LS solution, but outcome seems the same
    data_path = os.path.join(root, 'cms', 'data')
    data = os.listdir(data_path)

    if file_name not in data:
        flash(f'{file_name} does not exist.')
        return redirect(url_for('index'))
    elif file_name.endswith('.md'):
        with open(f'{data_path}/{file_name}', 'r') as f:
            html = markdown(f.read())
            return html

    return send_from_directory(data_path, file_name)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
