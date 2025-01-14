import pygame as pg
from setting import stage_data
import random

class EnemyCharacter:
    def __init__(self, init_pos, img_path):
        self.pos = pg.Vector2(init_pos)
        self.size = pg.Vector2(48, 64)
        self.dir = random.choice([0,1,2,3])  # 方向: 0=上, 1=右, 2=下, 3=左
        self.move_speed = 0.25
        self.change_direction_timer = random.randint(30,120)  # ランダム移動用のタイマー
        # 画像読み込み
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

        self.image = self.__img_arr[0][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.get_dp()

    def is_on_ground(self):
        """
        現在の位置の下に地面か梯子があるかを判定。
        """
        tile_x = int(self.pos.x // 32)
        tile_y = int((self.pos.y + self.size.y) // 32)  # 足元のタイルを確認

        # 範囲外チェック
        if 0 <= tile_y < len(stage_data) and 0 <= tile_x < len(stage_data[0]):
            return stage_data[tile_y][tile_x] in ["=", "L"]  # 地面または梯子
        return False

    def move(self, reimu, stage_data):
        print(f"Timer: {self.change_direction_timer}, Direction: {self.dir}")
        """
        敵の移動処理。
        """
        # タイマー減少
        if self.change_direction_timer > 0:
            self.change_direction_timer -= 1
        else:
            # 新しい方向を決定
            directions = {
                0: (0, -2),  # 上
                1: (0, 2),   # 下
                2: (-2, 0),  # 左
                3: (2, 0)    # 右
            }
            possible_directions = []
            for d, (dx, dy) in directions.items():
                new_x = self.pos.x + dx
                new_y = self.pos.y + dy
                if not self.is_obstacle(new_x, new_y):
                    possible_directions.append(d)
            if possible_directions:
                self.dir = random.choice(possible_directions)
            self.change_direction_timer = random.randint(30, 120)

        # 現在の方向に移動
        dx, dy = directions[self.dir]
        if not self.is_obstacle(self.pos.x + dx, self.pos.y + dy):
            self.pos.x += dx
            self.pos.y += dy
            self.rect.topleft = (int(self.pos.x), int(self.pos.y))


    def move_toward(self, reimu,stage_data,ladder_rect=None):
      """
      プレイヤーの現在位置と敵の位置をもとに移動処理。
      ただし、移動先が地面または梯子がある場合にのみ移動する。
      """
      # プレイヤーの位置と敵の位置の差を求める
      direction = reimu - self.pos
      dx, dy = 0, 0

      if direction.x > 0:
            dx = self.move_speed
      elif direction.x < 0:
            dx = -self.move_speed

      if direction.y > 0:
            dy = self.move_speed
      elif direction.y < 0:
            dy = -self.move_speed

      new_x = self.pos.x + dx
      new_y = self.pos.y + dy

      if not self.is_obstacle(new_x, self.pos.y) and self.is_on_ground():
            self.pos.x = new_x
      elif not self.is_obstacle(self.pos.x, new_y) and self.is_on_ground():
            self.pos.y = new_y

      self.rect.topleft = self.get_dp()

    def is_obstacle(self, x, y):
        """
        指定座標が障害物かどうかを判定。
        """
        tile_x = int(x//32)
        tile_y = int(y//32)
        if tile_y < 0 or tile_y >= len(stage_data) or tile_x < 0 or tile_x >= len(stage_data[0]):
          return True  # 範囲外は障害物とみなす
        if stage_data[tile_y][tile_x] in ["#", "="]:  # 壁や地面の記号
            return True
        return False

    def move_up_ladder(self, ladder_rect):
        # 梯子に接触したら、梯子上を移動するロジック
        if self.rect.colliderect(ladder_rect):
            self.rect.y -= 2  # 梯子を登るためにy座標を減らす

    def update(self):
        """
        敵の描画と位置を更新。
        """
        self.rect.topleft = self.get_dp()  # 新しい位置を反映
        frame = pg.time.get_ticks() // 100
        self.image = self.get_img(frame)

    def get_dp(self):
        return (self.pos.x * 48, self.pos.y * 64)

    def get_img(self, frame):
        return self.__img_arr[self.dir][frame // 6 % 4]

# EnemyCharacterクラスの定義 [ここまで]
