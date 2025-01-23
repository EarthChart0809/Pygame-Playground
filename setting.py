import pygame as pg

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
life_icon = load_image('./data/img/life_icon.png', (32, 32))

def draw_map(screen, stage_data, chip_s):
    for y, row in enumerate(stage_data):
        for x, cell in enumerate(row):
            rect = (x * chip_s, y * chip_s, chip_s, chip_s)  # グリッド線
            if cell == "#":  # 壁
                screen.blit(wall_img, rect)  # 壁の画像を描画
            elif cell == "L":  # 階段
                screen.blit(ladder_img, rect)  # 階段の画像を描画
            elif cell == "-":  # ロープ
                screen.blit(rope_img, rect)  # ロープの画像を描画
            elif cell == "=":  # 地面
                screen.blit(ground_img, rect)  # 地面の画像を描画

# ステージ要素
stage_data = [
    "######################################",
    "#                                    #",
    "#     L=====================L        #",
    "#     L                     L        #",
    "#     L                     LL       #",
    "#========L===========        L=======#",
    "#        L                 L         #",
    "#        L                 L         #",
    "#  L=====L====L=====L   ====L========#",
    "#  L          L     L                #",
    "#  L          L     L                #",
    "#  L     L====L     L     ====L      #",
    "#  L     L          L         L      #",
    "#  L     L          L         LL     #",
    "#  L=====L     =====L=====     L=====#",
    "#  L                                L#",
    "#  L                                L#",
    "#  ==================================#",
    "######################################",
]

def get_settings(difficulty):
    if difficulty == "Easy":
        return {"enemy_speed": 2, "player_lives": 5}
    elif difficulty == "Normal":
        return {"enemy_speed": 4, "player_lives": 3}
    elif difficulty == "Hard":
        return {"enemy_speed": 6, "player_lives": 1}
    else:
        raise ValueError("Unknown difficulty")

# ステージ要素
# Easy stage
easy_stage = [
    "##############################",
    "#                            #",
    "#     L============L         #",
    "#     L                      #",
    "#     LL                     #",
    "#======L====L======          #",
    "#           L                #",
    "#           L                #",
    "#  L=====L====L              #",
    "#  L     L    L              #",
    "#  L     L    L              #",
    "#  L =L==L====L              #",
    "#     L                      #",
    "#     L                      #",
    "#     L                      #",
    "#     L                     #",
    "#  L=====L====L              #",
    "#                            #",
    "##############################"
]

easy_enemies = [
    (5 * 32, 15 * 32),
    (12 * 32, 16 * 32)
]

easy_items = [
    (10 * 32, 5 * 32),
    (8 * 32, 10 * 32)
]

# Normal stage
normal_stage = [
    "######################################",
    "#                                    #",
    "#     L=====================L        #",
    "#     L                     L        #",
    "#     L          E          LL       #",
    "#========L===========        L=======#",
    "#        L                 L         #",
    "#        L          E      L         #",
    "#  L=====L====L=====L   ====L========#",
    "#  L          L     L                #",
    "#  L          L     L                #",
    "#  L     L====L     L     ====L      #",
    "######################################"
]

normal_enemies = [
    (5 * 32, 4 * 32),
    (10 * 32, 6 * 32),
    (15 * 32, 8 * 32)
]

normal_items = [
    (3 * 32, 5 * 32),
    (7 * 32, 9 * 32),
    (11 * 32, 13 * 32)
]

# Hard stage
hard_stage = [
    "######################################",
    "#                                    #",
    "#     L=====================L        #",
    "#     L                     L        #",
    "#     L                     LL       #",
    "#========L===========        L=======#",
    "#        L                 L         #",
    "#        L                 L         #",
    "#  L=====L====L=====L   ==L=L========#",
    "#  L          L     L     L          #",
    "#  L          L     L     L          #",
    "#  L     L====L     L     ====L      #",
    "#  L     L          L         L      #",
    "#  L     L          L         LL     #",
    "#  L=====L     =====L=====     L====L#",
    "#  L                L               L#",
    "#  L                L               L#",
    "#  ==================================#",
    "######################################",
]

hard_enemies = [
    (6 * 32, 5 * 32),  # 敵1: 6列目、5行目
    (10 * 32, 9 * 32),  # 敵2: 10列目、9行目
    (18 * 32, 11 * 32),  # 敵3: 18列目、11行目
    (20 * 32, 14 * 32)  # 敵4: 20列目、14行目
]

hard_items = [
    (8 * 32, 3 * 32),  # アイテム1: 8列目、3行目
    (15 * 32, 7 * 32),  # アイテム2: 15列目、7行目
    (20 * 32, 11 * 32),  # アイテム3: 20列目、11行目
    (25 * 32, 15 * 32)  # アイテム4: 25列目、15行目
]
