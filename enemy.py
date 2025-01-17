import pygame as pg
from setting import stage_data
from player import PlayerCharacter
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

        #print(f"Enemy initialized at {self.pos}")  # デバッグ用

    def is_on_ground(self):
        """
        現在の位置の下に地面か梯子があるかを判定。
        """
        tile_x = int((self.pos.x  + self.size.x//2)// 32)
        tile_y = int((self.pos.y + self.size.y) // 32)  # 足元のタイルを確認
        #print(f"Checking ground at ({tile_x}, {tile_y})")  # デバッグ用
        # 範囲外チェック
        if 0 <= tile_y < len(stage_data) and 0 <= tile_x < len(stage_data[0]):
            return stage_data[tile_y][tile_x] in ["=", "L"]  # 地面または梯子
        return False

    def move(self, player_pos, stage_data,map_size):
        """
        敵の移動処理。
        """
        if self.is_on_ladder:
          self.move_on_ladder(player_pos, stage_data, map_size)
        elif self.is_chasing_player:
          self.chase_player(player_pos, stage_data, map_size)
        else:  # ランダム移動
          self.random_move(stage_data, map_size)

        # 新しい位置を反映
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
          
    def move_toward(self,player_pos,ladder_rect=None):
      """
      プレイヤーの現在位置と敵の位置をもとに移動処理。
      ただし、移動先が地面または梯子がある場合にのみ移動する。
      """
      # プレイヤーの位置と敵の位置の差を求める
      direction = player_pos - self.pos
      move_vector = pg.Vector2(0, 0)

      # x方向の移動
      if direction.x > 0:
        move_vector.x = self.move_speed
      elif direction.x < 0:
        move_vector.x = -self.move_speed

      # y方向の移動
      if direction.y > 0:
        move_vector.y = self.move_speed
      elif direction.y < 0:
        move_vector.y = -self.move_speed

      # 移動先の計算
      new_x = self.pos.x + move_vector.x
      new_y = self.pos.y + move_vector.y

      # 移動先に障害物がない場合のみ移動
      if not self.is_obstacle(new_x, self.pos.y) and self.is_on_ground():
        self.pos.x = new_x
      elif not self.is_obstacle(self.pos.x, new_y) and self.is_on_ground():
        self.pos.y = new_y

      # 新しい位置を反映
      self.rect.topleft = self.get_dp()
    
    def is_obstacle(self, x, y):
        """
        指定座標が障害物かどうかを判定。
        """
        tile_x = int(x//32)
        tile_y = int(y//32)
        #print(f"Checking obstacle at ({tile_x}, {tile_y})")  # デバッグ用
        if tile_y < 0 or tile_y >= len(stage_data) or tile_x < 0 or tile_x >= len(stage_data[0]):
          return True  # 範囲外は障害物とみなす
        if stage_data[tile_y][tile_x] in ["#", "="]:  # 壁や地面の記号
            return True
        return False

    def is_on_ladder(self):
      """
      現在の位置が梯子上かどうかを判定。
      """
      tile_x = int(self.rect.centerx // 32)
      tile_y = int(self.rect.centery // 32)
      if 0 <= tile_y < len(stage_data) and 0 <= tile_x < len(stage_data[0]):
        return stage_data[tile_y][tile_x] == "L"
      return False

    def move_on_ladder(self, player_pos, stage_data, map_size):
        # タイルの幅と高さを分解
        tile_width, tile_height = map_size
    
        # 敵の現在位置
        current_tile_x = int(self.rect.centerx // tile_width)
        current_tile_y = int(self.rect.centery // tile_height)

        # プレイヤーの位置
        player_tile_x = int(player_pos[0] // tile_width)
        player_tile_y = int(player_pos[1] // tile_height)

        # ログ: 現在位置とプレイヤー位置
        print(f"Ladder detected. Current tile: ({current_tile_x}, {current_tile_y}), Player tile: ({player_tile_x}, {player_tile_y})")
        
        # 範囲外チェック
        if not (0 <= current_tile_x < len(stage_data[0])) or not (0 <= current_tile_y < len(stage_data)):
          print(f"Out of bounds: ({current_tile_x}, {current_tile_y})")
          return

        # 現在のタイルが梯子か確認
        current_tile = stage_data[current_tile_y][current_tile_x]
        if current_tile != "L":
          print(f"Enemy is not on a ladder: Tile data at ({current_tile_x}, {current_tile_y}) = {current_tile}")
          return

        # プレイヤーの位置による上下移動
        if player_tile_y < current_tile_y:  # プレイヤーが上にいる場合
          target_tile_y = current_tile_y - 1
          direction = "up"
        elif player_tile_y > current_tile_y:  # プレイヤーが下にいる場合
          target_tile_y = current_tile_y + 1
          direction = "down"
        else:
          # 同じタイル上ならその場で待機
          print("Player is on the same tile as the enemy. No movement required.")
          return

        # 範囲外チェック
        if not (0 <= target_tile_y < len(stage_data)):
          print(f"Target tile out of bounds: ({current_tile_x}, {target_tile_y})")
          return

        # 次のタイル情報を確認
        next_tile = stage_data[target_tile_y][current_tile_x]
        print(f"Tile data at ({current_tile_x}, {target_tile_y}): {next_tile}")

        # 移動処理: 次のタイルが梯子の場合
        if next_tile == "L":
          self.pos.y += (target_tile_y - current_tile_y) * tile_height
          print(
            f"Moved enemy {direction} to ({current_tile_x}, {target_tile_y}).")
        else:print(f"No ladder found at ({current_tile_x}, {target_tile_y}). Enemy did not move.")
    
    def move_up_ladder(self, ladder_rect):
        # 梯子に接触したら、梯子上を移動するロジック
        if self.rect.colliderect(ladder_rect):
            print(f"敵が梯子に接触しました: {ladder_rect}")
            self.rect.y -= 2  # 梯子を登るためにy座標を減らす
        else:
            # 梯子から外れている場合、何もしない
            print("梯子に接触していません")

    def adjust_to_ground(self):
      """
      敵が地面に着地するように位置を調整。
      """
      while not self.is_on_ground():
        self.pos.y += 1  # 少しずつ下方向に移動
        if self.pos.y > len(stage_data) * 32:  # ステージ範囲を超えた場合の安全策
            break
      self.rect.topleft = self.get_dp()  # 位置を更新

    def is_chasing_player(self,player_pos):
      """
      プレイヤーが追尾範囲内にいるかを判定。
      """
      player_distance = self.pos.distance_to(player_pos)
      return player_distance < 300  # 追尾範囲を300に設定

    def chase_player(self, player_pos, stage_data, map_size):
      """
      プレイヤーを追尾する処理。
      """
      direction = player_pos - self.pos
      dx, dy = 0, 0

      # X方向の追尾
      if direction.x > 0:
        dx = self.move_speed
      elif direction.x < 0:
        dx = -self.move_speed

      # Y方向の追尾
      if direction.y > 0:
        dy = self.move_speed
      elif direction.y < 0:
        dy = -self.move_speed

      new_x = self.pos.x + dx
      new_y = self.pos.y + dy

      # 障害物チェック
      if not self.is_obstacle(new_x, self.pos.y) and self.is_on_ground():
        self.pos.x = new_x
      elif not self.is_obstacle(self.pos.x, new_y) and self.is_on_ground():
        self.pos.y = new_y

      # 新しい位置を反映
      self.rect.topleft = self.get_dp()

    def random_move(self, stage_data, map_size):
      """
      ランダム移動処理。
      """
      directions = {
        0: (0, -2),  # 上
        1: (0, 2),   # 下
        2: (-2, 0),  # 左
        3: (2, 0)    # 右
      }

      if self.change_direction_timer > 0:
        self.change_direction_timer -= 1
      else:
        possible_directions = []
        for d, (dx, dy) in directions.items():
            new_x = self.pos.x + dx
            new_y = self.pos.y + dy
            if not self.is_obstacle(new_x, new_y) and self.is_on_ground():
                possible_directions.append(d)
        if possible_directions:
            self.dir = random.choice(possible_directions)
        self.change_direction_timer = random.randint(30, 120)

      dx, dy = directions[self.dir]
      if not self.is_obstacle(self.pos.x + dx, self.pos.y):
        self.pos.x += dx
      elif not self.is_obstacle(self.pos.x, self.pos.y + dy):
        self.pos.y += dy

    def update(self,player_rect,stage_data,map_size):
        """
        敵の描画と位置を更新。
        """
        # 地面に吸着させる
        self.adjust_to_ground()
        frame = pg.time.get_ticks() // 100
        self.image = self.get_img(frame)
        self.rect.topleft = self.get_dp()  # 新しい位置を反映
        
        # タイルの幅と高さを分解
        tile_width, tile_height = map_size

        # 敵の現在位置をグリッド座標に変換
        grid_x = int(self.rect.centerx // tile_width)
        grid_y = int(self.rect.centery // tile_height)

        # ステージデータ範囲外を防ぐチェック
        if 0 <= grid_x < len(stage_data[0]) and 0 <= grid_y < len(stage_data):
          if stage_data[grid_y][grid_x] == "L":  # 梯子の判定
            self.move_on_ladder(player_rect.center, stage_data, map_size)
          else:
            # 通常のプレイヤー追尾ロジック
            self.move_toward(player_rect.topleft)

    def get_dp(self):
        dp = (self.pos.x, self.pos.y)
        #print(f"Drawing position: {dp}")  # デバッグ用
        return dp

    def get_img(self, frame):
        return self.__img_arr[self.dir][frame // 6 % 4]

# EnemyCharacterクラスの定義 [ここまで]
