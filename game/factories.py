import random
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List

from pygame import Color

from game.units import Unit, Character, UnitLayer
from game.tile import Tile
from resource.loader import ImageLoader, background_images, character_images


class UnitType(Enum):
    BACKGROUND = 0
    MOVE_RANGE = 1
    BLOCKER = 2
    CHARACTER = 3


class GameFactory(metaclass=ABCMeta):

    @abstractmethod
    def create_unit(self, tile: Tile) -> Unit:
        pass

    def generate(self, tiles: List[Tile]) -> List[Unit]:
        return [self.create_unit(tile) for tile in tiles]


class BackgroundFactory(GameFactory):

    def create_unit(self, tile: Tile) -> Unit:
        return Unit(tile=tile, image=ImageLoader.random_load(background_images))


class MoveRangeFactory(GameFactory):

    def create_unit(self, tile: Tile) -> Unit:
        return Unit(tile=tile, layer=UnitLayer.MoveRange, bg_color=Color(0, 255, 0, 50))


class CharacterFactory(GameFactory):

    def create_unit(self, tile: Tile) -> Unit:
        return Character(tile=tile, images=[ImageLoader.random_load(character_images)])


class TerrainFactory(GameFactory):

    def create_unit(self, tile: Tile) -> Unit:
        return Unit(tile=tile, image=ImageLoader.random_load(background_images), layer=UnitLayer.Terrain,
                    is_block=random.Random().randint(1, 50) % 2 == 0)


def unit_factory(factory_type: UnitType) -> GameFactory:
    switcher = {
        UnitType.CHARACTER: CharacterFactory(),
        UnitType.BLOCKER: TerrainFactory(),
        UnitType.BACKGROUND: BackgroundFactory(),
        UnitType.MOVE_RANGE: MoveRangeFactory()
    }
    return switcher.get(factory_type)
