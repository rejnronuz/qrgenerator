import pygame
import qrcode
import os
import shutil

# Первоначальная настройка
pygame.init()
screen = pygame.display.set_mode((700, 700))
pygame.scrap.init()
pygame.display.set_caption("QrGenerator")
font = pygame.font.Font(None, 32)
infofont = pygame.font.Font(None, 16)
clock = pygame.time.Clock()
qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

# Загрузка картинок
try:
    moon_img = pygame.transform.scale(pygame.image.load('moon.png').convert_alpha(), (40, 40))
    sun_img = pygame.transform.scale(pygame.image.load('sun.png').convert_alpha(), (40, 40))
    settings_dark = pygame.transform.scale(pygame.image.load('settingslight.png').convert_alpha(), (40, 40))
    settings_light = pygame.transform.scale(pygame.image.load('settingsdark.png').convert_alpha(), (40, 40))
    toggle_light = pygame.transform.scale(pygame.image.load('togglelight.png').convert_alpha(), (40, 40))
    toggle_dark = pygame.transform.scale(pygame.image.load('toggledark.png').convert_alpha(), (40, 40))
except Exception as e:
    print(f"не удалось загрузить ассеты!: {e}")
    pygame.quit()
    exit()
# Темы, меняйте по желанию
# Светлая тема
light_theme = {
    'background': (255, 255, 255),  # Цвет фона
    'text': (0, 0, 0),  # Цвет текста
    'input': (200, 200, 200),  # Поле ввода
    'button': (0, 120, 215),  # Кнопка генерации
    'border': (0, 0, 0),  # Окно превью
    'qr_fill': (0, 0, 0),  # Цвет QR
    'qr_bg': (255, 255, 255),  # Фон превью
    'theme_btn_bg': (220, 220, 220),  # Фон выбора темы и настроек
    'button_inactive': (157, 169, 227)
}
# Темная тема
dark_theme = {
    'background': (30, 30, 30),  # Все так же как в светлой
    'text': (255, 255, 255),
    'input': (60, 60, 60),
    'button': (0, 80, 160),
    'border': (255, 255, 255),
    'qr_fill': (255, 255, 255),
    'qr_bg': (30, 30, 30),
    'theme_btn_bg': (80, 80, 80),
    'button_inactive': (157, 169, 227)
}

# Кнопки
input_rect = pygame.Rect(50, 100, 350, 40) # Поле ввода
button_rect = pygame.Rect(50, 165, 175, 40) # Кнопка генерации
clear_rect = pygame.Rect(230, 165, 175, 40)  # Кнопка очистки
preview_rect = pygame.Rect(50, 260, 350, 350) # Окно превью
theme_btn_rect = pygame.Rect(600, 20, 50, 50) # Кнопка темы
settings_btn_rect = pygame.Rect(600, 80, 50, 50) # Кнопка настроек
save_btn_rect = pygame.Rect(410, 568, 275, 40) # Кнопка сохранения
check_rect_folder = pygame.Rect(200, 405, 50, 50) # Кнопка темы
check_rect_document = pygame.Rect(200, 335, 50, 50)

# Переменные
active = False
qrcode_image = None
input_text = "" # Изначальный текст в поле ввода при запуске
is_dark_theme = True  # Изначальная тема при запуске
settings_window_open = False # Открыто ли окно настроек при запуске
color_dropdown_open = False  # Открыто ли меню выбора заливки
backcolor_dropdown_open = False  # Открыто ли меню выбора фона
savingInsideDocuments = False # Изначальное сохранение

# Цвета
color = 'black' # Изначальные цвет заливки QR при запуске
backcolor = 'white' # Изначальные цвет фона QR при запуске
available_colors = ['black', 'white', 'red', 'green', 'blue', 'yellow']  # Доступные цвета для выбора

# Надписи
def update_theme_texts(theme):
    global title_text, button_text, preview_title, info_text, settings_btn_text, clear_text, save_text, choice_text, choice_text_folder, save_settings_text, settings_title, backcolor_label, color_label
    title_text = font.render("Введите текст для генерации QR-кода:", True, theme['text']) # Верхний текст
    button_text = font.render("Сгенерировать", True, theme['text']) # Текст для кнопки генерации
    preview_title = font.render("Предпросмотр:", True, theme['text']) # Текст для превью
    info_text = font.render("Готовый QR-код будет сохранен в папку с программой", True, theme['text']) # Нижний текст
    settings_btn_text = font.render("Настройки", True, theme['text']) # Текст для настроек
    clear_text = font.render("Очистить", True, theme['text'])  # Текст для кнопки очистки
    save_text = font.render("Сохранить", True, theme['text'])  # Текст над кнопками
    save_settings_text = font.render("Cохранять в...", True, theme['text'])  # Текст для кнопки AAAAAAAAAAAAAAAAAAA CHURKI TOLPOY NAPALIIIII
    choice_text = font.render("В Документы", True, theme['text'])  # Документы
    choice_text_folder = font.render("В текущую папку", True, theme['text'])  # Текущая папка
    settings_title = font.render("Настройки", True, theme['text'])
    color_label = font.render("Цвет кода:", True, theme['text']) # Текст над выбором цвета
    backcolor_label = font.render("Цвет фона:", True, theme['text'])
    print('Updated texts')

if is_dark_theme == True:
    update_theme_texts(dark_theme)
else:
    update_theme_texts(light_theme)

import os
import shutil

def move(file):
    # докумендики гыгыхыхыхыг
    documents_path = os.path.expanduser('~/Documents')
    
    # Проверяем есть ли папка документов
    if not os.path.exists(documents_path):
        print(f"Documents not found{documents_path}")
        return False
    # Проверяем есть ли файл
    if not os.path.exists(file):
        print(f"Sourceиnot found {file}")
        return False
    # Берем имя файла
    filename = os.path.basename(file)
    # Создаем путь
    destination = os.path.join(documents_path, filename)
    
    # Передвигаем файл
    shutil.move(file, destination)
    print(f"File moved to documents {destination}")
    return True

# Генерация
def generate_qrcode(text):
    if not text:
        return None
    # Настройки
    qr.add_data(text)
    qr.make(fit=True)

    # Превью для тем
    img = qr.make_image(fill_color=color, back_color=backcolor)
    img_rgb = img.convert("RGB")
    data = img_rgb.tobytes()
    pygame_surface = pygame.image.fromstring(data, img_rgb.size, "RGB")
    print('Generated preview')
    return pygame.transform.scale(pygame_surface, (340, 340))

def save_qr(text):
    if not text:
        return None
    # Настройки
    qr.add_data(text)
    qr.make(fit=True)

    # Сохранение кода в папку
    img = qr.make_image(fill_color=color, back_color=backcolor)
    img.save("qrcode.png")
    if savingInsideDocuments == True:
        move("qrcode.png") #FUCKASS GRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH
    else:
        pass
    print("Saved QR")
# Отрисовка окна настроек
def draw_settings_window():
    settings_rect = pygame.Rect(150, 150, 400, 400) # Окно настроек

    pygame.draw.rect(screen, current_theme['background'], settings_rect)
    pygame.draw.rect(screen, current_theme['border'], settings_rect, 2)

    screen.blit(settings_title, (settings_rect.x + 20, settings_rect.y + 20))

    color_rect = pygame.Rect(settings_rect.x + 50, settings_rect.y + 80, 150, 40) # Выбор цвета
    pygame.draw.rect(screen, color if color != 'white' else (200, 200, 200), color_rect)
    pygame.draw.rect(screen, current_theme['border'], color_rect, 2)

    screen.blit(color_label, (settings_rect.x + 50, settings_rect.y + 60))
    screen.blit(save_settings_text, (settings_rect.x + 50, settings_rect.y + 145))

    #pygame.draw.rect(toggle_dark if is_dark_theme else toggle_light,
    #(screen, current_theme['button'], check_rect_document))
    pygame.draw.rect(screen, current_theme['button'], check_rect_document)
    pygame.draw.rect(screen, current_theme['button'], check_rect_folder)

    if savingInsideDocuments == True:
        screen.blit(toggle_dark if is_dark_theme else toggle_light, check_rect_document )  # fuckass
    else:
        screen.blit(toggle_dark if is_dark_theme else toggle_light, check_rect_folder )  # fuckass

    screen.blit(choice_text, (settings_rect.x + 115, settings_rect.y + 197))
    screen.blit(choice_text_folder, (settings_rect.x + 115, settings_rect.y + 267))

    if color_dropdown_open:
        for i, col in enumerate(available_colors): # Выбор заливки
            item_rect = pygame.Rect(color_rect.x, color_rect.y + (i + 1) * 40, 150, 40)
            pygame.draw.rect(screen, col if col != 'white' else (200, 200, 200), item_rect)
            pygame.draw.rect(screen, current_theme['border'], item_rect, 2)

    backcolor_rect = pygame.Rect(settings_rect.x + 200, settings_rect.y + 80, 150, 40)
    pygame.draw.rect(screen, backcolor if backcolor != 'white' else (200, 200, 200), backcolor_rect)
    pygame.draw.rect(screen, current_theme['border'], backcolor_rect, 2)
    screen.blit(backcolor_label, (settings_rect.x + 200, settings_rect.y + 60))

    if backcolor_dropdown_open: # Выбор фона
        for i, col in enumerate(available_colors):
            item_rect = pygame.Rect(backcolor_rect.x, backcolor_rect.y + (i + 1) * 40, 150, 40)
            pygame.draw.rect(screen, col if col != 'white' else (200, 200, 200), item_rect)
            pygame.draw.rect(screen, current_theme['border'], item_rect, 2)


running = True
while running:
    current_theme = dark_theme if is_dark_theme else light_theme
    screen.fill(current_theme['background'])
    # Ивенты
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_rect.collidepoint(event.pos):
                active = True
            else:
                active = False

            # Обработка нажатия по кнопке генерации
            if button_rect.collidepoint(event.pos):
                qrcode_image = generate_qrcode(input_text) # Вызываем функцию генерации с введенным текстом

            if save_btn_rect.collidepoint(event.pos):
                save_qr(input_text) # Вызываем функцию генерации с введенным текстом

            # Обработка нажатия по кнопке очистки
            if clear_rect.collidepoint(event.pos):
                input_text = ""  # Очищаем текст
                qrcode_image = None  # Сбрасываем превью
                print('Reset')

            if theme_btn_rect.collidepoint(event.pos):
                is_dark_theme = not is_dark_theme
                update_theme_texts(dark_theme if is_dark_theme else light_theme)
                print('Changed theme')

            # Обработка нажатия на кнопку настроек
            if settings_btn_rect.collidepoint(event.pos):
                settings_window_open = not settings_window_open
                print('Drew settings window')
            if settings_window_open:
                mouse_pos = event.pos
                color_rect = pygame.Rect(200, 230, 150, 40)
                backcolor_rect = pygame.Rect(350, 230, 150, 40)

                # Обработка нажатия на кнопку цвета заливки
                if color_rect.collidepoint(mouse_pos):
                    color_dropdown_open = not color_dropdown_open # Открываем окно с выбором цвета
                    backcolor_dropdown_open = False
                # Обработка нажатия на кнопку цвета фона
                elif backcolor_rect.collidepoint(mouse_pos):
                    backcolor_dropdown_open = not backcolor_dropdown_open # Открываем окно с выбором цвета
                    color_dropdown_open = False
                # Выбор цвета из списка
                elif color_dropdown_open:
                    for i, col in enumerate(available_colors):
                        item_rect = pygame.Rect(200, 270 + i * 40, 150, 40)
                        if item_rect.collidepoint(mouse_pos):
                            color = col
                            color_dropdown_open = False
                # Выбор фона из списка
                elif backcolor_dropdown_open:
                    for i, col in enumerate(available_colors):
                        item_rect = pygame.Rect(350, 270 + i * 40, 150, 40)
                        if item_rect.collidepoint(mouse_pos):
                            backcolor = col
                            backcolor_dropdown_open = False
                else:  # Нажатие вне элементов закрывает меню
                    color_dropdown_open = False
                    backcolor_dropdown_open = False

                # Обработка нажатий по выборам докумендиков
                if check_rect_folder.collidepoint(mouse_pos):
                    if savingInsideDocuments == False:
                        False
                    else:
                        savingInsideDocuments = False
                elif check_rect_document.collidepoint(mouse_pos):
                    if savingInsideDocuments == True:
                        False
                    else:
                        savingInsideDocuments = True

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

    # Отрисовка

    # Верхний текст
    screen.blit(title_text, (50, 50))

    # Поле ввода
    pygame.draw.rect(screen, current_theme['input'] if active else current_theme['background'], input_rect)
    pygame.draw.rect(screen, current_theme['border'], input_rect, 2)
    text_surface = font.render(input_text, True, current_theme['text'])
    screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

    # Кнопка генерации
    pygame.draw.rect(screen, current_theme['button'], button_rect)
    screen.blit(button_text, (button_rect.x + 5, button_rect.y + 10))

    # СОХРАНЕНИЕ ай капс
    pygame.draw.rect(screen, current_theme['button'], save_btn_rect)
    screen.blit(save_text, (save_btn_rect.x + 75, save_btn_rect.y + 10))

    # Кнопка очистки
    pygame.draw.rect(screen, current_theme['button'], clear_rect)
    screen.blit(clear_text, (clear_rect.x + 40, clear_rect.y + 10))

    # Окно для превью
    pygame.draw.rect(screen, current_theme['border'], preview_rect, 2)
    screen.blit(preview_title, (50, 230))

    # Кнопка смены темы
    pygame.draw.rect(screen, current_theme['theme_btn_bg'], theme_btn_rect)
    screen.blit(sun_img if is_dark_theme else moon_img,
                (theme_btn_rect.x + 5, theme_btn_rect.y + 5))

    pygame.draw.rect(screen, current_theme['theme_btn_bg'], settings_btn_rect)
    screen.blit(settings_light if is_dark_theme else settings_dark, (settings_btn_rect.x + 5, settings_btn_rect.y + 5))

    if qrcode_image:
        screen.blit(qrcode_image, (preview_rect.x + 5, preview_rect.y + 5))

    screen.blit(info_text, (50, 620))

    # Отрисовка окна настроек, если оно открыто
    if settings_window_open:
        draw_settings_window()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
