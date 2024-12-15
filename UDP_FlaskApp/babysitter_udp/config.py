import json

with open("/var/www/.client_secrets.json") as config_file:
    config = json.load(config_file)