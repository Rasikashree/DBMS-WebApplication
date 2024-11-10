from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rasi'
app.config['MYSQL_DB'] = 'movie_management_db'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
        existing_user = cur.fetchone()
        
        if existing_user:
            flash('Email is already taken. Please choose a different one.', 'error')
        else:
            cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)", 
                        (username, email, password, 'admin'))
            mysql.connection.commit()
            flash('Registration successful, please login.', 'success')
            return redirect(url_for('login'))
        cur.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user[3], password):
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            return redirect(url_for('admin'))
        
        flash('Incorrect email or password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if 'loggedin' in session and session['role'] == 'admin':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM movies")
        movies = cur.fetchall()
        cur.close()
        return render_template('admin.html', movies=movies)
    return redirect(url_for('login'))

@app.route('/admin/movie/new', methods=['GET', 'POST'])
def create_movie():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        release_year = request.form['release_year']
        genre = request.form['genre']
        rating = request.form['rating']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO movies (title, description, release_year, genre, rating) VALUES (%s, %s, %s, %s, %s)", 
                    (title, description, release_year, genre, rating))
        mysql.connection.commit()
        cur.close()
        flash('Movie added successfully.', 'success')
        return redirect(url_for('admin'))
    return render_template('movie_form.html')

@app.route('/admin/movie/edit/<int:id>', methods=['GET', 'POST'])
def edit_movie(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM movies WHERE id = %s", [id])
    movie = cur.fetchone()
    cur.close()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        release_year = request.form['release_year']
        genre = request.form['genre']
        rating = request.form['rating']
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE movies SET title = %s, description = %s, release_year = %s, genre = %s, rating = %s WHERE id = %s", 
                    (title, description, release_year, genre, rating, id))
        mysql.connection.commit()
        cur.close()
        flash('Movie updated successfully.', 'success')
        return redirect(url_for('admin'))
    
    return render_template('movie_form.html', movie=movie)

@app.route('/admin/movie/delete/<int:id>', methods=['POST'])
def delete_movie(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM movies WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()
    flash('Movie deleted successfully.', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)