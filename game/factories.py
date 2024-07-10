from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List

from game.units import Unit, Character, Tile, Terrain


class UnitType(Enum):
    CHARACTER = 1
    TERRAIN = 2


class GameFactory(metaclass=ABCMeta):

    @abstractmethod
    def create_unit(self, tile: Tile) -> Unit:
        pass

    def generate(self, tiles: List[Tile]) -> List[Unit]:
        return [self.create_unit(tile) for tile in tiles]


class CharacterFactory(GameFactory):

    def create_unit(self, tile: Tile) -> Unit:
        return Character(tile=tile)


class TerrainFactory(GameFactory):

    def create_unit(self, tile: Tile) -> Unit:
        return Terrain(tile=tile)


_character_factory = CharacterFactory()
_terrain_factory = TerrainFactory()


def unit_factory(factory_type: UnitType) -> CharacterFactory | TerrainFactory:
    switcher = {
        UnitType.CHARACTER: _character_factory,
        UnitType.TERRAIN: _terrain_factory
    }
    return switcher.get(factory_type)
