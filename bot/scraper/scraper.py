import undetected_chromedriver as uc

import yaml
import time

URL = "https://newsfilter.io/latest/news"

TIMESTAMP_CLASS = "sc-bwzfXH dasLyX"
STOCK_CLASS = "sc-bxivhb dirVGp"
# First span in this div without class is the headline
HEADLINE_CLASS = "sc-gZMcBi fWkNgt"


def load_config():
    with open("config.yml", "r") as config_file:
        config = yaml.safe_load(config_file)

    return config


def connect_database(dsn):
    return None


if __name__ == "__main__":
    driver = uc.Chrome(headless=True, use_subprocess=True)
    config = load_config()
    db = connect_database(config.get("database"))
    while True:
        time.sleep(config.get("interval", 30))
