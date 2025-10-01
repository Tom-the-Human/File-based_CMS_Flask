from flask import Flask, render_template, send_from_directory
import os
import os.path

app = Flask(__name__)
root = os.path.abspath(os.path.dirname(__file__))

@app.route('/')
@app.route('/index')
def index():
    data = os.listdir(os.path.join(root, 'cms', 'data'))
    return render_template('index.html', data=data)

@app.route('/<file_name>')
def file_content(file_name):
    data_path = os.path.join(root, 'cms', 'data')
    return send_from_directory(data_path, file_name)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
