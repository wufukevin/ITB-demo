from collections import deque
from abc import abstractmethod

from config.loader import app_config


class Action:
    def __init__(self):
        pass

    @abstractmethod
    def reachable_tiles(self):
        pass


class Move(Action):
    def __init__(self, distance: int):
        super().__init__()
        self.distance = distance

    def reachable_tiles(self, start: 'Tile', map: 'Map'):
        from game.units import Tile
        for x in range(start.x - self.distance, start.x + self.distance + 1):
            if x < 0 or x >= app_config.game.tiles.width:
                continue
            for y in range(start.y - self.distance, start.y + self.distance + 1):
                if y < 0 or y >= app_config.game.tiles.height:
                    continue
                if abs(x - start.x) + abs(y - start.y) > self.distance:
                    continue
                unit = map[(x, y)]
                if unit is None or not unit.is_block:
                    yield Tile(x=x, y=y)

    def find_path(self, start: 'Tile', map: 'Map'):
        queue = deque([(start, 0, [start])])
        visited = {start}
        reachable_tiles = list()

        while queue:
            current_tile, distance, path = queue.popleft()

            if distance <= self.distance:
                reachable_tiles.append((current_tile, path))

            if distance < self.distance:
                for neighbor in current_tile.neighbor_tiles:
                    unit = map[neighbor]
                    if neighbor in visited:
                        continue
                    if unit is None or not unit.is_block:
                        queue.append((neighbor, distance + 1, path + [neighbor]))
                        visited.add(neighbor)
        return reachable_tiles


class RangeAttack(Action):
    def __init__(self, distance: int):
        super().__init__()
        self.distance = distance

    def reachable_tiles(self, start: 'Tile', map: 'Map'):
        from game.units import Tile
        for x in range(start.x - self.distance, start.x + self.distance + 1):
            if x < 0 or x >= app_config.game.tiles.width:
                continue
            for y in range(start.y - self.distance, start.y + self.distance + 1):
                if y < 0 or y >= app_config.game.tiles.height:
                    continue
                if abs(x - start.x) + abs(y - start.y) > self.distance:
                    continue
                yield Tile(x=x, y=y)


class LineAttack(Action):
    def __init__(self, distance: int):
        super().__init__()
        self.distance = distance

    def reachable_tiles(self, start: 'Tile', map: 'Map'):
        from game.units import Tile
        for x in range(start.x - self.distance, start.x + self.distance + 1):
            if x < 0 or x >= app_config.game.tiles.width:
                continue
            for y in range(start.y - self.distance, start.y + self.distance + 1):
                if y < 0 or y >= app_config.game.tiles.height:
                    continue
                if x != start.x and y != start.y:
                    continue
                yield Tile(x=x, y=y)
