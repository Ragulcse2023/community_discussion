from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt  # For password hashing

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Configure MySQL
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '1234578'
app.config['MYSQL_DB'] = 'community_discussion'

mysql = MySQL(app)


# Register and Login
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        name = request.form['name']
        session['name']=name
        username = request.form['username']
        password = sha256_crypt.encrypt(request.form['password'])  # Hash the password

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, username, password) VALUES (%s, %s, %s)", (name, username, password))
        mysql.connection.commit()
        cur.close()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data[2]

            if sha256_crypt.verify(password_candidate, password):
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Discussion
@app.route('/')
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM discussions")
    discussions = cur.fetchall()
    cur.execute("select * from users")
    users = cur.fetchone()
    cur.close()
    print(discussions)
    print(users)
    return render_template('dashboard.html', discussions=discussions,users=users)
@app.route('/add_discussion', methods=['GET', 'POST'])
def add_discussion():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO discussions (title, content) VALUES (%s, %s)", (title, content))
        mysql.connection.commit()
        cur.close()
        flash('Discussion created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_discussion.html')
@app.route('/logout')
def logout():
    if 'name' in session:
        session.clear()
        return render_template('login.html')
    else:
        return "Unauthorized access. Please log Out first."


if __name__ == '__main__':
    app.run(debug=True)
