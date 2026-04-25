# Homelab Monitor

A lightweight, professional system monitoring solution designed specifically for home servers and Raspberry Pi environments. It continuously collects essential system metrics and provides a clean, responsive dashboard for real-time and historical visualization.

## Overview

Homelab Monitor is built to be simple to deploy and efficient to run. It gathers system data through a dedicated Python collector, stores the information securely in a PostgreSQL database, and exposes the data via a Flask REST API. The entire stack is containerized, ensuring a reliable and reproducible deployment process across different host machines.

## Features

- System Metrics Collection: Tracks CPU usage, memory utilization, disk space, network activity, and thermal readings.
- Historical Data Storage: Utilizes PostgreSQL for reliable, long-term metric persistence.
- RESTful API: Exposes a Flask-based API for programmatic access to current and historical system states.
- Web Dashboard: Features a minimalist and functional web interface for data visualization and system overview.
- Containerized Architecture: Fully packaged with Docker and Docker Compose for effortless installation.

## Architecture

The project consists of three main components running as Docker containers:
1. Collector: A background Python process utilizing `psutil` to harvest system metrics at regular intervals.
2. API & Dashboard: A Flask application that serves the static web interface and handles data requests.
3. Database: A PostgreSQL instance that stores all historical telemetry data.

## Prerequisites

- Docker
- Docker Compose

## Installation and Deployment

1. Clone the repository to your target machine:
   ```bash
   git clone https://github.com/DavideCuna/homelab-monitor.git
   cd homelab-monitor
   ```

2. Configure the environment variables:
   Create a `.env` file in the project root directory and define the required database credentials and configuration:
   ```env
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=secure_password
   POSTGRES_DB=homelab
   APP_PORT=5000
   DEVICE_HOSTNAME=my_server
   ```

3. Deploy the stack:
   Run the following command to build the images and start the services:
   ```bash
   docker-compose up -d --build
   ```

4. Access the Dashboard:
   Open a web browser and navigate to `http://<your-server-ip>:<APP_PORT>` to view the monitoring interface.

## Project Structure

- `/app`: Contains the Python source code for both the metric collector and the Flask REST API.
- `/dashboard`: Holds the HTML, CSS, and JavaScript files for the web interface.
- `/db`: Includes database initialization scripts for the PostgreSQL container.
