import pygame

# タイトルの描画（グラデーション）
def render_gradient_title(text, font, color1, color2, width, height):
    # グラデーション用のSurfaceを作成
    gradient_surface = pygame.Surface((width, height))

    # グラデーションの計算
    for y in range(height):
        ratio = y / height  # 現在の高さに応じた割合
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(gradient_surface, (r, g, b), (0, y), (width, y))

    # テキストの描画
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(width // 2, height // 2))

    # グラデーションにテキストをブレンド
    gradient_surface.blit(text_surface, text_rect)
    return gradient_surface

# 難易度を選択する関数
def display_home(screen):
    pygame.init()
    font = pygame.font.Font(None, 74)

    # タイル画像のロード
    tile_image = pygame.image.load("./data/img/ground.png")  # 32×32ピクセルのタイル画像を用意
    tile_width, tile_height = tile_image.get_size()

    # タイル背景を描画
    screen_width, screen_height = screen.get_size()
    for y in range(0, screen_height, tile_height):  # 縦方向にタイルを並べる
        for x in range(0, screen_width, tile_width):  # 横方向にタイルを並べる
            screen.blit(tile_image, (x, y))  # タイルを描画

    # 白い円の描画（中央付近）
    # 白い楕円の描画（中央付近）
    center_x, center_y = screen.get_width() // 2, screen.get_height() // 2
    radius_x, radius_y = 300, 200  # 楕円の半径（横方向と縦方向）
    ellipse_rect = pygame.Rect(
        center_x - radius_x, center_y - radius_y, radius_x * 2, radius_y * 2)
    pygame.draw.ellipse(screen, (255, 255, 255), ellipse_rect)
    
        # グラデーションタイトルを描画
    title_surface = render_gradient_title(
        "Load Runner", font, (255, 0, 0), (255, 165, 0), 800, 100
    )
    screen.blit(title_surface, (0, 50))  # タイトルの位置を調整

    # 難易度ボタンの定義
    button_data = [
        {"text": "Easy", "rect": pygame.Rect(
            150, 200, 200, 50), "color": (0, 255, 0)},
        {"text": "Normal", "rect": pygame.Rect(
            150, 300, 200, 50), "color": (255, 255, 0)},
        {"text": "Hard", "rect": pygame.Rect(
            150, 400, 200, 50), "color": (255, 0, 0)},
        {"text": "How to Play", "rect": pygame.Rect(
            450, 300, 200, 50), "color": (0, 0, 255)},
    ]

    # ボタンを描画
    font = pygame.font.Font(None, 36)
    mouse_pos = pygame.mouse.get_pos()  # マウスの座標を取得
    buttons = []

    for data in button_data:
        color = data["color"]
        if data["rect"].collidepoint(mouse_pos):  # マウスがボタン上にある場合
            color = (255, 255, 255)  # ハイライトカラー
        pygame.draw.rect(screen, color, data["rect"])
        text_surface = font.render(data["text"], True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=data["rect"].center)
        screen.blit(text_surface, text_rect)
        buttons.append({"text": data["text"], "rect": data["rect"]})

    pygame.display.flip()

    return buttons

def display_tutorial(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    tutorial_text = [
        "Use arrow keys to move.",
        "Collect all treasures to clear the stage.",
        "Avoid enemies and traps.",
        "Press 'Esc' to return to the main menu."
    ]
    for i, line in enumerate(tutorial_text):
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (50, 100 + i * 50))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # メインメニューに戻る

# 難易度を選択するためのイベント処理
def handle_home_events(buttons,screen):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos  # マウスのクリック位置
            for button in buttons:
                if button["rect"].collidepoint(mouse_pos):
                    if button["text"] == "How to Play":
                        display_tutorial(screen)  # チュートリアル画面を表示
                        return None
                    return button["text"]  # 難易度を返す
    return None
