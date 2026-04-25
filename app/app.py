# API Flask 
# Endpoints:
#   - GET   /api/metriche           ->  lista metriche disponibili
#   - POST  /api/letture            ->  ultime N letture per una metrica
#   - POST  /api/media_oraria       ->  media oraria nelle ultime 24 ore
#   - POST  /api/range_valori       ->  min e max di una metrica
#   - POST  /api/media_per_metrica  -> media per matrica in un intervallo date

from flask import Flask, jsonify, request, send_from_directory
from sqlalchemy import create_engine, text
import pandas as pd
import os

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

app = Flask("homelab_monitor")

# ---
# ENDPOINT 1: GET /api/metriche

@app.route("/api/metriche")
def get_metriche():
    with engine.connect() as con:
        df = pd.read_sql_query(
            sql=text("SELECT nome, unita_misura, descrizione FROM metric_type ORDER BY nome"),
            con=con
        )
    return jsonify(df.to_dict(orient="records"))

# ---
# ENDPOINT 2: POST /api/letture
# body atteso: {"metrica": "cpu_usage", "limit": 100 }

@app.route("/api/letture", methods=["POST"])
def get_letture():
    dati = request.get_json()
    metrica = dati["metrica"]
    limit = dati.get("limit", 100)

    with engine.connect() as con:
        df = pd.read_sql_query(
            sql=text("""
                SELECT R.timestamp, R.valore, M.unita_misura
                FROM reading as R
                JOIN metric_type AS M on M.id_metric = R.id_metric
                JOIN device AS D ON D.id_device = R.id_device
                WHERE M.nome = :metrica
                ORDER BY R.timestamp DESC
                LIMIT :limit
            """),
            con=con,
            params={"metrica": metrica, "limit":limit}
        )
    
    df = df.iloc[::-1].reset_index(drop=True)

    return jsonify(df.to_dict(orient="records"))

# ---
# ENDPOINT 3: POST /api/media_oraria
# body atteso: { "metrica": "cpu_usage"}

@app.route("/api/media_oraria", methods=["POST"])
def get_media_oraria():
    dati = request.get_json()
    metrica = dati["metrica"]

    with engine.connect() as con:
        df = pd.read_sql_query(
            sql=text("""
                SELECT DATE_TRUNC('hour', R.timestamp) AS ora, 
                       AVG(R.valore) AS media
                FROM reading AS R
                JOIN metric_type AS M ON M.id_metric = R.id_metric
                WHERE M.nome = :metrica
                AND R.timestamp >= NOW() - INTERVAL '24 hours'
                GROUP BY ora
                ORDER BY ora
            """),
            con=con,
            params={"metrica": metrica}
        )

    return jsonify(df.to_dict(orient="records"))

# ---
# ENDPOINT 4: POST /api/range_valori
# body atteso: {"metrica": "cpu_usage"}

@app.route("/api/range_valori", methods=["POST"])
def get_range_valori():
    dati = request.get_json()
    metrica = dati["metrica"]

    with engine.connect() as con:
        df = pd.read_sql_query(
            sql=text("""
                SELECT MIN(R.valore) AS valore_min,
                       MAX(R.valore) AS valore_max
                FROM reading AS R
                JOIN metric_type AS M ON M.id_metric = R.id_metric
                WHERE M.nome = :metrica
            """),
            con=con,
            params={"metrica": metrica}
        )

    if df.empty or df.iloc[0]["valore_min"] is None:
        return jsonify({"valore_min": None, "valore_max": None})

    return jsonify(df.iloc[0].to_dict())

# ---
# ENDPOINT 5: POST /api/media_per_metrica
# body atteso: { "start_date": "2026-01-01", "end_date": "2026-01-31" }

@app.route("/api/media_per_metrica", methods=["POST"])
def get_media_per_metrica():
    dati = request.get_json()
    start_date = dati["start_date"]
    end_date = dati["end_date"]

    with engine.connect() as con:
        df = pd.read_sql_query(
            sql=text("""
                SELECT M.nome AS metrica,
                       M.unita_misura AS unita,
                       AVG(R.valore) AS media,
                       MIN(R.valore) as minimo,
                       MAX(R.valore) as massimo
                FROM reading AS R
                JOIN metric_type AS M ON M.id_metric = R.id_metric
                WHERE R.timestamp BETWEEN :start_date AND :end_date
                GROUP BY M.nome, M.unita_misura
                ORDER BY M.nome
            """),
            con=con,
            params={"start_date": start_date, "end_date": end_date}
        )

    return jsonify(df.to_dict(orient="records"))

# ---
# DASHBOARD

@app.route("/")
def index():
    return send_from_directory("../dashboard", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
