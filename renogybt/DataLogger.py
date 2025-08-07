import json
import logging
import requests
import paho.mqtt.publish as publish
from configparser import ConfigParser
import datetime

class DataLogger:
    def __init__(self, config: ConfigParser):
        self.config = config

    def log_remote(self, json_data):
        headers = { "Authorization" : f"Bearer {self.config['remote_logging']['auth_header']}" }
        req = requests.post(self.config['remote_logging']['url'], json = json_data, timeout=15, headers=headers)
        logging.info("Log remote 200") if req.status_code == 200 else logging.error(f"Log remote error {req.status_code}")

    def log_mqtt(self, json_data):
        logging.info(f"mqtt logging")
        user = self.config['mqtt']['user']
        password = self.config['mqtt']['password']
        auth = None if not user or not password else {"username": user, "password": password}

        publish.single(
            self.config['mqtt']['topic'], payload=json.dumps(json_data),
            hostname=self.config['mqtt']['server'], port=self.config['mqtt'].getint('port'),
            auth=auth, client_id="renogy-bt"
        )

    def log_pvoutput(self, json_data):
        date_time = datetime.now().strftime("d=%Y%m%d&t=%H:%M")
        data = f"{date_time}&v1={json_data['power_generation_today']}&v2={json_data['pv_power']}&v3={json_data['power_consumption_today']}&v4={json_data['load_power']}&v5={json_data['controller_temperature']}&v6={json_data['battery_voltage']}"
        response = requests.post(self.config['pvoutput']['pvoutput_url'], data=data, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Pvoutput-Apikey": self.config['pvoutput']['api_key'],
            "X-Pvoutput-SystemId":  self.config['pvoutput']['system_id']
        })
        print(f"pvoutput {response}")

    def log_elasticsearch(self, dict_data):
            # Set the current time in ISO8601 format
            #date_time = datetime.now().strftime("%Y/%m/%dT%H:%M:%S+00:00")
            date_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
            #date_time = calendar.timegm(datetime.now().timetuple())
            # Add the timestamp to the dict
            dict_data["date"] = date_time
            # Convert the dict data to JSON format ready to send to Elasticsearch
            json_data = json.dumps(dict_data)
            logging.info("JSON_Data: " + json_data)
            # Build the destination URL from the config.ini data
            # http://<user>:<password>@<server>:<port>/<index>/_doc
            # Break this down into multiple lines for easy reading porpoises
            complete_url = self.config['elastic']['http_prefix'] + self.config['elastic']['server'] + ":" + self.config['elastic']['port']
            complete_url = complete_url + "/" + self.config['elastic']['index'] + "/_doc"
            # Set the verify boolean
            verify_flag = eval(self.config['elastic']['verify_ssl_cert'])
            # Send the data to Elasticseach
            response = requests.post(complete_url, data=json_data, auth=(self.config['elastic']['user'],self.config['elastic']['password']), headers={"Content-Type": "application/json"}, verify = verify_flag)
            logging.info(f"Elasticsearch {response}")
