import pygame as pg

class Goal(pg.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pg.image.load("./data/img/goal.png").convert_alpha()
        self.image = pg.transform.scale(self.image, size)  # 画像を指定したサイズにスケール
        self.rect = self.image.get_rect(topleft=pos)
