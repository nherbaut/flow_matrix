from influxdb import DataFrameClient
import pandas as pd
from colour import Color
import numpy as np

white = Color("white")
to_blue = list(white.range_to(Color("blue"), 10))
to_red = list(white.range_to(Color("red"), 10))

query_template = """SELECT last("bytes") as value FROM "telegraf"."autogen"."nftables" WHERE time > now() - 1h AND "host_app_dst"='%s' AND "host_app_src"='%s' GROUP BY time(10w) FILL(null)"""
query_template_full = """SELECT last("bytes") as value FROM "telegraf"."autogen"."nftables" WHERE time > now() - 1h AND "host_app_dst_port"='%s' AND "host_app_src_port"='%s' GROUP BY time(10w) FILL(null)"""


def sizeof_get_color(num, matrix_mean=0, std_dev=999999999999):
    if num < matrix_mean:
        col = to_blue[min(int(abs(num - matrix_mean) / std_dev), len(to_blue)-1)]
    else:
        col = to_red[min(int(abs(num - matrix_mean) / std_dev), len(to_red)-1)]

    return col.get_web()


def sizeof_fmt(num, suffix='B'):
    if num == 0:
        return ""
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def matrix_value(template, client, a, b):
    query = template % (a, b)
    res = client.query(query)
    if 'nftables' in res:
        if 'value' in res["nftables"]:
            return res["nftables"]['value'][0]

    return 0


def get_data(influxdb_host, influxdb_port, formatter=sizeof_fmt):
    client = DataFrameClient(influxdb_host, influxdb_port, "", "", "telegraf")

    apps = [app["value"] for app in list(client.query('SHOW TAG VALUES ON "telegraf" WITH KEY="host_app_src"'))[0] if
            'salt' not in app["value"]]

    matrix = pd.DataFrame.from_items(
        items=[(a, [matrix_value(query_template, client, a, b) for b in apps]) for a in apps],
        columns=apps,
        orient="index")

    matrix_mean = np.mean((matrix!=0).mean())
    matrix_std = np.mean((matrix.std()))

    def custo_formatter(v):
        col=sizeof_get_color(v,matrix_mean,matrix_std )
        return (col,formatter(v))

    matrix = matrix.applymap(custo_formatter)

    return matrix


def get_data_full(influxdb_host, influxdb_port, formatter=sizeof_fmt):
    client = DataFrameClient(influxdb_host, influxdb_port, "", "", "telegraf")

    apps = [app["value"] for app in list(client.query('SHOW TAG VALUES ON "telegraf" WITH KEY="host_app_src_port"'))[0]
            if 'salt' not in app["value"]]

    matrix = pd.DataFrame.from_items(
        items=[(a, [matrix_value(query_template_full, client, a, b) for b in apps]) for a in apps],
        columns=apps,
        orient="index")

    matrix.applymap(formatter)
    return matrix
