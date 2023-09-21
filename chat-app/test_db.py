import mysql.connector as db
import os

conn = db.connect(host='chat-app-db', port=3306, user='chat-app', password=os.environ.get('MYSQL_PASSWORD'), database='ChatApp')
cur = conn.cursor()

data = {
    'username': 'test-user',
    'password': 'test-password'
}
query = 'INSERT INTO User (username, password) VALUES (%(username)s, %(password)s);'
cur.execute(query, data)
conn.commit()
cur.close()
conn.close()