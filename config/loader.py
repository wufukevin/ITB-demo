import pathlib

from pydantic_yaml import parse_yaml_file_as

from .model import Config, App, Game, Screen


class AppConfig:
    def __init__(self):
        self.config = parse_yaml_file_as(Config, pathlib.Path(__file__).parent / "config.yaml")

    @property
    def app(self) -> App:
        return self.config.app

    @property
    def game(self) -> Game:
        return self.config.app.game

    @property
    def screen(self) -> Screen:
        return self.config.app.screen


app_config = AppConfig()
