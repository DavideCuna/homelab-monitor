-- SCHEMA

CREATE TABLE device (
		  id_device 	SERIAL 			PRIMARY KEY,
		  hostname 		VARCHAR(100) 	NOT NULL,
		  ip 				VARCHAR(45),
		  os 				VARCHAR(100),
		  note 			TEXT
);

CREATE TABLE metric_type (
		  id_metric 	SERIAL 			PRIMARY KEY,
		  nome 			VARCHAR(50) 	NOT NULL UNIQUE,
		  unita_misura VARCHAR(20) 	NOT NULL,
		  descrizione 	TEXT
);

CREATE TABLE reading (
		  id_reading 	SERIAL 			PRIMARY KEY,
		  id_device 	INTEGER 			NOT NULL REFERENCES device(id_device),
		  id_metric 	INTEGER 			NOT NULL REFERENCES metric_type(id_metric),
		  timestamp 	TIMESTAMPZ 		NOT NULL DEFAULT NOW(),
		  valore 		NUMERIC(10, 4) NOT NULL
);

-- SEED

INSERT INTO device (hostname, ip, os, note)
VALUES (
		  'dietpi',
		  '192.168.1.13',
		  'DietPi',
		  'Home server'
);

INSERT INTO metric_type (nome, unita_misura, descrizione) VALUES
		  ('cpu_usage'				'%',		'CPU usage percentage'),
		  ('ram_usage'				'%',		'RAM usage percentage'),
		  ('cpu_temp'				'°C',		'CPU temperature'),
		  ('disk_usage'			'%',		'Disk usage percentage on /'),
		  ('net_bytes_sent'		'MB/s',		'Network Mbytes sent per second'),
		  ('net_bytes_recv'		'MB/s',		'Network Mbytes received per second'),
