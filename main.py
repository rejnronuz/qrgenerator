# сам pygame
import pygame
# qrcode для генерации кодов
import qrcode

# первоначальная настройка пайгейма
pygame.init()
screen = pygame.display.set_mode((700, 700))
pygame.scrap.init()
pygame.display.set_caption("QrGenerator")
font = pygame.font.Font(None, 32)
infofont = pygame.font.Font(None, 16)
clock = pygame.time.Clock()

# загрузка иконок для тем
try:
    moon_img = pygame.transform.scale(pygame.image.load('moon.png').convert_alpha(), (40, 40))
    sun_img = pygame.transform.scale(pygame.image.load('sun.png').convert_alpha(), (40, 40))
    settings_dark = pygame.transform.scale(pygame.image.load('settingslight.png').convert_alpha(), (40, 40))
    settings_light = pygame.transform.scale(pygame.image.load('settingsdark.png').convert_alpha(), (40, 40))
except Exception as e:
    print(f"не удалось загрузить ассеты!: {e}")
    pygame.quit()
    exit()

# темы, меняйте по желанию
# светлая тема
light_theme = {
    'background': (255, 255, 255),  # фон
    'text': (0, 0, 0),  # текст
    'input': (200, 200, 200),  # активное окно ввода
    'button': (0, 120, 215),  # кнопка
    'border': (0, 0, 0),  # край предпросмотра
    'qr_fill': (0, 0, 0),  # цвет кода
    'qr_bg': (255, 255, 255),  # фон предпросмотра
    'theme_btn_bg': (220, 220, 220)  # фон кнопки с темами
}
# темная тема
dark_theme = {
    'background': (30, 30, 30),  # все так же как в светлой
    'text': (255, 255, 255),
    'input': (60, 60, 60),
    'button': (0, 80, 160),
    'border': (255, 255, 255),
    'qr_fill': (255, 255, 255),
    'qr_bg': (30, 30, 30),
    'theme_btn_bg': (80, 80, 80)
}

# кнопки
input_text = ""
input_rect = pygame.Rect(50, 100, 350, 40)
button_rect = pygame.Rect(50, 165, 350, 40)
preview_rect = pygame.Rect(50, 260, 350, 350)
theme_btn_rect = pygame.Rect(600, 20, 50, 50)
settings_btn_rect = pygame.Rect(600, 80, 50, 50)

# переменные
active = False
qrcode_image = None
is_dark_theme = False  # изначальная тема при запуске
settings_window_open = False
color = 'black'
backcolor = 'white'
color_dropdown_open = False  # открыто ли меню выбора цвета
backcolor_dropdown_open = False  # открыто ли меню выбора фона
available_colors = ['black', 'white', 'red', 'green', 'blue', 'yellow']  # доступные цвета

# обновление цветов статических надписей
def update_theme_texts(theme):
    global title_text, button_text, preview_title, info_text, settings_btn_text
    title_text = font.render("Введите текст для генерации QR-кода:", True, theme['text'])
    button_text = font.render("Сгенерировать QR-код", True, theme['text'])
    preview_title = font.render("Предпросмотр:", True, theme['text'])
    info_text = font.render("Готовый QR-код будет сохранен в папку с программой", True, theme['text'])
    settings_btn_text = font.render("Настройки", True, theme['text'])


update_theme_texts(light_theme)


# генерация qr кодов
def generate_qrcode(text):
    if not text:
        return None
    # настройки генерации кодов
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    # сохранение кода в папку
    img = qr.make_image(fill_color=color, back_color=backcolor)
    img.save("qrcode.png")

    # превью для тем
    theme = dark_theme if is_dark_theme else light_theme
    img = qr.make_image(fill_color=theme['qr_fill'], back_color=theme['qr_bg'])
    img_rgb = img.convert("RGB")
    data = img_rgb.tobytes()
    pygame_surface = pygame.image.fromstring(data, img_rgb.size, "RGB")
    return pygame.transform.scale(pygame_surface, (340, 340))


def draw_settings_window():
    settings_rect = pygame.Rect(150, 150, 400, 400)
    current_theme = dark_theme if is_dark_theme else light_theme

    # рисуем окно
    pygame.draw.rect(screen, current_theme['background'], settings_rect)
    pygame.draw.rect(screen, current_theme['border'], settings_rect, 2)

    # рисуем заголовок
    settings_title = font.render("Настройки", True, current_theme['text'])
    screen.blit(settings_title, (settings_rect.x + 20, settings_rect.y + 20))

    # кнопка выбора цвета qr-кода
    color_rect = pygame.Rect(settings_rect.x + 50, settings_rect.y + 80, 150, 40)
    pygame.draw.rect(screen, color if color != 'white' else (200, 200, 200), color_rect)
    pygame.draw.rect(screen, current_theme['border'], color_rect, 2)
    color_label = font.render("Цвет кода:", True, current_theme['text'])
    screen.blit(color_label, (settings_rect.x + 50, settings_rect.y + 60))

    # поясняющая надпись
    preview_note = infofont.render("(в предпросмотре не отображается)", True, current_theme['text'])
    screen.blit(preview_note, (settings_rect.x + 50, settings_rect.y + 130))

    # выпадающий список цветов
    if color_dropdown_open:
        for i, col in enumerate(available_colors):
            item_rect = pygame.Rect(color_rect.x, color_rect.y + (i + 1) * 40, 150, 40)
            pygame.draw.rect(screen, col if col != 'white' else (200, 200, 200), item_rect)
            pygame.draw.rect(screen, current_theme['border'], item_rect, 2)

    # кнопка выбора фона qr-кода
    backcolor_rect = pygame.Rect(settings_rect.x + 200, settings_rect.y + 80, 150, 40)
    pygame.draw.rect(screen, backcolor if backcolor != 'white' else (200, 200, 200), backcolor_rect)
    pygame.draw.rect(screen, current_theme['border'], backcolor_rect, 2)
    backcolor_label = font.render("Цвет фона:", True, current_theme['text'])
    screen.blit(backcolor_label, (settings_rect.x + 200, settings_rect.y + 60))

    # выпадающий список фонов
    if backcolor_dropdown_open:
        for i, col in enumerate(available_colors):
            item_rect = pygame.Rect(backcolor_rect.x, backcolor_rect.y + (i + 1) * 40, 150, 40)
            pygame.draw.rect(screen, col if col != 'white' else (200, 200, 200), item_rect)
            pygame.draw.rect(screen, current_theme['border'], item_rect, 2)


running = True
while running:
    current_theme = dark_theme if is_dark_theme else light_theme
    screen.fill(current_theme['background'])
    # кучка ивентов
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_rect.collidepoint(event.pos):
                active = True
            else:
                active = False

            if button_rect.collidepoint(event.pos):
                qrcode_image = generate_qrcode(input_text)

            if theme_btn_rect.collidepoint(event.pos):
                is_dark_theme = not is_dark_theme
                update_theme_texts(dark_theme if is_dark_theme else light_theme)
                if input_text:
                    qrcode_image = generate_qrcode(input_text)

            # обработка нажатия на кнопку настроек
            if settings_btn_rect.collidepoint(event.pos):
                settings_window_open = not settings_window_open
            if settings_window_open:
                mouse_pos = event.pos
                color_rect = pygame.Rect(200, 230, 150, 40)
                backcolor_rect = pygame.Rect(350, 230, 150, 40)

                # клик по кнопке цвета
                if color_rect.collidepoint(mouse_pos):
                    color_dropdown_open = not color_dropdown_open
                    backcolor_dropdown_open = False
                # клик по кнопке фона
                elif backcolor_rect.collidepoint(mouse_pos):
                    backcolor_dropdown_open = not backcolor_dropdown_open
                    color_dropdown_open = False
                # выбор цвета из списка
                elif color_dropdown_open:
                    for i, col in enumerate(available_colors):
                        item_rect = pygame.Rect(200, 270 + i * 40, 150, 40)
                        if item_rect.collidepoint(mouse_pos):
                            color = col
                            color_dropdown_open = False
                # выбор фона из списка
                elif backcolor_dropdown_open:
                    for i, col in enumerate(available_colors):
                        item_rect = pygame.Rect(350, 270 + i * 40, 150, 40)
                        if item_rect.collidepoint(mouse_pos):
                            backcolor = col
                            backcolor_dropdown_open = False
                # клик вне элементов закрывает меню
                else:
                    color_dropdown_open = False
                    backcolor_dropdown_open = False

        if event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                clipboard_text = pygame.scrap.get(pygame.SCRAP_TEXT)
                if clipboard_text:
                    try:
                        pasted_text = clipboard_text.decode('utf-8').replace('\x00', '')
                        input_text += pasted_text
                    except UnicodeDecodeError:
                        pass
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            elif not (event.mod & pygame.KMOD_CTRL and event.key == pygame.K_v):
                input_text += event.unicode

    # дальше идет отрисовка всякой брехни

    # верхний текст / название
    screen.blit(title_text, (50, 50))

    # поле ввода
    pygame.draw.rect(screen, current_theme['input'] if active else current_theme['background'], input_rect)
    pygame.draw.rect(screen, current_theme['border'], input_rect, 2)
    text_surface = font.render(input_text, True, current_theme['text'])
    screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

    # кнопка генерации
    pygame.draw.rect(screen, current_theme['button'], button_rect)
    screen.blit(button_text, (button_rect.x + 50, button_rect.y + 10))

    # место для превью
    pygame.draw.rect(screen, current_theme['border'], preview_rect, 2)
    screen.blit(preview_title, (50, 230))

    # кнопка смены темы
    pygame.draw.rect(screen, current_theme['theme_btn_bg'], theme_btn_rect)
    screen.blit(sun_img if is_dark_theme else moon_img,
                (theme_btn_rect.x + 5, theme_btn_rect.y + 5))

    pygame.draw.rect(screen, current_theme['theme_btn_bg'], settings_btn_rect)
    screen.blit(settings_light if is_dark_theme else settings_dark, (settings_btn_rect.x + 5, settings_btn_rect.y + 5))

    if qrcode_image:
        screen.blit(qrcode_image, (preview_rect.x + 5, preview_rect.y + 5))

    screen.blit(info_text, (50, 620))

    # отрисовка окна настроек, если оно открыто
    if settings_window_open:
        draw_settings_window()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
