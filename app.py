from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os
import base64

app = Flask(__name__)
app.secret_key = "your_secret_key"

# --- CockroachDB Connection ---
DB_URL = "postgresql://karan:Uwq7W2xtJJEwvb7t15QxRQ@wiser-hound-16720.j77.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert=root.crt"

def get_db_connection():
    return psycopg2.connect(DB_URL)

# --- LOGIN PAGE ---
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        session['user_email'] = email
        return redirect(url_for('details_form'))
    else:
        return "❌ Invalid login credentials"

# --- DETAILS FORM ---
@app.route('/details')
def details_form():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('detailsForm.html')

@app.route('/submit_details', methods=['POST'])
def submit_details():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    address = request.form['address']
    image = request.files['image']
    image_data = image.read()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_details (email, name, age, gender, address, image)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (session['user_email'], name, age, gender, address, psycopg2.Binary(image_data)))

    conn.commit()
    cur.close()
    conn.close()

    # ✅ Redirect to all_details page instead of show_details
    return redirect(url_for('all_details'))

# --- SHOW LAST ENTERED DETAILS ---
@app.route('/show_details')
def show_details():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT name, age, gender, address, image
        FROM user_details
        WHERE email = %s
        ORDER BY id DESC LIMIT 1
    """, (session['user_email'],))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:
        name, age, gender, address, image_data = result
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        return render_template('showDetails.html', name=name, age=age, gender=gender, address=address, image=image_base64)
    else:
        return "❌ No details found."

# --- SHOW ALL USERS DETAILS ---
@app.route('/all_details')
def all_details():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, age, gender, address, image FROM user_details ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Convert images to base64
    all_users = []
    for row in rows:
        name, age, gender, address, image_data = row
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        all_users.append({
            'name': name,
            'age': age,
            'gender': gender,
            'address': address,
            'image': image_base64
        })

    return render_template('allDetails.html', users=all_users)

if __name__ == '__main__':
    app.run(debug=True)

































# from flask import Flask, render_template, request, redirect, url_for, session
# import psycopg2
# import os
# import base64
# from dotenv import load_dotenv

# app = Flask(__name__)
# app.secret_key = "your_secret_key"

# # Load .env file
# load_dotenv()

# # --- SUPABASE POSTGRESQL CONNECTION ---
# def get_db_connection():
#     return psycopg2.connect(
#         host=os.getenv("HOST"),
#         port=os.getenv("PORT"),
#         user=os.getenv("USER"),
#         password=os.getenv("PASSWORD"),
#         dbname=os.getenv("DBNAME"),
#         sslmode="require"
#     )

# # --- LOGIN PAGE ---
# @app.route('/')
# def login():
#     return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def do_login():
#     email = request.form['email']
#     password = request.form['password']

#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM users1 WHERE email=%s AND password=%s", (email, password))
#     user = cur.fetchone()
#     cur.close()
#     conn.close()

#     if user:
#         session['user_email'] = email
#         return redirect(url_for('details_form'))
#     else:
#         return "❌ Invalid login credentials"

# # --- DETAILS FORM ---
# @app.route('/details')
# def details_form():
#     if 'user_email' not in session:
#         return redirect(url_for('login'))
#     return render_template('detailsForm.html')

# @app.route('/submit_details', methods=['POST'])
# def submit_details():
#     if 'user_email' not in session:
#         return redirect(url_for('login'))

#     name = request.form['name']
#     age = request.form['age']
#     gender = request.form['gender']
#     address = request.form['address']
#     image = request.files['image']
#     image_data = image.read()

#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO user_details (email, name, age, gender, address, image)
#         VALUES (%s, %s, %s, %s, %s, %s)
#     """, (session['user_email'], name, age, gender, address, psycopg2.Binary(image_data)))

#     conn.commit()
#     cur.close()
#     conn.close()

#     return redirect(url_for('all_details'))

# # --- SHOW LAST ENTERED DETAILS ---
# @app.route('/show_details')
# def show_details():
#     if 'user_email' not in session:
#         return redirect(url_for('login'))

#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT name, age, gender, address, image 
#         FROM user_details
#         WHERE email = %s
#         ORDER BY created_at DESC LIMIT 1
#     """, (session['user_email'],))
    
#     result = cur.fetchone()
#     cur.close()
#     conn.close()

#     if result:
#         name, age, gender, address, image_data = result
#         image_base64 = base64.b64encode(image_data).decode('utf-8')
#         return render_template('showDetails.html', name=name, age=age, gender=gender, address=address, image=image_base64)
#     else:
#         return "❌ No details found."

# # --- SHOW ALL USERS DETAILS ---
# @app.route('/all_details')
# def all_details():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT name, age, gender, address, image FROM user_details ORDER BY created_at DESC")
#     rows = cur.fetchall()
#     cur.close()
#     conn.close()

#     all_users = []
#     for row in rows:
#         name, age, gender, address, image_data = row
#         image_base64 = base64.b64encode(image_data).decode('utf-8')
#         all_users.append({
#             'name': name,
#             'age': age,
#             'gender': gender,
#             'address': address,
#             'image': image_base64
#         })

#     return render_template('allDetails.html', users=all_users)

# if __name__ == '__main__':
#     app.run(debug=True)



