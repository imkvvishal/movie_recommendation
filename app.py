# ...existing code...
# Place these route functions after app = Flask(__name__) and all imports
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from db_connect import create_database_and_table, insert_user, create_registration_table
from db_config import get_db_config
import logging
from flask_mysqldb import MySQL
import mysql.connector
import movie_file
from wishlist import add_to_wishlist, remove_from_wishlist, is_in_wishlist

app = Flask(__name__)
app.secret_key = "Secret_Key" 
@app.route('/myprofile', methods=['GET', 'POST'])
def myprofile():
    user_id = session.get('user_id')
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        phonenumber = request.form.get('phonenumber')
        try:
            cursor.execute('UPDATE users SET name=%s, age=%s, phonenumber=%s WHERE id=%s', (name, age, phonenumber, user_id))
            connection.commit()
            flash('Profile updated successfully!')
        except Exception as e:
            flash(f'Error updating profile: {e}')
    cursor.execute('SELECT name, age, phonenumber, email FROM users WHERE id=%s', (user_id,))
    user = cursor.fetchone()

    # Fetch history for this user (by name)
    user_name = user['name'] if user else None
    history = []
    if user_name:
        try:
            history_cursor = connection.cursor(dictionary=True)
            history_cursor.execute('SELECT movie_name FROM history WHERE name=%s', (user_name,))
            history = history_cursor.fetchall()
            history_cursor.close()
        except Exception as e:
            print(f"Error fetching history: {e}")

    cursor.close()
    connection.close()
    return render_template('myprofile.html', user=user, history=history)

@app.route('/settings', methods=['GET', 'POST'])

def settings():
    user_id = session.get('user_id')
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    if request.method == 'POST':
        # Notification preference
        notifications = 1 if request.form.get('notifications') else 0
        cursor.execute('UPDATE users SET notifications=%s WHERE id=%s', (notifications, user_id))
        # Password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        if current_password and new_password and new_password == confirm_new_password:
            cursor.execute('SELECT password FROM users WHERE id=%s', (user_id,))
            user = cursor.fetchone()
            if user and check_password_hash(user['password'], current_password):
                hashed_new = generate_password_hash(new_password)
                cursor.execute('UPDATE users SET password=%s WHERE id=%s', (hashed_new, user_id))
                flash('Password changed successfully!')
            else:
                flash('Current password is incorrect.')
        elif new_password or confirm_new_password:
            flash('Passwords do not match.')
            connection.commit()
    cursor.execute('SELECT notifications FROM users WHERE id=%s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('settings.html', user=user)




# Change this to a random secret key

# Configure logging to capture errors
logging.basicConfig(level=logging.DEBUG)

# Initialize the database when the app starts
# try:
#     create_database_and_table()
#     print("Database initialized successfully on app startup.")
# except Exception as e:
#     print(f"Database initialization failed on startup: {e}. You can initialize manually at /init_db")

# Temporarily disable MySQL connection logic to ensure Flask starts successfully
try:
    # Ensure the registration table exists on app startup
    create_registration_table()
except Exception as e:
    print(f"Error ensuring registration table exists: {e}")

# Function to get SQLite database connection (for movies)
def get_db_connection():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    return conn
# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Function to get user by email from MySQL
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            connection = get_mysql_connection()
            if connection is None:
                flash("Database connection failed. Please try again later.")
                return redirect(url_for('login'))

            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            print(f"User record from DB: {user}")
            if user:
                print(f"Password in DB: {user['password']}")
                print(f"Password entered: {password}")
                if check_password_hash(user['password'], password):
                    print("Password check: SUCCESS")
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    return redirect(url_for('home'))
                else:
                    print("Password check: FAIL")
            flash('Invalid email or password.')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error during login: {e}")
            flash("An error occurred. Please try again later.")
            return redirect(url_for('login'))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
    return render_template('login.html')

# Sign Up page
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        phonenumber = request.form.get('phonenumber')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        # Validate required fields
        if not all([name, age, phonenumber, email, password]):
            flash("All fields are required.")
            return redirect(url_for('signup'))

        # Convert age to int and handle error
        try:
            age = int(age)
        except ValueError:
            flash("Age must be a number.")
            return redirect(url_for('signup'))

        try:
            connection = get_mysql_connection()
            if connection is None:
                flash("Database connection failed. Please try again later.")
                return redirect(url_for('signup'))

            cursor = connection.cursor()
            insert_query = """
            INSERT INTO users (name, age, phonenumber, email, password)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (name, age, phonenumber, email, hashed_password))
            connection.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash("Email already exists. Please use a different email.")
            return redirect(url_for('signup'))
        except Exception as e:
            error_message = f"Error during registration: {e}"
            print(error_message)
            flash(error_message)
            return redirect(url_for('signup'))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
    return render_template("signup.html")

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Admin page to view registered users
@app.route('/admin/users')
@login_required
def admin_users():
    return "MySQL connection is disabled. Admin functionality is not available.", 503

# Function to get MySQL database connection
def get_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host='LOCAL_HOST',  # Replace with your MySQL host
            user='USER_NAME',  # Replace with your MySQL username
            password='PASS-WORD',  # Replace with your MySQL password
            database='film_frame'  # Replace with your MySQL database name
        )
        if connection.is_connected():
            print("MySQL connection successful")
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None



@app.route('/')
def home():
    movies = movie_file.load_movies()
    trending_movies = sorted(movies, key=lambda m: m.get('rating', 0), reverse=True)[:8]
    return render_template('home.html', trending_movies=trending_movies)

@app.route('/movies')
@login_required
def movies():
    movies = movie_file.load_movies()
    return render_template('movies.html', movies=movies)

@app.route('/recommendations')
@login_required
def recommendations():
    genre = request.args.get('genre', '')
    mood = request.args.get('mood', '')
    movies = movie_file.load_movies()
    # Collect all moods from movies
    all_moods = set()
    for m in movies:
        if isinstance(m.get('mood'), list):
            all_moods.update(m['mood'])
        elif m.get('mood'):
            all_moods.add(m['mood'])
    moods = sorted(all_moods)
    filtered = movies
    if genre:
        filtered = [m for m in filtered if genre.lower() in m.get('genre', '').lower()]
    if mood:
        filtered = [m for m in filtered if mood.lower() in [md.lower() for md in (m.get('mood', []) if isinstance(m.get('mood'), list) else [m.get('mood', '')])]]
    else:
        filtered = [] if genre == '' and mood == '' else filtered
    return render_template('recommendations.html', movies=filtered, genre=genre, mood=mood, moods=moods)

@app.route('/search')
@login_required
def search():
    query = request.args.get('query', '')
    genre = request.args.get('genre', '')
    language = request.args.get('language', '')
    type_ = request.args.get('type', '')
    movies = movie_file.load_movies()
    filtered = movies
    if query:
        filtered = [m for m in filtered if query.lower() in m.get('name', '').lower()]
    if genre:
        filtered = [m for m in filtered if genre.lower() in m.get('genre', '').lower()]
    if language:
        filtered = [m for m in filtered if language.lower() in m.get('language', '').lower()]
    if type_:
        filtered = [m for m in filtered if type_.lower() in m.get('type', '').lower()]
    # For filter dropdowns, get unique values
    genres = sorted(set(m.get('genre', '') for m in movies if m.get('genre')))
    languages = sorted(set(m.get('language', '') for m in movies if m.get('language')))
    types = sorted(set(m.get('type', 'Movie') for m in movies))
    return render_template('search.html', movies=filtered, query=query, genre=genre, language=language, type_=type_, genres=genres, languages=languages, types=types)

@app.route('/movie/<int:index>')
@login_required
def movie_detail(index):
    movies = movie_file.load_movies()
    if 0 <= index < len(movies):
        movie = movies[index]
        in_wishlist = is_in_wishlist(index)
        # Insert into history table (store user name and movie name)
        try:
            connection = get_mysql_connection()
            if connection is not None:
                cursor = connection.cursor()
                from datetime import datetime
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                user_name = session.get('user_name')
                movie_name = movie.get('name', '')
                cursor.execute(
                    'INSERT INTO history (name, movie_name) VALUES (%s, %s)',
                    (user_name, movie_name)
                )
                connection.commit()
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"Error inserting into history: {e}")
        return render_template('movie_detail.html', movie=movie, index=index, in_wishlist=in_wishlist)
    else:
        return "Movie not found", 404

@app.route('/wishlist/add/<int:index>', methods=['POST'])
@login_required
def add_wishlist(index):
    add_to_wishlist(index)
    return ('', 204)

@app.route('/wishlist/remove/<int:index>', methods=['POST'])
@login_required
def remove_wishlist(index):
    remove_from_wishlist(index)
    return ('', 204)

if __name__ == "__main__":
    app.run(debug=True)
