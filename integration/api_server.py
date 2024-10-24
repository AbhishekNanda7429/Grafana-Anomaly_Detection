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

@app.route('/calls-total', methods=['POST'])
def send_anomalies_calls_total():
    data = request.json
    
    # Get the database connection
    connection = get_db_connection()

    # If connection is None, return an error message
    if connection is None:
        return jsonify({"status": "error", "message": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor()  # Use cursor() method instead of a context manager with mysql.connector
        sql = "INSERT INTO calls_total (timestamp, value, is_anomaly) VALUES (%s, %s, %s)"
        
        # Iterate over the full dataset (not just anomalies)
        for entry in data["data"]:
            cursor.execute(sql, (entry["timestamp"], entry["value"], entry["is_anomaly"]))
        
        # Commit all changes to the database
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

    return jsonify({"status": "success", "message": "Data sent to the database"}), 200

@app.route('/scrape-duration-seconds', methods=['POST'])
def send_anomalies_scrape_duration_seconds():
    data = request.json
    
    # Get the database connection
    connection = get_db_connection()

    # If connection is None, return an error message
    if connection is None:
        return jsonify({"status": "error", "message": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor()  # Use cursor() method instead of a context manager with mysql.connector
        sql = "INSERT INTO scrape_duration_seconds (timestamp, value, is_anomaly) VALUES (%s, %s, %s)"
        
        # Iterate over the full dataset (not just anomalies)
        for entry in data["data"]:
            cursor.execute(sql, (entry["timestamp"], entry["value"], entry["is_anomaly"]))
        
        # Commit all changes to the database
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

    return jsonify({"status": "success", "message": "Data sent to the database"}), 200

@app.route('/duration-milliseconds-sum', methods=['POST'])
def send_anomalies_duration_milliseconds_sum():
    data = request.json
    
    # Get the database connection
    connection = get_db_connection()

    # If connection is None, return an error message
    if connection is None:
        return jsonify({"status": "error", "message": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor()  # Use cursor() method instead of a context manager with mysql.connector
        sql = "INSERT INTO duration_milliseconds_sum (timestamp, value, is_anomaly) VALUES (%s, %s, %s)"
        
        # Iterate over the full dataset (not just anomalies)
        for entry in data["data"]:
            cursor.execute(sql, (entry["timestamp"], entry["value"], entry["is_anomaly"]))
        
        # Commit all changes to the database
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

    return jsonify({"status": "success", "message": "Data sent to the database"}), 200

@app.route('/duration-milliseconds-bucket', methods=['POST'])
def send_anomalies_duration_millisecond_bucket():
    data = request.json
    
    # Get the database connection
    connection = get_db_connection()

    # If connection is None, return an error message
    if connection is None:
        return jsonify({"status": "error", "message": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor()  # Use cursor() method instead of a context manager with mysql.connector
        sql = "INSERT INTO duration_millisecond_bucket (timestamp, value, is_anomaly) VALUES (%s, %s, %s)"
        
        # Iterate over the full dataset (not just anomalies)
        for entry in data["data"]:
            cursor.execute(sql, (entry["timestamp"], entry["value"], entry["is_anomaly"]))
        
        # Commit all changes to the database
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

    return jsonify({"status": "success", "message": "Data sent to the database"}), 200

if __name__ == '__main__':
    app.run(debug=True)
