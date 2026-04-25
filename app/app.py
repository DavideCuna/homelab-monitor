# API Flask 
# Endpoints:
#   - GET   /api/metriche           ->  lista metriche disponibili
#   - POST  /api/letture            ->  ultime N letture per una metrica
#   - POST  /api/media_oraria       ->  media oraria nelle ultime 24 ore
#   - POST  /api/range_valori       ->  min e max di una metrica
#   - POST  /api/media_per_metrica  -> media per matrica in un intervallo date

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text
import pandas as pd
import os

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

app = Flask("homelab_monitor")

# ENDPOINT 1: GET /api/metriche
@app.route("/api/metriche")
def get_metriche():
    with engine.connect() as con:
        df = pd.read_sql_query(
            sql=text("SELECT nome, unita_misura, descrizione FROM metric_type ORDER BY nome"),
            con=con
        )
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
