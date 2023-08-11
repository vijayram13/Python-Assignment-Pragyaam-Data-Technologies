from flask import Flask, request, jsonify
import requests
import sqlite3

app = Flask(__name__)

# Initialize SQLite database connection
conn = sqlite3.connect('user_database.db', check_same_thread=False)
cursor = conn.cursor()

# Create user table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        age INTEGER,
        gender TEXT,
        email TEXT,
        phone TEXT,
        Birth_date TEXT
    )
''')
conn.commit()


@app.route('/api/users', methods=['GET'])
def search_users():
    first_name = request.args.get('first_name')
    # print(first_name)
    if not first_name:
        return jsonify({'error': 'Missing mandatory parameter "first_name"'}), 400

    # Search for users in the local database
    cursor.execute('SELECT * FROM user WHERE first_name LIKE ?', (f'{first_name}%',))
    matching_users = cursor.fetchall()

    if matching_users:
        users_response = [
            {'id': user[0], 'first_name': user[1], 'last_name': user[2], 'age': user[3], 'gender': user[4],
             'email': user[5], 'phone': user[6], 'Birth_date': user[7]} for user in matching_users]
        return jsonify(users_response)
    else:
        # If no users found, fetch from external API
        external_api_url = f'https://dummyjson.com/users/search?q={first_name}'
        response = requests.get(external_api_url)
        new_users = response.json()
        print("new_users",new_users)

        # Save new users to local database
        for user in new_users["users"]:

            # print("hello",cursor.execute('SELECT id FROM user WHERE id <>', (f"{user['id']}")))
            cursor.execute(
                'INSERT INTO user (id,first_name, last_name, age, gender, email, phone, Birth_date) VALUES (?,?, ?, ?, ?, ?, ?, ?)',
                (user['id'], user['firstName'], user['lastName'], user['age'], user['gender'], user['email'], user['phone'],
                 user['birthDate']))
        conn.commit()

        return jsonify(new_users)


if __name__ == '__main__':
    app.run()