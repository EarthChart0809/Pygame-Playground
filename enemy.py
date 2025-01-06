import pygame as pg
import random

class EnemyCharacter:
    def __init__(self, init_pos, img_path):
        self.pos = pg.Vector2(init_pos)
        self.size = pg.Vector2(48, 64)
        self.dir = 2  # 方向: 0=上, 1=右, 2=下, 3=左
        self.move_speed = 0.25
        self.change_direction_timer = 0  # ランダム移動用のタイマー
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

    def is_on_ground(self, stage_data):
      """
      現在の位置の下に地面があるかを判定。
      """
      tile_x = int(self.pos.x)
      tile_y = int(self.pos.y + 1)  # 下のタイルを確認
      if 0 <= tile_y < len(stage_data) and 0 <= tile_x < len(stage_data[0]):
        return stage_data[tile_y][tile_x] == "="  # 地面の記号
      return False

    def move(self, player_pos, stage_data):
      """
      敵の移動処理。
      """
      directions = {
          0: (0, -self.move_speed),  # 上
          1: (self.move_speed, 0),  # 右
          2: (0, self.move_speed),  # 下
          3: (-self.move_speed, 0),  # 左
      }

      if not self.is_on_ground(stage_data):
        # 地面がない場合は方向を変える
        self.dir = (self.dir + 2) % 4  # 反対方向に切り替え
      else:
        dx, dy = directions[self.dir]
        new_x = self.pos.x + dx
        new_y = self.pos.y + dy

        if not self.is_obstacle(new_x, new_y, stage_data):
            self.pos.x = new_x
            self.pos.y = new_y
        else:
            # 障害物がある場合は方向をランダムに変更
            self.dir = random.choice([0, 1, 2, 3])

    def move_toward(self, player_pos, stage_data):
      # プレイヤーの現在位置と敵の位置をもとに移動処理
      direction = player_pos - self.pos  # プレイヤーへの方向を計算
      direction = direction.normalize()  # ベクトルの正規化
      new_pos = self.pos + direction  # 新しい位置を計算

      # 新しい位置が移動可能かを確認（例：壁や障害物がないか）
      if stage_data[int(new_pos.y)][int(new_pos.x)] != "#":  # "#"は壁
        self.pos = new_pos  # 移動可能なら新しい位置に更新

    def is_obstacle(self, x, y, stage_data):
        """
        指定座標が障害物かどうかを判定。
        """
        tile_x = int(x)
        tile_y = int(y)
        if stage_data[tile_y][tile_x] in ["#", "="]:  # 壁や障害物の記号
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
