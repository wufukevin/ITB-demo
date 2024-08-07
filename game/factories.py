from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List

from game.units import Unit, Character, Terrain, UnitLayer, Tile
from resource.loader import ImageLoader, background_images, character_images


class UnitType(Enum):
    BACKGROUND = 0
    MOVE_RANGE = 1
    TERRAIN = 2
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
        return Unit(tile=tile, layer=UnitLayer.MoveRange)


class CharacterFactory(GameFactory):

    def create_unit(self, tile: Tile) -> Unit:
        return Character(tile=tile, image=ImageLoader.random_load(character_images))


class TerrainFactory(GameFactory):

    def create_unit(self, tile: Tile) -> Unit:
        return Terrain(tile=tile, image=ImageLoader.random_load(background_images))


def unit_factory(factory_type: UnitType) -> GameFactory:
    switcher = {
        UnitType.CHARACTER: CharacterFactory(),
        UnitType.TERRAIN: TerrainFactory(),
        UnitType.BACKGROUND: BackgroundFactory(),
        UnitType.MOVE_RANGE: MoveRangeFactory()
    }
    return switcher.get(factory_type)
