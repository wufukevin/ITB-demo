import pathlib

from pydantic_yaml import parse_yaml_file_as

from .config import Model

__config_path = pathlib.Path(__file__).parent / "config.yaml"
app_config = parse_yaml_file_as(Model, __config_path)
