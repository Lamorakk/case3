import mysql.connector
from mysql.connector import Error

def init_db():
    try:
        conn = mysql.connector.connect(
            host='your_host',
            database='bot_database',
            user='your_username',
            password='your_password'
        )

        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    balance DECIMAL(10, 2) DEFAULT 0.00,
                    has_access TINYINT(1) DEFAULT 0
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    amount DECIMAL(10, 2),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            conn.commit()
            cursor.close()
            conn.close()

    except Error as e:
        print(f"Error: {e}")

# Call the function to initialize the database
init_db()
