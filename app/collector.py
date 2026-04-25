"""
collector.py

Legge le metriche di sistema ogni 60 secondi e le scrive nel database:
    - psutil per la lettura delle metriche
    - SQLAlchemy per scriverle nel database
    - Loop con time.sleep
    - Ricerca dell'id_device per l'hostname
    - Calcolo della velocità di rete come differenza tra letture
"""

import os
import socket
import time

import psutil
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

# ricerca del proprio hostname nel database

def get_device_id():
    hostname = socket.gethostname()
    with engine.connect() as con:
        result = con.execute(
            text("SELECT id_device FROM device WHERE hostname = :hostname"),
            {"hostname": hostname}
        )
        row = result.fetchone()
        if row is None:
            raise RuntimeError(f"Device '{hostname}' non trovato nel database. ")
        return row[0]

# lettura valori di sistema tramite psutil

def leggi_metriche(prev_next, prev_time):
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    try:
        temps = psutil.sensors_temperatures()
        cpu_temp = temps["cpu_thermal"][0].current
    except (KeyError, AttributeError):
        try:
            cpu_temp = temps["coretemp"][0].current
        except (KeyError, AttributeError):
            cpu_temp = None

    curr_net = psutil.net_io_counters()
    curr_time = time.time()
    elapsed = curr_time - prev_time

    sent_mbs = (curr_net.bytes_sent - prev_net.bytes_sent) / elapsed / 1_000_000
    recv_mbs = (curr_net.bytes_recv - prev_net.bytes_recv) / elapsed / 1_000_000

    return {
        "cpu_usage": cpu,
        "ram_usage": ram,
        "disk_usage": disk,
        "cpu_temp": cpu_temp,
        "net_bytes_sent": round(sent_mbs, 4),
        "net_bytes_recv": round(recv_mbs, 4),
    }, curr_net, curr_time

# scrittura nel database delle metriche lette

def scrivi_metriche(id_device, metriche):
    with engine.connect() as con:
        for nome, valore in metriche.items():
            if valore is None:
                continue

            result = con.execute(
                text("SELECT id_metric FROM metric_type WHERE nome = :nome"),
                {"nome": nome}
            )
            row = result.fetchone()
            if row is None:
                print(f"[WARN] Metrica '{nome}' non trovata nel db, skip.")
                continue

            con.execute(
                text("""
                    INSERT INTO reading (id_device, id_metric, valore)
                    VALUES (:id_device, id_metric, :valore)
                """),
                {"id_device": id_device, "id_metric": row[0], "valore": valore}
            )
            con.commit()

# MAIN LOOP, all'avvio si recupera id_device e i contatori di rete iniziali (loop ogni 60 secondi)

def main():
    print("[INFO] Collector avviato.")
    id_device = get_device_id()
    print(f"[INFO] Device id: {id_device}")

    prev_net = psutil.net_io_counters()
    prev_time = time.time()

    time.sleep(60)

    while True:
        try:
            metriche, prev:net, prev_time = leggi_metriche(prev_net, prev_time)
            scrivi_metriche(id_device, metriche)
            print(f"[INFO] Metriche scritte: {metriche}")
        except Exception as e:
            print(f"[ERROR] {e}"

        time.sleep(60)


if __name__ =="__main__":
    main()
