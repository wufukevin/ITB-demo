import pathlib

from pydantic_yaml import parse_yaml_file_as
from pygame import Vector2

from .model import Config


class AppConfig:
    def __init__(self):
        self.config = parse_yaml_file_as(Config, pathlib.Path(__file__).parent / "config.yaml")
        self.tile_width = self.screen.width / self.game.tiles
        self.tile_height = self.screen.height / self.game.tiles

    def get_tile_rect(self, x, y) -> Vector2:
        """
        get tile rect with tile coordinates, tile coordinates start from (0,0) in the top left corner

        :param x: coordinate x
        :param y: coordinate y
        :return: the screen rect of the tile
        """
        return Vector2(x * self.tile_width, y * self.tile_height)

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
