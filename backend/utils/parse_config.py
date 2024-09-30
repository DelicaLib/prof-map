import tomllib
import os

from dopplersdk import DopplerSDK


def set_env_vars_from_doppler(token: str | None):
    if token is None:
        return
    sdk = DopplerSDK()
    sdk.set_access_token(token)
    secrets = sdk.secrets.list(
        project="prof-map",
        config="dev"
    ).secrets
    for key, value in secrets.items():
        os.environ[key] = value["computed"]


def parse_raw_settings(raw_settings):
    if isinstance(raw_settings, str):
        if raw_settings.startswith("env:$"):
            env_name = raw_settings.removeprefix("env:$")
            if os.environ.get(env_name) is None:
                raise ValueError(f"Not found environment variable ${env_name}")
            raw_settings = os.environ[env_name]

    if isinstance(raw_settings, dict):
        for key, value in raw_settings.items():
            new_value = parse_raw_settings(value)
            raw_settings[key] = new_value
    if isinstance(raw_settings, list):
        new_values = []
        for value in raw_settings:
            new_values.append(parse_raw_settings(value))

    return raw_settings


def parse_config(config_path: str) -> dict:
    with open(config_path, "rb") as toml_file:
        raw_settings = tomllib.load(toml_file)
    set_env_vars_from_doppler(parse_raw_settings(raw_settings.get("doppler_token")))
    return parse_raw_settings(raw_settings)
