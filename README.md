# IoT Garden

# Getting started
## Set up your environment (.env) file

```xml
iot_connection_string=<iot-connection-string>
log_analytics_instrumentation_key=<app-insights-instrumentation-key>
analogue_device=mcp3008
pin_number_pump=16
pin_number_dht=12
tsdb_user=<user>
tsdb_password=<password>
tsdb_dbname=<db-name>
tsdb_host=<host>.postgres.database.azure.com
log_level=INFO
pin_clk=18
pin_miso=23
pin_mosi=24
pin_cs=25
analogue_channel=4
```

## Install Python 3.7

If you have raspbian, you may have a old version of Python which isn't compatiable.

```bash
$ sudo apt-get update

$ sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev

$ wget https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tgz

$ sudo tar zxf Python-3.7.7.tgz

$ cd Python-3.7.7

$ sudo ./configure

$ sudo make -j 4

$ sudo make altinstall

$ python3.7 -V
```

## Install psycopg2
```bash
git clone https://github.com/psycopg/psycopg2
cd psycopg2
`which python3.7` setup.py build
`which python3.7` setup.py install
```

## Set up your Virtual Environment

```bash
$ python3.7 -m venv ~/GIT/iot-garden/env

$ source env/bin/activate

$ pip install -r requirements.txt --default-timeout=100
```

## Setup TimescaleDB

TimescaleDB is a time series database and i used to store the telemetry created from the device.

## Setup Grafana

Grafana is an open-source time series visualisation tool

## Build into Docker container


# Just run with Docker

```bash
$ docker-compose up
```

