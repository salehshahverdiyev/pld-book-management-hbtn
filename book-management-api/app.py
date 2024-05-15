from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import jwt
import os
from functools import wraps

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  
app.config['SECRET_KEY'] = '12345'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publication_date = db.Column(db.Date, nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

with app.app_context():
    db.create_all()

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(username=data['username']).first()
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return func(current_user, *args, **kwargs)

    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 409

    password_hash = generate_password_hash(password)

    new_user = User(username=username, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid username or password'}), 401

    token = jwt.encode({'username': username}, app.config['SECRET_KEY'])
    return jsonify({'token': token.decode('UTF-8')}), 200

@app.route('/books', methods=['GET'])
@token_required
def get_books():
    """
    Get all books or filter by query parameters
    """
    title = request.args.get('title')
    author = request.args.get('author')
    genre = request.args.get('genre')
    publication_date = request.args.get('publication_date')

    books = Book.query

    if title:
        books = books.filter(Book.title.like(f'%{title}%'))
    if author:
        books = books.filter(Book.author.like(f'%{author}%'))
    if genre:
        books = books.filter(Book.genre == genre)
    if publication_date:
        try:
            publication_date = datetime.datetime.strptime(publication_date, '%Y-%m-%d').date()
            books = books.filter(Book.publication_date == publication_date)
        except ValueError:
            return jsonify({'message': 'Invalid publication date format'}), 400

    books = books.all()
    return jsonify([book.to_dict() for book in books])

@app.route('/books/<int:book_id>', methods=['GET'])
@token_required
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@app.route('/books', methods=['POST'])
@token_required
def create_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    publication_date = data.get('publication_date')
    genre = data.get('genre')
    isbn = data.get('isbn')

    if not title or not author or not publication_date or not genre or not isbn:
        return jsonify({'message': 'All fields are required'}), 400

    try:
        publication_date = datetime.datetime.strptime(publication_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid publication date format'}), 400

    new_book = Book(title=title, author=author, publication_date=publication_date, genre=genre, isbn=isbn)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book created successfully'}), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
@token_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.publication_date = data.get('publication_date', book.publication_date)
    book.genre = data.get('genre', book.genre)
    book.isbn = data.get('isbn', book.isbn)

    db.session.commit()
    return jsonify({'message': 'Book updated successfully'}), 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
@token_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'}), 204

class Book:
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'publication_date': self.publication_date.strftime('%Y-%m-%d'),
            'genre': self.genre,
            'isbn': self.isbn
        }

if __name__ == '__main__':
    app.run(debug=True)