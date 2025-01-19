import pygame as pg
from player import PlayerCharacter
from enemy import EnemyCharacter
from goal import Goal
from setting import draw_map ,load_image
from home_screen import display_home, handle_home_events
from setting import easy_stage, normal_stage, hard_stage
from setting import easy_enemies, normal_enemies, hard_enemies
from setting import easy_items, normal_items, hard_items

life_icon = load_image('./data/img/life_icon.png',(32, 32))  
item_icon = load_image('./data/img/item_icon.png',(32,32))

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

#画面更新の際、情報を固定位置に描画する関数を作成
def draw_fixed_info(surface, score, life, goal_count,reimu,frame):
  # ライフ表示（左上）
  life_text_color = (255, 0, 0) if life <= 1 else (255, 255, 255)
  life_text = font.render(f"Lives:", True, life_text_color)
  surface.blit(life_text, (10, 10))

  for i in range(life):
      # 無敵状態のとき、ハートアイコンを点滅させる（例: フレーム数で奇数のとき非表示）
      if not (reimu.invincible and frame % 10 < 5):
          surface.blit(life_icon, (10 + i * 30, 40))

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
  pg.draw.rect(surface, progress_bg_color, progress_bar_rect)
  progress_fill_width = (goal_items_collected / GOAL_ITEM_COUNT) * progress_width  # 目標10個収集
  pg.draw.rect(surface, progress_color, pg.Rect(progress_bar_rect.x,
                                                progress_bar_rect.y, progress_fill_width, progress_bar_rect.height))

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

def draw_game_elements(screen, stage_data, chip_s, reimu, enemies, items, frame):
    """ゲーム内の全要素を描画する関数"""
    # ステージ描画
    draw_map(screen, stage_data, chip_s)

    # プレイヤー描画
    screen.blit(reimu.get_img(frame), reimu.rect.topleft)

    # 敵描画
    for enemy in enemies:
        screen.blit(enemy.get_img(frame), enemy.rect.topleft)

    # アイテム描画
    for item in items:
        item_rect = pg.Rect(item[0] * chip_s, item[1] * chip_s, chip_s, chip_s)
        screen.blit(item_icon, item_rect)

    # フレームカウンタの描画
    frame += 1
    frm_str = f'{frame:05}'
    screen.blit(font.render(frm_str, True, 'BLACK'), (10, 10))
    screen.blit(font.render(f'{reimu.pos}', True, 'BLACK'), (10, 20))


# キー入力関連の処理を関数化
def handle_keydown(event, reimu, stage_data, broken_tiles):
    """
    キー押下時の処理を管理。
    """
    global goal_items_collected, lives, MAX_LIVES

    if event.key == pg.K_a:  # Aキーで左側の地面を壊す
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

def get_movement_command(key_state):
    """
    移動コマンドを返す関数。
    """
    if key_state[pg.K_UP]:
        return 0
    elif key_state[pg.K_RIGHT]:
        return 1
    elif key_state[pg.K_DOWN]:
        return 2
    elif key_state[pg.K_LEFT]:
        return 3
    return -1

# ゲームオーバー画面の描画
def draw_game_over_screen(screen):
    font = pg.font.Font(None, 48)
    text = font.render("Game Over!", True, (255, 0, 0))
    restart_text = font.render(
        "Press R to Restart or Q to Quit", True, (255, 255, 255))
    screen.blit(text, (200, 200))
    screen.blit(restart_text, (300, 300))

# ゲームクリア画面の描画
def draw_game_clear_screen(screen):
    font = pg.font.Font(None, 48)
    text = font.render("Congratulations!", True, (0, 255, 0))
    next_stage_text = font.render(
        "Press R to Restart or Q to Quit", True, (255, 255, 255))
    screen.blit(text, (200, 200))
    screen.blit(next_stage_text, (200, 300))

def get_settings(difficulty):
    if difficulty == "Easy":
        return {"stage_data": easy_stage, "enemies": easy_enemies, "items": easy_items}
    elif difficulty == "Normal":
        return {"stage_data": normal_stage, "enemies": normal_enemies, "items": normal_items}
    elif difficulty == "Hard":
        return {"stage_data": hard_stage, "enemies": hard_enemies, "items": hard_items}
    else:
        return {"stage_data": easy_stage, "enemies": easy_enemies, "items": easy_items}

# アイテムの位置リスト
items = [(3, 4), (7, 7), (10, 16), (12, 16), (13, 10), (20, 7)]
goal_positions = [(3, 4), (7, 5), (10, 15), (12, 18)]  # ゴールアイテムの位置
goal_count = handle_goal_progress(player_pos, goal_positions)  # ゴール進捗の更新

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
game_state = "playing"  # 初期状態はゲーム中

def main():
  global game_state, player_lives, goal_items_collected, stage

  # 初期化処理
  pg.init()
  chip_s = 32  # マップチップの基本サイズ

  # ホーム画面の表示
  screen = pg.display.set_mode((800, 600))
  difficulty = None
  while difficulty is None:
      buttons = display_home(screen)
      difficulty = handle_home_events(buttons)

  print(f"選択された難易度: {difficulty}")

  # 難易度ごとの設定を取得
  settings = get_settings(difficulty)
  stage_data = settings["stage_data"]
  print(f"設定: {settings}")
  map_s = pg.Vector2(len(stage_data[0]),len(stage_data))  # マップの横・縦の配置数

  # 難易度ごとの設定を取得
  settings = get_settings(difficulty)
  stage_data = settings["stage_data"]
  enemy_positions = settings["enemies"]
  item_positions = settings["items"]
  print(f"設定: {settings}")

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
  enemy_list = enemy_list = [EnemyCharacter(pos, './data/img/enemy.png') for pos in enemy_positions]

# アイテムの生成・初期化
  item_list = [Goal(pos, (32,32)) for pos in item_positions]

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
  goal_count = len(goals)  # ゴールの初期数を更新

  # スコアとライフ
  score = 0
  player_lives = 3
  game_clear = False
  game_clear_time = 0

  # 定数の設定
  MOVE_COOLDOWN = 256  # ミリ秒単位で移動のクールダウン時間を設定

  # グローバルまたはクラス内変数
  last_move_time = 0  # 最後に移動した時間を記録

  # 初期化時に背景を描画してキャッシュ
  background_surface = pg.Surface((disp_w, disp_h))
  background_surface.fill((0, 0, 0))  # 背景色を設定
  for x in range(0, disp_w, chip_s):  # 縦線
    pg.draw.line(background_surface, grid_c, (x, 0), (x, disp_h))
  for y in range(0, disp_h, chip_s):  # 横線
    pg.draw.line(background_surface, grid_c, (0, y), (disp_w, y))

  # ゲームループ
  while not exit_flag:
    current_time = pg.time.get_ticks()
    # 穴に落ちて埋まる判定
    player_x, player_y = int(reimu.pos.x), int(reimu.pos.y)
    if stage_data[player_y + 1][player_x] == "=" and stage_data[player_y][player_x] == "#":
        print("穴に埋まりました！ゲームオーバー")
        game_over = True

    # ライフが0になった場合のゲームオーバー判定
    if player_lives <= 0:
        game_state = "game_over"

    # ゴールアイテムをすべて収集し、ゴールに触れた場合のゲームクリア判定
    if goal_items_collected >= GOAL_ITEM_COUNT and stage_data[player_y][player_x] == "G":
        game_state = "game_clear"

    # イベント処理
    for event in pg.event.get():
        if event.type == pg.QUIT:
          exit_flag = True
        elif event.type == pg.KEYDOWN:
          if event.key == pg.K_r and game_state in ["game_over", "game_clear"]:
              # ゲームリスタート
              game_state = "playing"
              player_lives = 3
              score = 0
              goal_items_collected = 0
              stage = 1
          elif event.key == pg.K_q and game_state in ["game_over", "game_clear"]:
              # ゲーム終了
              exit_flag = True
          else:
            # キー押下時の処理
            handle_keydown(event, reimu, stage_data, broken_tiles)

    # ゲームの状態に応じた処理
    if game_state == "playing":
      # ゲーム進行処理
      screen.fill((0, 0, 0))
      draw_map(screen, stage_data, chip_s)
      reimu.update()

      # タイルの幅と高さを計算
      tile_width = SCREEN_WIDTH / len(stage_data[0])  # 1タイルの幅
      tile_height = SCREEN_HEIGHT / len(stage_data)  # 1タイルの高さ

      # 移動のクールダウンを適用
      if cmd_move != -1 and current_time - last_move_time > MOVE_COOLDOWN:
          reimu.update()
          last_move_time = current_time

      for enemy in enemy_list:
        # 敵の移動処理（プレイヤーを追いかける）
        enemy.move(reimu.pos, stage_data, (len(stage_data[0]), len(stage_data)))
    
        # 敵の更新処理
        enemy.update(reimu.rect, stage_data, (tile_width, tile_height))

        # 敵を描画
        screen.blit(enemy.image, enemy.rect.topleft)

        # プレイヤーと敵の接触判定
        if reimu.rect.colliderect(enemy.rect) and not reimu.invincible:
          player_lives -= 1  # ライフを1減少
          reimu.invincible = True  # 無敵状態をオン
          reimu.invincible_timer = 60  # 無敵状態の持続時間（例: 60フレーム）
          print(f"敵にぶつかりました！残りライフ: {player_lives}")

          if player_lives <= 0:
            game_state = "game_over"
            print("ライフが尽きました！ゲームオーバー")

        # アイテムの描画
      for item in item_list:
                screen.blit(item.image, item.rect)

      # ゴール達成判定
      goal_count = check_goal_collision(reimu.rect, goals, goal_count)
      if goal_count == 0:
          game_state = "game_clear"
      if player_lives <= 0 and game_state == "playing":
        game_state = "game_over"

      # 描画更新
      draw_fixed_info(screen, score, player_lives,goal_items_collected, reimu, frame)

    elif game_state == "game_over":
      screen.fill((0,0,0))
      draw_game_over_screen(screen)

    elif game_state == "game_clear":
      screen.fill((0,0,0))
      draw_game_clear_screen(screen)

    # ゲーム進行
    screen.blit(background_surface, (0, 0))
    reimu.rect.topleft = reimu.get_dp()  # プレイヤーの位置を更新

    # システムイベントの検出
    cmd_move = -1
      
    # キー入力の状態を取得して移動コマンドを更新
    key = pg.key.get_pressed()
    cmd_move = get_movement_command(key)

    # 移動可能かチェック
    if cmd_move - last_move_time > MOVE_COOLDOWN:
        if key[pg.K_UP]:
            cmd_move = 0
            last_move_time = cmd_move  # 最後の移動時間を更新
        elif key[pg.K_RIGHT]:
            cmd_move = 1
            last_move_time = cmd_move
        elif key[pg.K_DOWN]:
            cmd_move = 2
            last_move_time = cmd_move
        elif key[pg.K_LEFT]:
            cmd_move = 3
            last_move_time = cmd_move
        else:
            cmd_move = -1  # キーが押されていない場合

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

    # メインループ内で呼び出す処理
    goal_count = check_goal_collision(reimu.rect, goals, goal_count)

    # 自キャラの描画
    screen.blit(reimu.get_img(frame), reimu.get_dp())

    # ゲームループ内での進捗表示
    collected_goals = 0  # プレイヤーが収集したゴールアイテムの数
    goal_positions = [(3, 4), (6, 7)]  # ゴールアイテムの位置（例）

    # ゲームループ内で進捗を更新
    collected_goals = handle_goal_progress(reimu.pos, goal_positions)

    # ゴールの描画
    goals.draw(screen)

    # 進捗バーの表示
    draw_progress_bar()

    # スコアやライフが条件を満たしたらゲームオーバー
    if player_lives <= 0:
        game_over = True

    score = handle_collisions(reimu.rect, goals, score)
    if len(goals) == 0:  # 全ゴールを達成した場合
      print("すべてのゴールを達成しました！ゲームクリア")
      game_over = True  # ゲームを終了状態に

    # ステージ情報表示
    display_message(f"ステージ: {stage}", (0, 255, 0), -100)  # (0, 255, 0) は緑色

    # ゲームループ内の描画部分
    draw_game_elements(screen, stage_data, chip_s, reimu, enemy_list, items, frame)

    # 固定情報の描画
    draw_fixed_info(screen, score, player_lives, collected_goals, reimu, frame)

    pg.display.update()

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