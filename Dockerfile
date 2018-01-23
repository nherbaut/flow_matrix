from python:3.6-slim
RUN apt-get update && apt-get install tk-dev --yes --no-install-recommends && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY ./dist/*.whl /tmp
RUN pip install /tmp/*.whl
EXPOSE 5011
CMD flow-matrix --influxdb_host $INFLUX_DB_HOST 
