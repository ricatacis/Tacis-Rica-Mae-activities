from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '123456789'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                          (username, email, password))
            conn.commit()
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username or email already exists!', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password_input):
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
        cursor.close()
        conn.close()

    return render_template('login.html')

# Combined dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get students data
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', 
                         username=session['username'], 
                         students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        course = request.form['course']
        year_level = request.form['year_level']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO students (student_id, first_name, last_name, email, course, year_level) VALUES (%s, %s, %s, %s, %s, %s)",
                (student_id, first_name, last_name, email, course, year_level)
            )
            conn.commit()
            flash('Student added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding student: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        course = request.form['course']
        year_level = request.form['year_level']
        
        try:
            cursor.execute(
                "UPDATE students SET first_name = %s, last_name = %s, email = %s, course = %s, year_level = %s WHERE student_id = %s",
                (first_name, last_name, email, course, year_level, student_id)
            )
            conn.commit()
            flash('Student updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating student: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()
            return redirect(url_for('dashboard'))
    else:
        try:
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
            student = cursor.fetchone()
            if not student:
                flash('Student not found', 'danger')
                return redirect(url_for('dashboard'))
            return render_template('edit_student.html', student=student)
        finally:
            cursor.close()
            conn.close()

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('dashboard'))




@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)