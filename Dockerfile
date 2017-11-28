from python:3.6-slim
COPY requirements-python3.txt /tmp/requirements-python3.txt
RUN pip install -r /tmp/requirements-python3.txt
COPY ./dist/Flow_Matrix_Web_page-0.0.3-py3.6.egg /tmp/Flow_Matrix_Web_page-0.0.3-py3.6.egg
RUN easy_install /tmp/Flow_Matrix_Web_page-0.0.3-py3.6.egg
EXPOSE 5011
CMD flow-matrix --influxdb_host $INFLUX_DB_HOST
