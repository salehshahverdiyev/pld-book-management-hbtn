import requests

base_url = 'http://127.0.0.1:5000'

def test_get_all_books():
    response = requests.get(f'{base_url}/books')
    if response.status_code == 200:
        print('Success: GET /books')
        print(response.json())
    else:
        print(f'Error: {response.status_code} - {response.text}')

def test_create_book():
    new_book = {
        'title': 'The Hitchhiker\'s Guide to the Galaxy',
        'author': 'Douglas Adams',
        'publication_date': '1979-05-12',
        'genre': 'Science Fiction',
        'isbn': '0345391802'
    }
    response = requests.post(f'{base_url}/books', json=new_book)
    if response.status_code == 201:
        print('Success: POST /books')
        print(response.json()) 
    else:
        print(f'Error: {response.status_code} - {response.text}')

def test_get_book_by_id(book_id):
    response = requests.get(f'{base_url}/books/{book_id}')
    if response.status_code == 200:
        print(f'Success: GET /books/{book_id}')
        print(response.json())
    else:
        print(f'Error: {response.status_code} - {response.text}')

def test_register_user():
    new_user = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    response = requests.post(f'{base_url}/register', json=new_user)
    if response.status_code == 201:
        print('Success: POST /register')
        print(response.json())
    else:
        print(f'Error: {response.status_code} - {response.text}')

def test_register_user():
    new_user = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    response = requests.post(f'{base_url}/register', json=new_user) 


test_register_user()
test_get_all_books()
test_create_book()
test_get_book_by_id(1)

assert response.status_code == 200, 'GET /books should return 200'
assert 'title' in response.json(), 'Response should contain a title' 