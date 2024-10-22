from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# MySQL connection configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'abhi1502'  # Add your MySQL password here
MYSQL_DB = 'anomaly_db'

# Function to get a MySQL database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

@app.route('/send-anomalies', methods=['POST'])
def send_anomalies():
    data = request.json
    
    # Get the database connection
    connection = get_db_connection()

    # If connection is None, return an error message
    if connection is None:
        return jsonify({"status": "error", "message": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor()  # Use cursor() method instead of a context manager with mysql.connector
        sql = "INSERT INTO anomalies (timestamp, value, is_anomaly) VALUES (%s, %s, %s)"
        for anomaly in data["anomalies"]:
            cursor.execute(sql, (anomaly["timestamp"], anomaly["value"], anomaly["is_anomaly"]))
        connection.commit()

    except Error as e:
        print(f"Error executing SQL query: {e}")
        return jsonify({"status": "error", "message": "Failed to execute SQL query"}), 500

    finally:
        # Always close the connection if it was successfully established
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

    return jsonify({"status": "success", "message": "Anomalies sent to the database"}), 200

if __name__ == '__main__':
    app.run(debug=True)
