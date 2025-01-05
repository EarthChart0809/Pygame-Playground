import pygame as pg
import clock
import time

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
        # rect属性を追加
        self.image = self.__img_arr[0][0]  # 初期の画像
        self.rect = self.image.get_rect()
        self.rect.topleft = self.get_dp()

    def move_toward(self, player_pos, stage_data, directions):
        """
        指定されたアルゴリズムで移動。
        """
        # 移動速度の調整
        move_speed = 0.05  # 0.5にすると半分の速さで移動

        # 1. 同じ高さにいて、地続きの場合
        if self.pos.y == player_pos.y:
            step = move_speed if self.pos.x < player_pos.x else -move_speed
            if step != 0:
              x = self.pos.x
              while (step > 0 and x < player_pos.x) or (step < 0 and x > player_pos.x):
                if stage_data[int(self.pos.y)][int(x)] == "#":
                    break
                else:
                    x += step
                    self.pos.x = x
                    self.dir = 1 if step > 0 else 3
              return

        # 2. プレイヤーのいる高さに行ける場合
        diff_y = int(player_pos.y - self.pos.y)
        step_y = move_speed if diff_y > 0 else - move_speed
        if stage_data[int(self.pos.y + step_y)][int(self.pos.x)] not in ["#", "="]:
            self.pos.y += step_y
            self.dir = 2 if step_y > 0 else 0
            return

        # 3. その他、優先順位の高い移動
        for move, vec in directions.items():
            new_pos = self.pos + vec * move_speed
            if stage_data[int(new_pos.y)][int(new_pos.x)] != "#":
                self.pos += vec * move_speed
                self.dir = move
                return

    def get_dp(self):
        return self.pos * 32 - pg.Vector2(0, 24)

    def get_img(self, frame):
        return self.__img_arr[self.dir][frame // 6 % 4]

# EnemyCharacterクラスの定義 [ここまで]

class Goal(pg.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pg.Surface(size)
        self.image.fill((0, 255, 0))  # 緑色のゴール
        self.rect = self.image.get_rect(topleft=pos)

# 画像の読み込み関数
def load_image(path, size=None):
    try:
        img = pg.image.load(path)
        if size:
            img = pg.transform.scale(img, size)
        return img
    except pg.error as e:
        print(f"Error loading image {path}: {e}")
        return None

# 画像の読み込み
wall_img = load_image('./data/img/wall.png', (32, 32))  # サイズを変更して読み込む
ladder_img = load_image('./data/img/ladder.png', (32, 32))
rope_img = load_image('./data/img/rope.png', (32, 32))
ground_img = load_image('./data/img/ground.png', (32, 32))
life_icon = load_image('./data/img/life_icon.png',(32, 32))  

# Pygameの初期化
pg.init()
screen = pg.display.set_mode((800, 600))
pg.display.set_caption("Load Runner")
clock = pg.time.Clock()
pg.font.init()

# プレイヤー初期設定
player_pos = [400, 300]

# フォントを定義 (デフォルトフォント、サイズ36)
font = pg.font.Font(None, 36)

# グラフィック設定
player_life = 3  # プレイヤーの残りライフ

# ゲーム内目標 (例: ゴールまであと3つ)
goal_count = 3

# 定数
MAX_LIVES = 3
GOAL_ITEM_COUNT = 10
SCREEN_WIDTH = 800  # 画面の幅
SCREEN_HEIGHT = 600  # 画面の高さ

def draw_score(surface, score):
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # 白い文字
    surface.blit(score_text, (10, 10))  # 画面左上に表示

def handle_collisions(player_rect, goals, score):
    for goal in goals:
        if player_rect.colliderect(goal.rect):  # 矩形の衝突判定
            goals.remove(goal)  # ゴールを削除
            score += 10  # スコア加算
            print("ゴール達成！")  # デバッグ用出力
    return score

# ゲーム内での目標進捗更新処理
def handle_goal_progress(player_pos, goal_positions):
    collected_goals = 0
    for goal in goal_positions:
        if player_pos == goal:
            collected_goals += 1
    return collected_goals

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

# 画面更新の際、情報を固定位置に描画する関数を作成
def draw_fixed_info(surface, score, life, goal_count):
  # ライフ表示（左上）
  life_text_color = (255, 0, 0) if life <= 1 else (255, 255, 255)
  life_text = font.render(f"Lives:", True, life_text_color)
  surface.blit(life_text, (10, 10))

  # ハートアイコンの色の変化
  for i in range(life):
    surface.blit(life_icon, (10 + i * 30, 40))  # ハートアイコンを描画（位置調整）

  # スコア表示（右上）
  score_text = font.render(f"Score: {score}", True, (255, 255, 255))
  surface.blit(score_text, (surface.get_width() - 150, 10))

  # 目標表示（右下）
  goal_text = font.render(f"Goal: {goal_count}", True, (255, 255, 255))
  surface.blit(goal_text, (surface.get_width() - 150, surface.get_height() - 30))

  # ゴール進捗バー（画面上部）
  progress_width = 200  # バーの幅
  progress_height = 20  # バーの高さ
  progress_bg_color = (100, 100, 100)  # 背景色（灰色）
  progress_color = (0, 255, 0)  # 進捗色（緑）

  # ゴール進捗バーの描画
  progress_bar_rect = pg.Rect(surface.get_width() // 2 - progress_width // 2, 30, progress_width, progress_height)
  pg.draw.rect(surface, progress_bg_color, progress_bar_rect)  # 背景のバー
  progress_fill_width = (goal_count / 10) * progress_width  # 目標10個収集
  pg.draw.rect(surface, progress_color, pg.Rect(progress_bar_rect.x,
                                                  progress_bar_rect.y, progress_fill_width, progress_bar_rect.height))  # 進捗のバー

# ゴール収集時の処理
def check_goal_collision(player_rect, goals, goal_count):
    # ゴールのリストをループ
    for goal in list(goals):  # Group をリストに変換してループ
        if player_rect.colliderect(goal.rect):  # 衝突を確認
            goals.remove(goal)  # ゴールをグループから削除
            goal_count += 1  # ゴールカウントを増やす
    return goal_count

# ゲームオーバー/クリアメッセージ表示関数
def display_message(message, color, y_offset=0):
    text = font.render(message, True, color)
    text_rect = text.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(text, text_rect)

# 新しいステージへの進行
def next_stage():
    global stage, collected_items
    stage += 1
    collected_items = 0
    # 追加のステージ設定があればここで設定
    print(f"次のステージ {stage}へ進行")

# 進捗バーの表示
def draw_progress_bar():
    progress_width = 300
    progress_height = 20
    filled_width = int(
        (goal_items_collected / GOAL_ITEM_COUNT) * progress_width)
    pg.draw.rect(screen, (200, 200, 200), (screen.get_width(
    ) - 310, screen.get_height() - 30, progress_width, progress_height))
    pg.draw.rect(screen, (0, 255, 0), (screen.get_width(
    ) - 310, screen.get_height() - 30, filled_width, progress_height))

# ゲームクリアの判定
def check_game_clear():
    global goal_items_collected
    if goal_items_collected >= GOAL_ITEM_COUNT:
        return True
    return False

#ステージ要素
stage_data = [
    "###############################",
    "#                             #",
    "#     L=============          #",
    "#     L                       #",
    "#     L                       #",
    "#============L================#",
    "#            L                #",
    "#            L                #",
    "#   =========L================#",
    "###############################",
]

# アイテムの位置リスト
items = [(3, 4), (6, 7)]  

# 壊れたタイルを記録するリスト
broken_tiles = []  # [(x, y, remaining_time), ...]

# ゲーム変数
running = True
game_over = False
player_lives = 3
stage = 1  # 最初のステージ
goal_items_collected = 0
MAX_LIVES = 3
GOAL_ITEM_COUNT = 10
lives = MAX_LIVES


def main():
  global game_over, player_lives, goal_items_collected, stage

  # 初期化処理
  chip_s = 32  # マップチップの基本サイズ
  map_s = pg.Vector2(len(stage_data[0]),len(stage_data))  # マップの横・縦の配置数

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

#ステージ要素の描画設定
  wall_img = pg.image.load('./data/img/wall.png')
  ladder_img = pg.image.load('./data/img/ladder.png')
  rope_img = pg.image.load('./data/img/rope.png')
  ground_img = pg.image.load('./data/img/ground.png')
  item_icon_img = pg.image.load('./data/img/item_icon.png')
  
  wall_img = pg.transform.scale(wall_img, (chip_s, chip_s))
  ladder_img = pg.transform.scale(ladder_img, (chip_s, chip_s))
  rope_img = pg.transform.scale(rope_img, (chip_s, chip_s))
  ground_img = pg.transform.scale(ground_img, (chip_s, chip_s))  
  item_icon = pg.transform.scale(item_icon_img,(chip_s,chip_s))

  # ゴールの作成とグループ管理
  goals = pg.sprite.Group()
  goal_count = len(goals)  # ゴールの初期数

  # ゴールを特定の位置に配置
  fixed_goal_position = (10 * chip_s, 1 * chip_s)  # 例えば、5列目の1行目（梯子の上）
  fixed_goal = Goal(fixed_goal_position, (30, 30))
  goals.add(fixed_goal)

  # スコアとライフ
  score = 0
  player_lives = 3
  game_clear = False
  game_clear_time = 0

  # ゲームループ
  while not exit_flag:
    # プレイヤーと敵の衝突判定
    for enemy in enemy_list:
      if reimu.rect.colliderect(enemy.rect):  # 矩形の衝突判定
        print("敵にぶつかりました！ゲームオーバー")
        game_over = True
        break

    # 穴に落ちて埋まる判定
    player_x, player_y = int(reimu.pos.x), int(reimu.pos.y)
    if stage_data[player_y + 1][player_x] == "=" and stage_data[player_y][player_x] == "#":
        print("穴に埋まりました！ゲームオーバー")
        game_over = True

    if game_over:
        screen.fill((0, 0, 0))  # 背景を黒にする
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        restart_text = font.render(
            "Press R to Restart or Q to Quit", True, (255, 255, 255))
        screen.blit(game_over_text, (disp_w // 2 - 100, disp_h // 2 - 50))
        screen.blit(restart_text, (disp_w // 2 - 150, disp_h // 2 + 20))
        pg.display.flip()

        # イベント処理 (再スタートまたは終了)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit_flag = True
            if event.type == pg.KEYDOWN:
              if event.key == pg.K_r:  # Rキーで再スタート
                score = 0
                player_lives = MAX_LIVES
                goal_items_collected = 0
                stage = 1  # ステージ1にリセット
                game_over = False
              elif event.key == pg.K_q:  # Qキーで終了
                exit_flag = True
            clock.tick(30)
            continue

    # ゲーム進行
    screen.fill((0, 0, 0))  # 背景の描画
    draw_map(screen, stage_data, chip_s)  # ステージマップを描画
    reimu.rect.topleft = reimu.get_dp()  # プレイヤーの位置を更新
    screen.blit(reimu.get_img(frame), reimu.rect.topleft)  # プレイヤーの画像を描画

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
        elif event.key == pg.K_n and check_game_clear():
          # 次のステージ
          goal_items_collected = 0
          lives = MAX_LIVES
        elif event.key == pg.K_r and check_game_clear():
          # ゲームをリスタート
          goal_items_collected = 0
          lives = MAX_LIVES

    # グリッド
    for x in range(0, disp_w, chip_s):  # 縦線
      pg.draw.line(screen, grid_c, (x, 0), (x, disp_h))
    for y in range(0, disp_h, chip_s):  # 横線
      pg.draw.line(screen, grid_c, (0, y), (disp_w, y))

    # アイテムの描画
    for item in items:
      item_rect = pg.Rect(item[0] * chip_s, item[1] *chip_s, chip_s, chip_s)  # 画像を描画する位置
      screen.blit(item_icon, item_rect)  # 画像を描画

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

    # 穴に落ちて埋まる判定
    player_x, player_y = int(reimu.pos.x), int(reimu.pos.y)
    below_player = stage_data[player_y +
                          1][player_x] if player_y + 1 < map_s.y else None
    current_tile = stage_data[player_y][player_x]

    if below_player == "=" and current_tile == "#":  # 足元が穴、現在位置が埋まっている場合
      print("穴に埋まりました！ゲームオーバー")
      game_over = True

    # 壊れたタイルの復活処理
    for i, (x, y, time) in enumerate(broken_tiles):
        if time > 0:
            broken_tiles[i] = (x, y, time - 1)  # 時間を1減らす
        else:
            # タイルを復活させる
            stage_data[y] = stage_data[y][:x] + "=" + stage_data[y][x + 1:]
            broken_tiles.pop(i)  # 復活済みタイルをリストから削除

    # ゲームクリア処理
    if check_game_clear():
        screen.blit(font.render("ゲームクリア！", True, (255, 255, 255)), (300, 250))
        screen.blit(font.render("次のステージ(N) / 再スタート(R)",
                    True, (255, 255, 255)), (250, 300))

    for enemy in enemy_list:
      enemy.move_toward(reimu.pos, stage_data, directions)

    # メインループ内で呼び出す処理
    goal_count = check_goal_collision(reimu.rect, goals, goal_count)

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

    # ゲームループ内での進捗表示
    collected_goals = 0  # プレイヤーが収集したゴールアイテムの数
    goal_positions = [(3, 4), (6, 7)]  # ゴールアイテムの位置（例）

    # ゲームループ内で進捗を更新
    collected_goals = handle_goal_progress(reimu.pos, goal_positions)

    # 固定情報の描画
    draw_fixed_info(screen, score, player_lives, collected_goals)

    # ゴールの描画
    goals.draw(screen)

    # 進捗バーの表示
    draw_progress_bar()

    # スコアやライフが条件を満たしたらゲームオーバー
    if player_lives <= 0:
        game_over = True

    # 固定位置に情報を描画
    draw_fixed_info(screen, score, player_life, goal_count)

    score = handle_collisions(reimu.rect, goals, score)
    if len(goals) == 0:  # 全ゴールを達成した場合
      print("すべてのゴールを達成しました！ゲームクリア")
      game_over = True  # ゲームを終了状態に

    # ステージ情報表示
    display_message(f"ステージ: {stage}", (0, 255, 0), -100)  # (0, 255, 0) は緑色

    # 画面の更新
    pg.display.flip()

    # FPS制御
    clock.tick(30)  # 30 FPSに制限

  # ゲームループ [ここまで]
  pg.quit()
  return exit_code
  
if __name__ == "__main__":
  code = main()
  print(f'プログラムを「コード{code}」で終了しました。')