monitoring:
  - host: h0
placement:
  cassandra:
      instances:
        - name: cassa
          host: h1
        - name: cassb
          host: h2
        - name: cassc
          host: h3
      version: 3.11.1
      first_cqlsh_instance: cassa
      antiaffinity: True
  client:
      instances:
        - name: clia
          host: h1
          configuration:
            target: h2
        - name: clib
          host: h2
          configuration:
            target: h3
        - name: clic
          host: h3
          configuration:
            target: h1

