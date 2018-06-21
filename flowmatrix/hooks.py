query_template = """SELECT last("bytes") as value FROM "telegraf"."autogen"."nftables" WHERE time > now() - 1h AND "host_app_dst"='%s' AND "host_app_src"='%s' GROUP BY time(10w) FILL(null)"""
query_template_full = """SELECT last("bytes") as value FROM "telegraf"."autogen"."nftables" WHERE time > now() - 1h AND "host_app_dst_port"='%s' AND "host_app_src"='%s' GROUP BY time(10w) FILL(null)"""

