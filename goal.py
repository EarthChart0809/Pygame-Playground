import pygame as pg

class Goal(pg.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pg.Surface(size)
        self.image.fill((0, 255, 0))  # 緑色のゴール
        self.rect = self.image.get_rect(topleft=pos)
