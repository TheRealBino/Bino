from flask import Flask, jsonify, request, send_from_directory
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "mills.db"

app = Flask(
    __name__,
    static_folder=str(BASE_DIR),   # serve index.html from this folder
    static_url_path=""
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mill_name TEXT NOT NULL,
            supplier TEXT NOT NULL,
            material TEXT NOT NULL,
            country TEXT NOT NULL,
            address TEXT,
            latitude REAL,
            longitude REAL
        );
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    # Serve your existing index.html directly from this folder
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/mills", methods=["GET"])
def get_mills():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM mills;")
    rows = cur.fetchall()
    conn.close()
    mills = [
        {
            "id": row["id"],
            "mill_name": row["mill_name"],
            "supplier": row["supplier"],
            "material": row["material"],
            "country": row["country"],
            "address": row["address"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
        }
        for row in rows
    ]
    return jsonify(mills)

@app.route("/api/mills", methods=["POST"])
def create_mill():
    data = request.get_json(force=True) or {}
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO mills (mill_name, supplier, material, country, address, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("mill_name", "Unnamed Mill"),
            data.get("supplier", "Unknown Supplier"),
            data.get("material", "Unknown Material"),
            data.get("country", "Unknown Country"),
            data.get("address", ""),
            data.get("latitude"),
            data.get("longitude"),
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({"id": new_id}), 201

@app.route("/api/mills/<int:mill_id>", methods=["PUT"])
def update_mill(mill_id):
    data = request.get_json(force=True) or {}
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE mills
        SET mill_name = ?, supplier = ?, material = ?, country = ?, address = ?, latitude = ?, longitude = ?
        WHERE id = ?
        """,
        (
            data.get("mill_name", "Unnamed Mill"),
            data.get("supplier", "Unknown Supplier"),
            data.get("material", "Unknown Material"),
            data.get("country", "Unknown Country"),
            data.get("address", ""),
            data.get("latitude"),
            data.get("longitude"),
            mill_id,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})

@app.route("/api/mills/<int:mill_id>", methods=["DELETE"])
def delete_mill(mill_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM mills WHERE id = ?", (mill_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True,
        ssl_context=("cert.pem", "key.pem")
    )

import os
import psycopg2
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Pull DATABASE_URL from environment (Render will set this)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route("/")
def index():
    # serve your single-page app
    return send_from_directory(".", "index.html")

@app.route("/api/mills", methods=["GET"])
def list_mills():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, mill_name, supplier, material, country, address, latitude, longitude "
        "FROM mills"
    )
    rows = cur.fetchall()
    conn.close()

    mills = []
    for r in rows:
        mills.append({
            "id": r[0],
            "mill_name": r[1],
            "supplier": r[2],
            "material": r[3],
            "country": r[4],
            "address": r[5],
            "latitude": float(r[6]) if r[6] is not None else None,
            "longitude": float(r[7]) if r[7] is not None else None,
        })
    return jsonify(mills)

@app.route("/api/mills", methods=["POST"])
def create_mill():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO mills (mill_name, supplier, material, country, address, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            data.get("mill_name"),
            data.get("supplier"),
            data.get("material"),
            data.get("country"),
            data.get("address"),
            data.get("latitude"),
            data.get("longitude"),
        ),
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return jsonify({"id": new_id}), 201

@app.route("/api/mills/<int:id>", methods=["PUT"])
def update_mill(id):
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE mills
        SET mill_name = %s,
            supplier = %s,
            material = %s,
            country = %s,
            address = %s,
            latitude = %s,
            longitude = %s
        WHERE id = %s
        """,
        (
            data.get("mill_name"),
            data.get("supplier"),
            data.get("material"),
            data.get("country"),
            data.get("address"),
            data.get("latitude"),
            data.get("longitude"),
            id,
        ),
    )
    conn.commit()
    conn.close()
    return "", 204

@app.route("/api/mills/<int:id>", methods=["DELETE"])
def delete_mill(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM mills WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)