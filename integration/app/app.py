from flask import Flask, request, jsonify
import pymysql  # or psycopg2 for PostgreSQL

app = Flask(__name__)

def connect_db():
    connection = pymysql.connect(
        host='localhost',
        user='your_user',
        password='your_password',
        db='anomaly_db'
    )
    return connection

@app.route('/send-anomalies', methods=['POST'])
def send_anomalies():
    data = request.json
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO anomalies (timestamp, value, is_anomaly) VALUES (%s, %s, %s)"
            for anomaly in data["anomalies"]:
                cursor.execute(sql, (anomaly["timestamp"], anomaly["value"], anomaly["is_anomaly"]))
        connection.commit()
    finally:
        connection.close()
    return jsonify({"status": "success", "message": "Anomalies sent to the database"}), 200

if __name__ == '__main__':
    app.run(debug=True)
