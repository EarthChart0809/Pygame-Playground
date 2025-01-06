import pygame as pg

# PlayerCharacterクラスの定義 [ここから]

class PlayerCharacter:

  # コンストラクタ
  def __init__(self, init_pos, img_path):
    self.pos = pg.Vector2(init_pos)
    self.size = pg.Vector2(48, 64)
    self.dir = 1
    img_raw = pg.image.load(img_path)
    self.__img_arr = []
    for i in range(4):
      self.__img_arr.append([])
      for j in range(3):
        p = pg.Vector2(24 * j, 32 * i)
        tmp = img_raw.subsurface(pg.Rect(p, (24, 32)))
        tmp = pg.transform.scale(tmp, self.size)
        self.__img_arr[i].append(tmp)
      self.__img_arr[i].append(self.__img_arr[i][1])

    # rect属性を追加
    self.image = self.__img_arr[0][0]  # 初期の画像
    self.rect = self.image.get_rect()
    self.rect.topleft = self.get_dp()
    self.invincible = False  # 無敵状態のフラグ
    self.invincible_timer = 0  # 無敵状態の残り時間（フレーム数）

  def turn_to(self, dir):
    self.dir = dir

  def move_to(self, vec):
    self.pos += vec

  def get_dp(self):
    return self.pos * 32 - pg.Vector2(0, 24)

  def get_img(self, frame):
    return self.__img_arr[self.dir][frame // 6 % 4]

  def update(self):
      # 無敵状態のタイマーを減少
      if self.invincible:
          self.invincible_timer -= 1
          if self.invincible_timer <= 0:
              self.invincible = False  # 無敵状態解除

  def draw(self, surface):
      if self.invincible and pg.time.get_ticks() % 500 < 250:  # 500ms間隔で点滅
          return  # 点滅中は描画しない
      surface.blit(self.image, self.rect)

# PlayerCharacterクラスの定義 [ここまで]
