import os
import psycopg2
from flask import Flask, jsonify, request, send_from_directory

app = Flask(
    __name__,
    static_folder=".",
    static_url_path=""
)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

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
