import sqlite3
import logging
import sys
import time
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

def logger_message(message):
    date = time.asctime()
    return f"{date}, {message}"


def get_db_connection():
    """
    Function to get a database connection.
    This function connects to database with the name `database.db`
    """
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global connection_count
    connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['connection_count'] = 0
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    app.logger.debug(logger_message('Debuging test message'))
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    response = app.response_class(
        response=json.dumps({"db_connection_count": connection_count, "post_count": len(posts)}),
        status=200,
        mimetype='application/json'
    )
    return response

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error("There are no articles! ")
        return render_template('404.html'), 404
    else:
        app.logger.info("Article \'%s' ")
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("About page successfully retrived")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


if __name__ == "__main__":
    """
    Starting the application on port 3111
    Recording the logs to both STDOUT & STDERR
    """
    logger = logging.getLogger('logfile')
    logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stderror_handler = logging.StreamHandler(stream=sys.stderr)
    stderror_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s __ %(name)s __ %(levelname)s __ %(message)s',datefmt='%d/%m/%Y')

    stdout_handler.setFormatter(formatter)
    stderror_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderror_handler)

    handlers = [stdout_handler, stderror_handler]

    logging.basicConfig(
        level=logging.DEBUG,
        filemode= 'w',
        format = '%(levelname)s __ %(asctime)s __ %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        handlers=handlers
    )
    app.run(host='0.0.0.0', port='3111')
