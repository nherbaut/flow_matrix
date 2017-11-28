from influxdb import DataFrameClient
import pandas as pd

query_template = """SELECT last("bytes") as value FROM "telegraf"."autogen"."nftables" WHERE time > now() - 1h AND "host_app_dst"='%s' AND "host_app_src"='%s' GROUP BY time(10w) FILL(null)"""
query_template_full = """SELECT last("bytes") as value FROM "telegraf"."autogen"."nftables" WHERE time > now() - 1h AND "host_app_dst_port"='%s' AND "host_app_src_port"='%s' GROUP BY time(10w) FILL(null)"""


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
    print(query)
    res = client.query(query)
    if 'nftables' in res:
        if 'value' in res["nftables"]:
            return res["nftables"]['value'][0]

    return 0


def get_data(influxdb_host, influxdb_port):
    client = DataFrameClient(influxdb_host, influxdb_port, "", "", "telegraf")

    df = pd.DataFrame(data=list(range(30)))

    apps = [app["value"] for app in list(client.query('SHOW TAG VALUES ON "telegraf" WITH KEY="host_app_src"'))[0] if
            'salt' not in app["value"]]

    matrix = pd.DataFrame.from_items(
        items=[(a, [sizeof_fmt(matrix_value(query_template, client, a, b)) for b in apps]) for a in apps],
        columns=apps,
        orient="index")
    return matrix.to_dict()


def get_data_full(influxdb_host, influxdb_port):
    client = DataFrameClient(influxdb_host, influxdb_port, "", "", "telegraf")

    df = pd.DataFrame(data=list(range(30)))

    apps = [app["value"] for app in list(client.query('SHOW TAG VALUES ON "telegraf" WITH KEY="host_app_src_port"'))[0]
            if 'salt' not in app["value"]]

    matrix = pd.DataFrame.from_items(
        items=[(a, [sizeof_fmt(matrix_value(query_template_full, client, a, b)) for b in apps]) for a in apps],
        columns=apps,
        orient="index")
    return matrix.to_dict()
