import pygame as pg

class Goal(pg.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pg.Surface(size)
        self.image = pg.image.load("./data/img/goal.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
