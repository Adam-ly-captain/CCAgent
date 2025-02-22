import yaml


def parse_config(config_path="cca/config/dev.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def get_agent_config():    
    config = parse_config()
    return config['openai']


def get_tool_agent_config():
    config = parse_config()
    return config['tool_openai']


def get_ui_control_config():
    config = parse_config()
    return config['ui_control']


def get_os_config():
    config = parse_config()
    return config['os']


def get_screen_resolution():
    config = parse_config()
    return config['screen_resolution']


def get_db_config():
    config = parse_config()
    return config['db']


def get_applications_info() -> str:
    config = parse_config()
    app_path = config['application']
    return app_path
