import pathlib

from pydantic_yaml import parse_yaml_file_as
from pygame import Vector2

from .model import Config


class AppConfig:
    def __init__(self):
        self.config = parse_yaml_file_as(Config, pathlib.Path(__file__).parent / "config.yaml")

    @property
    def app(self):
        return self.config.app

    @property
    def game(self):
        return self.config.app.game

    @property
    def screen(self):
        return self.config.app.screen


app_config = AppConfig()
