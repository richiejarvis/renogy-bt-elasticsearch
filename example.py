import logging
import json
import configparser
import os
import sys
from renogybt import DCChargerClient, InverterClient, RoverClient, RoverHistoryClient, BatteryClient, DataLogger, Utils


config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.ini'
config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file)
config = configparser.ConfigParser(inline_comment_prefixes=('#'))
config.read(config_path)
# Pickup the log level from the config.ini

logging.basicConfig()
logger = logging.getLogger()
log_level_info = {'logging.DEBUG': logging.DEBUG,
                 'logging.INFO': logging.INFO,
                 'logging.WARNING': logging.WARNING,
                 'logging.ERROR': logging.ERROR,
                 }
my_log_level_from_config = config['log']['level']
my_log_level = log_level_info.get(my_log_level_from_config, logging.ERROR)
logger.setLevel(my_log_level)
data_logger: DataLogger = DataLogger(config)

# the callback func when you receive data
def on_data_received(client, data):
    filtered_data = Utils.filter_fields(data, config['data']['fields'])
    logging.info(f"{client.ble_manager.device.name} => {filtered_data}")
    if config['remote_logging'].getboolean('enabled'):
        data_logger.log_remote(json_data=filtered_data)
    if config['mqtt'].getboolean('enabled'):
        data_logger.log_mqtt(json_data=filtered_data)
    if config['pvoutput'].getboolean('enabled') and config['device']['type'] == 'RNG_CTRL':
        data_logger.log_pvoutput(json_data=filtered_data)
    if config['elastic'].getboolean('enabled') and config['device']['type'] == 'RNG_CTRL':
        data_logger.log_elasticsearch(dict_data=filtered_data)
    if not config['data'].getboolean('enable_polling'):
        client.stop()

# error callback
def on_error(client, error):
    print("hit this")
    logging.error(f"on_error: {error}")

# start client
if config['device']['type'] == 'RNG_CTRL':
    RoverClient(config, on_data_received, on_error).start()
elif config['device']['type'] == 'RNG_CTRL_HIST':
    RoverHistoryClient(config, on_data_received, on_error).start()
elif config['device']['type'] == 'RNG_BATT':
    BatteryClient(config, on_data_received, on_error).start()
elif config['device']['type'] == 'RNG_INVT':
    InverterClient(config, on_data_received, on_error).start()
elif config['device']['type'] == 'RNG_DCC':
    DCChargerClient(config, on_data_received, on_error).start()
else:
    logging.error("unknown device type")
