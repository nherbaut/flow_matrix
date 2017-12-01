from influxdb import DataFrameClient
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

import io
from colour import Color

white = Color("white")
to_blue = list(white.range_to(Color("blue"), 10))
to_red = list(white.range_to(Color("red"), 10))

query_template = """SELECT last("bytes") as value FROM "telegraf"."autogen"."nftables" WHERE time > now() - 1h AND "host_app_dst"='%s' AND "host_app_src"='%s' GROUP BY time(10w) FILL(null)"""
query_template_full = """SELECT last("bytes") as value FROM "telegraf"."autogen"."nftables" WHERE time > now() - 1h AND "host_app_dst_port"='%s' AND "host_app_src"='%s' GROUP BY time(10w) FILL(null)"""


def sizeof_get_color(num, matrix_mean=0, std_dev=999999999999):
    try:
        if num < matrix_mean:
            col = to_blue[min(int(abs(num - matrix_mean) / std_dev), len(to_blue) - 1)]
        else:
            col = to_red[min(int(abs(num - matrix_mean) / std_dev), len(to_red) - 1)]

        return col.get_web()
    except:
        return white.get_web()


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

    print(matrix.to_csv())

    matrix_mean = np.mean((matrix != 0).mean())
    matrix_std = np.mean((matrix.std()))

    def custo_formatter(v):
        col = sizeof_get_color(v, matrix_mean, matrix_std)
        return (col, formatter(v))

    svg = get_svg(matrix)

    matrix = matrix.applymap(custo_formatter)

    return matrix, svg


def get_data_full(influxdb_host, influxdb_port, formatter=sizeof_fmt):
    client = DataFrameClient(influxdb_host, influxdb_port, "", "", "telegraf")

    apps = [app["value"] for app in list(client.query('SHOW TAG VALUES ON "telegraf" WITH KEY="host_app_dst_port"'))[0]
            if 'salt' not in app["value"]]

    apps2 = [app["value"] for app in list(client.query('SHOW TAG VALUES ON "telegraf" WITH KEY="host_app_src"'))[0] if
             'salt' not in app["value"]]

    matrix = pd.DataFrame.from_items(
        items=[(a, [matrix_value(query_template, client, a, b) for b in apps2]) for a in apps],
        columns=apps2,
        orient="index")

    svg = get_svg(matrix)

    matrix.applymap(formatter)
    return matrix, svg


def get_svg(d):
    black = Color("black")
    to_red = list(black.range_to(Color("red"), 5))
    to_blue = list(black.range_to(Color("blue"), 5))

    d.apply(lambda x: 1 / x)

    def sizeof_get_color(num, matrix_mean=0, std_dev=999999999999):
        try:
            if num < matrix_mean:
                col = to_blue[min(int(abs(num - matrix_mean) / std_dev), len(to_blue) - 1)]
            else:
                col = to_red[min(int(abs(num - matrix_mean) / std_dev), len(to_red) - 1)]
            return col.get_web(), min(max((num - matrix_mean) / std_dev, 1), 15)
        except:
            return black.get_web(), 1

    def type_to_col(name_full):
        name = name_full.split("_")[-1]
        if name == "cass":
            return "green"
        elif name == "zoo":
            return "gray"
        elif name == "kafka":
            return "blue"
        elif name == "spark":
            return "red"
        else:
            return "red"
#Todo adapt for FULL page
    upper = d.where(~np.tril(np.ones(d.shape)).astype(np.bool))
    bottom = d.transpose().where(~np.tril(np.ones(d.shape)).astype(np.bool))
    bc = upper + bottom
    bc = bc.where(bc != 0)

    g = nx.Graph()

    mmean = np.mean(bc.mean())
    mstd = np.mean(bc.std())

    for row, array in bc.items():
        for column in array.index:
            if not pd.isnull(array[column]):
                g.add_edge(row, column, length=array[column], type=row)

    values = [type_to_col(node) for node in g.nodes()]
    node_labels = {node: node for node in g.nodes()}
    values_edge_color = [sizeof_get_color(e[2]["length"], mmean, mstd)[0] for e in g.edges(data=True)]
    values_edge_width = [2 * sizeof_get_color(e[2]["length"], mmean, mstd)[1] for e in g.edges(data=True)]

    nx.draw(g, with_labels=True, node_color=values, edge_color=values_edge_color, width=values_edge_width,
            labels=node_labels)
    # plt.show()
    s = io.StringIO()
    plt.legend(numpoints=1)
    plt.savefig(s, format="svg")
    plt.cla()
    return s.getvalue()
