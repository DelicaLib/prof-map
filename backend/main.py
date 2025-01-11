import logging
import colorlog

import click

from app import run, prepare_app
from utils.parse_config import parse_config
from configurations import Container


formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s%(white)s %(asctime)s  %(name)-32s:%(reset)s %(log_color)s%(message)s",
    datefmt='%d-%m-%Y %H:%M:%S',
    log_colors={
        'DEBUG': 'light_black',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logging.basicConfig(level=logging.DEBUG, handlers=[console_handler])


def prepare_container(settings_dict):
    container = Container()
    container.raw_settings.override(settings_dict)
    container.wire([
        __name__,
        "dependencies",
        "applications",
        "app",
        "routers.debug",
        "routers.language_model",
        "routers.parser",
        "routers.openai",
        "routers.vacancy",
        "lifespan",
    ])


@click.command()
@click.option('--port', help='Server port', required=False)
@click.option('--config', help='Path to config', required=True)
def main(port: int, config: str):
    settings_dict = parse_config(config)
    if port is not None:
        settings_dict["port"] = port
    prepare_container(settings_dict)
    prepare_app()
    run(port=int(settings_dict["port"]))


if __name__ == "__main__":
    main()
