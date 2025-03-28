import yaml

def read_config():
    config_path = 'conf/config.yaml'
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

