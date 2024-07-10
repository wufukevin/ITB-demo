import pathlib
import random
from typing import List

import pygame

__resource_path = pathlib.Path(__file__).parent

__terrains_dir = __resource_path / "terrains"
__characters_dir = __resource_path / "characters"

# get all files in the folder
background_images = [image for image in __terrains_dir.glob("*.png")]
character_images = [image for image in __characters_dir.glob("*.png")]


class ImageLoader:

    @staticmethod
    def random_load(image_src) -> pygame.surface.Surface:
        return ImageLoader.load_image(random.choice(image_src))

    @staticmethod
    def load_image(image_path: pathlib.Path) -> pygame.surface.Surface:
        return pygame.image.load(image_path).convert_alpha()

    @staticmethod
    def load_images(image_paths: List[pathlib.Path]) -> List[pygame.surface.Surface]:
        return [pygame.image.load(path).convert_alpha() for path in image_paths]
