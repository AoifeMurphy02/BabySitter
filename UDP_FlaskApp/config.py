import json

with open("/var/www/UDP_FlaskApp/babysitter_udp/.client_secrets.json") as config_file:
    config = json.load(config_file)