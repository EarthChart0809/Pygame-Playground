import pygame
import sys
import numpy as np

# 背景画像の明度を調整する関数
def adjust_brightness(image, brightness_factor):
    """画像の明度を調整する関数"""
    array = pygame.surfarray.pixels3d(image)
    array = np.clip(array * brightness_factor, 0, 255).astype(np.uint8)
    return pygame.surfarray.make_surface(array)

# グラデーションテキストを作成する関数
def create_gradient_text(text, font, gradient_colors):
    surface = font.render(text, True, (255, 255, 255))
    width, height = surface.get_size()
    gradient_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    for y in range(height):
        ratio = y / height
        r = int(gradient_colors[0][0] * (1 - ratio) +
                gradient_colors[1][0] * ratio)
        g = int(gradient_colors[0][1] * (1 - ratio) +
                gradient_colors[1][1] * ratio)
        b = int(gradient_colors[0][2] * (1 - ratio) +
                gradient_colors[1][2] * ratio)
        pygame.draw.line(gradient_surface, (r, g, b), (0, y), (width, y))

    surface.blit(gradient_surface, (0, 0), None, pygame.BLEND_RGBA_MULT)
    return surface

# ドロップシャドウを描画する関数
def draw_shadow_text(screen, text, font, x, y, shadow_color, gradient_colors):
    shadow_surface = font.render(text, True, shadow_color)
    screen.blit(shadow_surface, (x + 3, y + 3))  # ドロップシャドウの位置
    gradient_text = create_gradient_text(text, font, gradient_colors)
    screen.blit(gradient_text, (x, y))

# 背景を描画する関数（ライト効果付き）
def draw_background(screen, tile_image):
    screen_width, screen_height = screen.get_size()
    tile_width, tile_height = tile_image.get_size()

    # タイル画像の描画
    for x in range(0, screen_width, tile_width):
        for y in range(0, screen_height, tile_height):
            screen.blit(tile_image, (x, y))

    # ライト効果の描画
    light_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    pygame.draw.circle(light_surface, (255, 255, 255, 100), (screen_width // 2, 200), 300)
    screen.blit(light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

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

# ボタンの描画関数
def draw_button(screen, text, font, rect, text_color, rect_color, hover_color, mouse_pos):
    color = hover_color if rect.collidepoint(mouse_pos) else rect_color
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

# タイトル画面の描画
def draw_title_screen(screen, font_title, font_button, mouse_pos, new_game_button_rect, gradient_colors):
    draw_shadow_text(screen, "Lode Runner", font_title,200, 100, (0, 0, 0), gradient_colors)
    draw_button(screen, "New Game", font_button, new_game_button_rect,
                (255, 255, 255), (0, 128, 0), (0, 200, 0), mouse_pos)

# 難易度選択画面の描画
def draw_difficulty_screen(screen, font_button, mouse_pos):
    draw_button(screen, "Easy", font_button, pygame.Rect(200, 200, 400, 60),
                (255, 255, 255), (0, 128, 0), (0, 200, 0), mouse_pos)
    draw_button(screen, "Normal", font_button, pygame.Rect(
        200, 280, 400, 60), (255, 255, 255), (0, 128, 0), (0, 200, 0), mouse_pos)
    draw_button(screen, "Hard", font_button, pygame.Rect(200, 360, 400, 60),
                (255, 255, 255), (0, 128, 0), (0, 200, 0), mouse_pos)

# イベント処理関数
def handle_events(game_state, new_game_button_rect, mouse_pos):
    selected_difficulty = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "title" and new_game_button_rect.collidepoint(mouse_pos):
                game_state = "difficulty"
            elif game_state == "difficulty":
                if 200 <= mouse_pos[0] <= 600:
                    if 200 <= mouse_pos[1] <= 260:
                        selected_difficulty = "Easy"
                    elif 280 <= mouse_pos[1] <= 340:
                        selected_difficulty = "Normal"
                    elif 360 <= mouse_pos[1] <= 420:
                        selected_difficulty = "Hard"
    return game_state, selected_difficulty