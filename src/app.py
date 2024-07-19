from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, docx, PyPDF2, textract
from dbconnect import app, db, User, Document
from sqlalchemy import func, or_
from sqlalchemy.sql import text
from flask import Flask, render_template, request
from weather import get_weather  

app.secret_key = 'd69706d5e537202f9fd1ec67f5772ae4'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_file_content(file_path, extension):
    content = ""
    if extension == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    elif extension == 'docx':
        doc = docx.Document(file_path)
        content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    elif extension == 'pdf':
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            content = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif extension == 'doc':
        content = textract.process(file_path).decode('utf-8')
    return content

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('search'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
'''
@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    results = []
    if request.method == 'POST':
        query = request.form['query']
        query = query.lower()

        results = Document.query.filter(
            or_(
                func.lower(Document.content).contains(query),
                func.lower(Document.title).contains(query)
            )
        ).all()

    return render_template('search.html', results=results)
'''
@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    results = []
    if request.method == 'POST':
        query = request.form['query']
        query = query.lower()

        phrase_query = f'"{query}"'

        results = db.session.query(Document, text(
            "MATCH(content, title) AGAINST(:phrase_query IN BOOLEAN MODE) AS relevance"
        )).filter(text(
            "MATCH(content, title) AGAINST(:phrase_query IN BOOLEAN MODE)"
        )).params(phrase_query=phrase_query).order_by(text("relevance DESC")).all()

    return render_template('search.html', results=[result[0] for result in results])

@app.route('/document', methods=['GET', 'POST'])
def document():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            try:
                content = read_file_content(file_path, filename.rsplit('.', 1)[1].lower())
            except Exception as e:
                flash(f'Error reading file content: {e}', 'error')
                return redirect(request.url)
            new_document = Document(title=filename, content=content)
            db.session.add(new_document)
            db.session.commit()
            flash('Document added successfully!', 'success')
            return redirect(url_for('document'))

    return render_template('document.html')

@app.route('/document/<int:document_id>')
def view_document(document_id):
    document = Document.query.get_or_404(document_id)
    return render_template('view_document.html', document=document)

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'username': user.username, 'email': user.email} for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        if not data or not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({'error': 'Missing required fields'}), 400

        new_user = User(username=data['username'], email=data['email'], password_hash=generate_password_hash(data['password']))
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/weather')
def weather():
    city = request.args.get('city', 'London')  # Default to London if city parameter not provided
    weather_data = get_weather(city)
    
    if weather_data:
        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        return render_template('weather.html', temperature=temperature, description=description, humidity=humidity)
    else:
        return render_template('weather.html', error=True)


if __name__ == '__main__':
    app.run(debug=True)
