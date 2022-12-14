"""Imports"""
import datetime
import logging
import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

db_connection_count=0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Get the total amount of connections to the database. For example, accessing an article will query the database, hence will count as a connection. 
def count_db_connections(): 
    global db_connection_count
    db_connection_count=db_connection_count+1
    return db_connection_count

# Total amount of posts in the database
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Get the total number of posts
def number_of_posts(): 
    global total_posts
    connection = get_db_connection()
    total_posts = connection.execute('SELECT count(*) FROM posts').fetchone()
    connection.close()
    """Convert total post to JSON serializable""" 
    print(total_posts[0])
    return total_posts

# Get also date/time in format Y/M/D/, H:M:S apart from datefmt='%Y-%m-%d %H:%M:%S'
# e.g. INFO:app 10/10/2022, 10:28:39, Status request successfull
def time():
    global timestamp
    now = datetime.datetime.now()
    timestamp = str(now.strftime("%d/%m/%Y, %H:%M:%S, "))
    return timestamp

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/healthz')
def healthz():
    """Get Health""" 
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    ## log line
    """Log message for a non-existing article"""
    time()
    app.logger.info(timestamp + '"Healthz" request successfull')
    app.logger.debug('Healthz debug message')
    return response  

@app.route('/metrics')
def metrics():
    global total_posts
    number_of_posts()
    response = app.response_class(
            response=json.dumps({"db_connection_count": db_connection_count , "posts_count": total_posts[0]}),
            status=200,
            mimetype='application/json'
    )
    time()
    app.logger.info(timestamp + '"Metrics" request successfull')
    app.logger.debug('Metrics debug message')
    return response 

    
# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    time()
    app.logger.info(timestamp + '"Main Page" request successfull')
    app.logger.debug('Main Page debug message')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    time()
    if post is None:
      """Log message for a non-existing article"""
      app.logger.error(timestamp + 'Non-existing Article!')
      return render_template('404.html'), 404
    else:
      """Log message for a non-existing article"""
      app.logger.info(timestamp + 'Article "' + post[2] + '" retrieved!')
      app.logger.debug('Atricle retrieval debug message')
      """call function to get total ammount of db connections"""
      count_db_connections()
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    time()
    app.logger.info(timestamp + '"About Us" page retrieved!')
    app.logger.debug('"About Us" page retrieval debug message')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    time()
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
            app.logger.info(timestamp + 'The Article Post with title "' + str(title) + ' " was successfully created')
            app.logger.debug('Atricle creation debug message')
            """call function to get total ammount of db connections"""
            count_db_connections()
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":

   # Log to STDOUT with the format e.g. INFO:werkzeug:127.0.0.1 - - [08/Jan/2021 22:40:06] "GET /metrics HTTP/1.1" 200 -
   logging.basicConfig(format='%(levelname)s:%(name)s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')
   logging.basicConfig(format='%(levelname)s:%(name)s %(message)s',level=logging.DEBUG,datefmt='%Y-%m-%d %H:%M:%S')
   logging.basicConfig(format='%(levelname)s:%(name)s %(message)s',level=logging.ERROR,datefmt='%Y-%m-%d %H:%M:%S')
   
   app.run(host='0.0.0.0', port='3111')
   