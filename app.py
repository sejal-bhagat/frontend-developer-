import os
import sqlite3
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, phone TEXT, prescription TEXT)')
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload.html')
@app.route('/upload')
def upload_page():
    return render_template('templates/upload.html')

@app.route('/submit', methods=['POST'])
def submit():
    phone = request.form.get('phone')
    file = request.files.get('prescription')

    if not phone or not file or file.filename == '':
        return "Error: File or Phone missing!", 400

    try:
        filename = secure_filename(f"{phone}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO orders (phone, prescription) VALUES (?, ?)", (phone, filename))
            conn.commit()

        return """
        <div style="text-align:center; margin-top:100px; font-family:sans-serif;">
            <h1 style="color: #008080;">✅ Order Confirmed!</h1>
            <p>Your prescription and phone number have been saved successfully.</p>
            <a href="/" style="display:inline-block; margin-top:20px; padding:10px 20px; background:#008080; color:white; text-decoration:none; border-radius:5px;">Back to Upload</a>
        </div>
        """
    except Exception as e:
        return f"Server Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)