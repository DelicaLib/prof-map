import logging

import click

from app import run, prepare_app
from utils.parse_config import parse_config
from configurations import Container


logging.basicConfig(level=logging.DEBUG)


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
