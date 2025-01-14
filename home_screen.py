import pygame

# 難易度を選択する関数
def display_home(screen):
    pygame.init()
    font = pygame.font.Font(None, 74)

    # 背景の描画
    screen.fill((0, 0, 0))
    title = font.render("Load Runner", True, (255, 255, 255))
    screen.blit(title, (300, 100))

    # 難易度ボタンの定義
    button_data = [
        {"text": "Easy", "rect": pygame.Rect(
            150, 200, 200, 50), "color": (0, 255, 0)},
        {"text": "Normal", "rect": pygame.Rect(
            150, 300, 200, 50), "color": (255, 255, 0)},
        {"text": "Hard", "rect": pygame.Rect(
            150, 400, 200, 50), "color": (255, 0, 0)},
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


# 難易度を選択するためのイベント処理
def handle_home_events(buttons):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos  # マウスのクリック位置
            for button in buttons:
                if button["rect"].collidepoint(mouse_pos):
                    return button["text"]
    return None
