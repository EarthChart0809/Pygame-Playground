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

  def turn_to(self, dir):
    self.dir = dir

  def move_to(self, vec):
    self.pos += vec

  def get_dp(self):
    return self.pos * 32 - pg.Vector2(0, 24)

  def get_img(self, frame):
    return self.__img_arr[self.dir][frame // 6 % 4]

# PlayerCharacterクラスの定義 [ここまで]

class EnemyCharacter:
    def __init__(self, init_pos, img_path):
        self.pos = pg.Vector2(init_pos)
        self.size = pg.Vector2(48, 64)
        self.dir = 2
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

    def move_toward(self, player_pos, stage_data, directions):
        """
        指定されたアルゴリズムで移動。
        """
        # 1. 同じ高さにいて、地続きの場合
        if self.pos.y == player_pos.y:
            step = 1 if self.pos.x < player_pos.x else -1
            for x in range(int(self.pos.x), int(player_pos.x), step):
                if stage_data[int(self.pos.y)][x] == "#":
                    break
            else:
                self.pos.x += step
                self.dir = 1 if step > 0 else 3
                return

        # 2. プレイヤーのいる高さに行ける場合
        diff_y = int(player_pos.y - self.pos.y)
        step_y = 1 if diff_y > 0 else -1
        if stage_data[int(self.pos.y + step_y)][int(self.pos.x)] not in ["#", "="]:
            self.pos.y += step_y
            self.dir = 2 if step_y > 0 else 0
            return

        # 3. その他、優先順位の高い移動
        for move, vec in directions.items():
            new_pos = self.pos + vec
            if stage_data[int(new_pos.y)][int(new_pos.x)] != "#":
                self.pos += vec
                self.dir = move
                return

    def get_dp(self):
        return self.pos * 32 - pg.Vector2(0, 24)

    def get_img(self, frame):
        return self.__img_arr[self.dir][frame // 6 % 4]

# EnemyCharacterクラスの定義 [ここまで]

wall_img = pg.image.load('./data/img/wall.png')
ladder_img = pg.image.load('./data/img/ladder.png')
rope_img = pg.image.load('./data/img/rope.png')
ground_img = pg.image.load('./data/img/ground.png')

def draw_map(screen, stage_data, chip_s):
    for y, row in enumerate(stage_data):
        for x, cell in enumerate(row):
            rect = (x * chip_s, y * chip_s, chip_s, chip_s)
            if cell == "#":  # 壁
                screen.blit(wall_img, rect)  # 壁の画像を描画
            elif cell == "L":  # 階段
                screen.blit(ladder_img, rect)  # 階段の画像を描画
            elif cell == "-":  # ロープ
                screen.blit(rope_img, rect)  # ロープの画像を描画
            elif cell == "=":  # 地面
                screen.blit(ground_img, rect)  # 地面の画像を描画

def destroy_tile_by_key(player_pos, direction, stage_data, broken_tiles, respawn_time=300):
    """
    プレイヤーの左右の地面を壊す処理。
    direction: -1 (左) または 1 (右)
    broken_tiles: 壊れたタイルを記録するリスト
    respawn_time: 復活までのフレーム数
    """
    tile_pos = pg.Vector2(player_pos.x + direction,
                          player_pos.y + 1)  # プレイヤーの真下を確認
    x, y = int(tile_pos.x), int(tile_pos.y)

    # タイルが範囲内か確認
    if 0 <= y < len(stage_data) and 0 <= x < len(stage_data[0]):
        # 壊せるのは地面 ("=") のみ
        if stage_data[y][x] == "=":
            # 地面を壊して空白に変更
            stage_data[y] = stage_data[y][:x] + " " + stage_data[y][x + 1:]
            # 壊れたタイルの情報を記録（復活時間を設定）
            broken_tiles.append((x, y, respawn_time))

#ステージ要素
stage_data = [
    "#################",
    "#               #",
    "#   L===========#",
    "#   L           #",
    "#   L           #",
    "#===#===========#",
    "#################",
]

# アイテムの位置リスト
items = [(3, 4), (6, 7)]  

# 壊れたタイルを記録するリスト
broken_tiles = []  # [(x, y, remaining_time), ...]

# PlayerCharacterクラスの定義 [ここまで]

def main():

  # 初期化処理
  chip_s = 32  # マップチップの基本サイズ
  map_s = pg.Vector2(16, 9)  # マップの横・縦の配置数

  pg.init()
  pg.display.set_caption('Load Runner')
  disp_w = int(chip_s * map_s.x)
  disp_h = int(chip_s * map_s.y)
  screen = pg.display.set_mode((disp_w, disp_h))
  clock = pg.time.Clock()
  font = pg.font.Font(None, 15)
  frame = 0
  exit_flag = False
  exit_code = '000'

  # グリッド設定
  grid_c = '#dddddd'  # 薄いグレー

  # 自キャラ移動関連
  cmd_move = -1  # 移動コマンドの管理変数
  m_vec = [
      pg.Vector2(0, -1),
      pg.Vector2(1, 0),
      pg.Vector2(0, 1),
      pg.Vector2(-1, 0)
  ]  # 移動コマンドに対応したXYの移動量

  # 自キャラの生成・初期化
  reimu = PlayerCharacter((2, 3), './data/img/reimu.png')
  enemy_list = [
      EnemyCharacter((4, 2), './data/img/enemy.png'),
      EnemyCharacter((6, 4), './data/img/enemy.png'),
  ]

  wall_img = pg.image.load('./data/img/wall.png')
  ladder_img = pg.image.load('./data/img/ladder.png')
  rope_img = pg.image.load('./data/img/rope.png')
  ground_img = pg.image.load('./data/img/ground.png')
  
  
  wall_img = pg.transform.scale(wall_img, (chip_s, chip_s))
  ladder_img = pg.transform.scale(ladder_img, (chip_s, chip_s))
  rope_img = pg.transform.scale(rope_img, (chip_s, chip_s))
  ground_img = pg.transform.scale(ground_img, (chip_s, chip_s))  # 必要に応じてサイズ調整


  # ゲームループ
  while not exit_flag:

    # システムイベントの検出
    cmd_move = -1
    for event in pg.event.get():
      if event.type == pg.QUIT:  # ウィンドウ[X]の押下
        exit_flag = True
        exit_code = '001'
      # 移動操作の「キー入力」の受け取り処理
      if event.type == pg.KEYDOWN:
        if event.key == pg.K_UP:
          cmd_move = 0
        elif event.key == pg.K_RIGHT:
          cmd_move = 1
        elif event.key == pg.K_DOWN:
          cmd_move = 2
        elif event.key == pg.K_LEFT:
          cmd_move = 3
        elif event.key == pg.K_a:  # Aキーで左側の地面を壊す
          destroy_tile_by_key(reimu.pos, -1, stage_data, broken_tiles)
        elif event.key == pg.K_d:  # Dキーで右側の地面を壊す
          destroy_tile_by_key(reimu.pos, 1, stage_data, broken_tiles)

    # 背景描画
    screen.fill(pg.Color('WHITE'))

    # グリッド
    for x in range(0, disp_w, chip_s):  # 縦線
      pg.draw.line(screen, grid_c, (x, 0), (x, disp_h))
    for y in range(0, disp_h, chip_s):  # 横線
      pg.draw.line(screen, grid_c, (0, y), (disp_w, y))

    # ステージデータの描画
    draw_map(screen, stage_data, chip_s)

    # アイテムの描画
    for item in items:
      pg.draw.circle(screen, pg.Color(
        'YELLOW'), (item[0] * chip_s + chip_s // 2, item[1] * chip_s + chip_s // 2), chip_s // 4)

    if cmd_move != -1:  # 有効な移動コマンドがある場合
      af_pos = reimu.pos + m_vec[cmd_move]  # 仮の移動先座標

    # 上下移動の制約
      if cmd_move in [0, 2]:  # 上または下
        # 現在の位置が梯子上、または移動先が梯子の場合に移動を許可
        if stage_data[int(reimu.pos.y)][int(reimu.pos.x)] == "L" or \
          stage_data[int(af_pos.y)][int(reimu.pos.x)] == "L":
            if 0 <= af_pos.y < map_s.y:  # 範囲内チェック
                reimu.move_to(m_vec[cmd_move])

    # 左右移動の制約
      elif cmd_move in [1, 3]:  # 右または左
        # 地面または梯子の上でのみ左右移動可能
        if stage_data[int(reimu.pos.y) + 1][int(reimu.pos.x)] in ["=", "L"]:
            if 0 <= af_pos.x < map_s.x:  # 範囲内チェック
                if stage_data[int(reimu.pos.y)][int(af_pos.x)] in [" ","L", "-", "="]:
                    reimu.move_to(m_vec[cmd_move])

    # 重力処理
    af_pos = reimu.pos + pg.Vector2(0, 1)  # 下の位置を確認
    if 0 <= af_pos.y < map_s.y:  # 範囲内チェック
      if stage_data[int(af_pos.y)][int(reimu.pos.x)] == " ":  # 下が空間の場合
        reimu.move_to(pg.Vector2(0, 1))  # 自動で落下


    # アイテムの収集判定
    player_tile_pos = (int(reimu.pos.x), int(reimu.pos.y))
    if player_tile_pos in items:
      items.remove(player_tile_pos)  # アイテムを削除

    # 敵の移動処理
    directions = {
      0: pg.Vector2(0, -1),  # 上
      1: pg.Vector2(1, 0),   # 右
      2: pg.Vector2(0, 1),   # 下
      3: pg.Vector2(-1, 0),  # 左
  }

    # 壊れたタイルの復活処理
    for i, (x, y, time) in enumerate(broken_tiles):
        if time > 0:
            broken_tiles[i] = (x, y, time - 1)  # 時間を1減らす
        else:
            # タイルを復活させる
            stage_data[y] = stage_data[y][:x] + "=" + stage_data[y][x + 1:]
            broken_tiles.pop(i)  # 復活済みタイルをリストから削除

    for enemy in enemy_list:
      enemy.move_toward(reimu.pos, stage_data, directions)

    # 自キャラの描画
    screen.blit(reimu.get_img(frame), reimu.get_dp())

    # 敵キャラクターの描画
    for enemy in enemy_list:
      screen.blit(enemy.get_img(frame), enemy.get_dp())

    # フレームカウンタの描画
    frame += 1
    frm_str = f'{frame:05}'
    screen.blit(font.render(frm_str, True, 'BLACK'), (10, 10))
    screen.blit(font.render(f'{reimu.pos}', True, 'BLACK'), (10, 20))

    # 画面の更新と同期
    pg.display.update()
    clock.tick(30)

  # ゲームループ [ここまで]
  pg.quit()
  return exit_code
  
if __name__ == "__main__":
  code = main()
  print(f'プログラムを「コード{code}」で終了しました。')