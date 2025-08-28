import pygame # Сам пайгейм, обработка интерфейса
import qrcode # Для генерации кодов
import os # Для создания папок и путей в функциях move и createfolder
import shutil # Для передвижения кода в функции move
import sys # Можешь ваще на это забить, но короче когда ты в .ехе собираешь через pyinstaller, там рабочая директория не папка с екзешником а новая папка каждый раз временная, этот модуль нужен чтобы проверять запускаемся мы со скрипта или с экзешника
from pathlib import Path
from xdg import *
# Короче похер

# Первоначальная настройка
pygame.init() # Нужно пайгеймом
screen = pygame.display.set_mode((700, 700)) # Размер окна
pygame.scrap.init() # Нужно пайгеймом 
pygame.display.set_caption("QrGenerator") # Название окна
font = pygame.font.Font(None, 32) # Шрифт, тут дефолтный стоит
clock = pygame.time.Clock() # Время
folder_name = 'Results' # Название папки в которую будут сохранятся коды если в настройках сохранение в папку

# Загрузка картинок
try:
    moon_img = pygame.transform.scale(pygame.image.load('Assets/moon.png').convert_alpha(), (40, 40))
    sun_img = pygame.transform.scale(pygame.image.load('Assets/sun.png').convert_alpha(), (40, 40))
    settings_dark = pygame.transform.scale(pygame.image.load('Assets/settingslight.png').convert_alpha(), (40, 40))
    settings_light = pygame.transform.scale(pygame.image.load('Assets/settingsdark.png').convert_alpha(), (40, 40))
    toggle_light = pygame.transform.scale(pygame.image.load('Assets/togglelight.png').convert_alpha(), (40, 40))
    toggle_dark = pygame.transform.scale(pygame.image.load('Assets/toggledark.png').convert_alpha(), (40, 40))
except Exception as e: # Выдает ошибку если нету картинок в рабочей директории
    print(f"не удалось загрузить ассеты!: {e}")
    pygame.quit()

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
    'button_inactive': (157, 169, 227),
    'err': (219, 70, 59)
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
    'button_inactive': (157, 169, 227),
    'err': (219, 70, 59)
}

# Кнопки
input_rect = pygame.Rect(50, 100, 350, 40) # Поле ввода
button_rect = pygame.Rect(50, 165, 175, 40) # Кнопка генерации
clear_rect = pygame.Rect(230, 165, 175, 40)  # Кнопка очистки
preview_rect = pygame.Rect(50, 260, 350, 350) # Окно превью
theme_btn_rect = pygame.Rect(600, 20, 50, 50) # Кнопка темы
settings_btn_rect = pygame.Rect(600, 80, 50, 50) # Кнопка настроек
save_btn_rect = pygame.Rect(410, 568, 275, 40) # Кнопка сохранения
check_rect_folder = pygame.Rect(200, 405, 50, 50) # Кнопка сохранения в папку
check_rect_document = pygame.Rect(200, 335, 50, 50) # Кнопка сохранения в документ



# Переменные
active = False
qrcode_image = None # Пока еще ничего не генерировали, пустое изображение в предпросмотре
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
    global title_text, button_text, preview_title, info_text, settings_btn_text, clear_text, save_text, choice_text, choice_text_folder, save_settings_text, settings_title, backcolor_label, color_label, error_setting_text
    title_text = font.render("Введите текст для генерации QR-кода:", True, theme['text']) # Верхний текст
    button_text = font.render("Сгенерировать", True, theme['text']) # Текст для кнопки генерации
    preview_title = font.render("Предпросмотр:", True, theme['text']) # Текст для превью
    if savingInsideDocuments == False:
        info_text = font.render("Готовый QR-код будет сохранен в папку 'Results'", True, theme['text']) # Меняем нижний текст в зависимости от того, куда сохраняем
    else:
        info_text = font.render("Готовый QR-код будет сохранен в документы", True, theme['text']) # Ну я думаю тут ясно
    clear_text = font.render("Очистить", True, theme['text'])  # Текст для кнопки очистки
    save_text = font.render("Сохранить", True, theme['text'])  # Текст кнопки сохранения
    save_settings_text = font.render("Cохранять в...", True, theme['text'])  # Текст над кнопками сохранения в настройках
    error_setting_text = font.render("Папка 'Документы' не найдена!", True, theme['err'])  # Текст над кнопками сохранения в настройках
    choice_text = font.render("В Документы", True, theme['text'])  # Документы
    choice_text_folder = font.render("В 'Results'", True, theme['text'])  # Текущая папка
    settings_title = font.render("Настройки", True, theme['text']) # Верхний текст настроек
    color_label = font.render("Цвет кода:", True, theme['text']) # Текст над выбором цвета
    backcolor_label = font.render("Цвет фона:", True, theme['text']) # Текст над выбором фона
    print('Updated texts')

if is_dark_theme == True: # Обновляем текста в зависимости от темы
    update_theme_texts(dark_theme)
else:
    update_theme_texts(light_theme)

def get_documents_path():
    if sys.platform == 'win32':
        return os.path.join(os.environ['USERPROFILE'], 'Documents')
    else:
        try:
            from xdg import BaseDirectory
            return BaseDirectory.xdg_documents_dir
        except ImportError:
            # Резервный вариант без pyxdg
            xdg_documents = os.environ.get('XDG_DOCUMENTS_DIR')
            if xdg_documents:
                return xdg_documents
                
            config_path = Path.home() / '.config' / 'user-dirs.dirs'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    for line in f:
                        if line.startswith('XDG_DOCUMENTS_DIR'):
                            path = line.split('=')[1].strip().strip('"')
                            return path.replace('$HOME', str(Path.home()))
            
            return str(Path.home() / 'Documents')

def createfolder():
    # Берем рабочую папку скрипта
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    # Создаем путь к Results в рабочей директории
    folder_path = os.path.join(script_dir, folder_name)

    # Проверяем есть ли папка
    if not os.path.isdir(folder_path):
        try:
            # Создаем папку
            os.mkdir(folder_path)
            print(f"Directory '{folder_name}' created successfully")
        except OSError as error: # Если что то случилось, не создаем папку
            print(f"Error creating directory '{folder_name}': {error}")
        else: # Или если она уже существует
            print(f"{folder_name} already exists")

def move(file, document):
    if document:
        documents_path = get_documents_path()
    else:
        # Берем рабочую директорию
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        # Генерим путь к папке Results
        documents_path = os.path.join(script_dir, folder_name)
        # Создаем папку, если она не существует
        if not os.path.exists(documents_path):
            os.makedirs(documents_path)
    
    # Проверяем есть ли файл
    if not os.path.exists(file):
        print(f"Source not found {file}")
        return False
    
    # Берем имя файла
    filename = os.path.basename(file)
    # Создаем путь
    destination = os.path.join(documents_path, filename)
    
    try:
        # Передвигаем файл
        shutil.move(file, destination)
        print(f"File {file} moved to {destination}")
        return True
    except Exception as e:
        print(f"Error moving file: {e}")
        return False
    
# Генерация превью НЕ СОХРАНЕНИЕ!!!!!!
def generate_qrcode(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # Если нет текста, ничего не делать
    if not text:
        return None
    # Настройки
    qr.add_data(text) # Закидываем младенца во фритюрницу (текст в генератор кодов)
    qr.make(fit=True)

    # Генерим превью
    img = qr.make_image(fill_color=color, back_color=backcolor)
    img_rgb = img.convert("RGB")
    data = img_rgb.tobytes()
    # Выводим
    pygame_surface = pygame.image.fromstring(data, img_rgb.size, "RGB")
    print('Generated preview')
    return pygame.transform.scale(pygame_surface, (340, 340))

# СОХРАНЕНИЕ В ПАПКУ НЕ ГЕНЕРАЦИЯ ПРЕВЬЮ!!!!!
def save_qr(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # Если нет текста, ничего не делаем
    if not text:
        return None
    # Настройки
    qr.add_data(text) # Закидываем младенца во фритюрницу (текст в генератор кодов)
    qr.make(fit=True)

    # Сохранение кода в папку
    img = qr.make_image(fill_color=color, back_color=backcolor)
    img.save("qrcode.png")
    createfolder() # Если нет папки в рабочей директории, делаем
    if savingInsideDocuments == True:
        move("qrcode.png", True) # Передвигаем файл ЛИБО в папку Results ЛИБО в папку Документы
    else:
        move("qrcode.png", False)
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
        screen.blit(toggle_dark if is_dark_theme else toggle_light, check_rect_document)  # Отрисовываем галочку на соответствующем выборе пользователя
    else:
        screen.blit(toggle_dark if is_dark_theme else toggle_light, check_rect_folder)  # fuckass

    screen.blit(choice_text, (settings_rect.x + 115, settings_rect.y + 197))
    if not os.path.exists(get_documents_path()):
        screen.blit(error_setting_text, (settings_rect.x + 30, settings_rect.y + 347))
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
                qr = qrcode.QRCode( # shit had me stressed
                version=1, # Тимур или Рамазан тут баг короче был то что оно норм не сбрасывалось, как код показывать будешь уберешь
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
                    )
                print('Reset')

            # Обработка нажатий по кнопке темы
            if theme_btn_rect.collidepoint(event.pos):
                is_dark_theme = not is_dark_theme # Меняем тему
                update_theme_texts(dark_theme if is_dark_theme else light_theme) # Обновляем текста с новой темой
                print('Changed theme')

            # Обработка нажатия на кнопку настроек
            if settings_btn_rect.collidepoint(event.pos):
                settings_window_open = not settings_window_open # Открываем окно настроек если оно закрыто
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
                        item_rect = pygame.Rect(200, 270 + i * 40, 150, 40) # Рисуем квадратик на каждый цвет в списке
                        if item_rect.collidepoint(mouse_pos):
                            color = col # Выбираем цвет в зависимости от выбора пользователя
                            color_dropdown_open = False # Закрываем окошко
                # Выбор фона из списка
                elif backcolor_dropdown_open:
                    for i, col in enumerate(available_colors):
                        item_rect = pygame.Rect(350, 270 + i * 40, 150, 40) # Рисуем квадратик на каждый цвет в списке
                        if item_rect.collidepoint(mouse_pos):
                            backcolor = col # Выбираем цвет в зависимости от выбора пользователя
                            backcolor_dropdown_open = False # Закрываем окошко
                else:  # Нажатие вне элементов закрывает окно
                    color_dropdown_open = False
                    backcolor_dropdown_open = False

                # Обработка нажатий по выборам докумендиков
                if check_rect_folder.collidepoint(mouse_pos):
                    if savingInsideDocuments == False:
                        False # Если уже выбор который нам нужен, ничего не делаем
                    else:
                        savingInsideDocuments = False # Меняем сохранение
                        if is_dark_theme == True: # Обновляем текста для нижнего текста
                            update_theme_texts(dark_theme)
                        else:
                            update_theme_texts(light_theme)
                elif check_rect_document.collidepoint(mouse_pos):
                    if savingInsideDocuments == True:
                        False # Если уже выбор который нам нужен, ничего не делаем
                    else:
                        if not os.path.exists(get_documents_path()):
                            print('fake ahh docs')
                            savingInsideDocuments = False
                        else:
                            savingInsideDocuments = True # Меняем сохранение
                        if is_dark_theme == True: # Обновляем текста для нижнего текста
                            update_theme_texts(dark_theme)
                        else:
                            update_theme_texts(light_theme)

        if event.type == pygame.KEYDOWN and active: # ВВОД ТЕКСТА ЭТО ВАЩЕ НЕ ТРОГАТЬ
            if event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                clipboard_text = pygame.scrap.get(pygame.SCRAP_TEXT) # Обрабатываем вставку
                if clipboard_text:
                    try:
                        pasted_text = clipboard_text.decode('utf-8').replace('\x00', '')
                        input_text += pasted_text
                    except UnicodeDecodeError:
                        pass
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1] # Если бекспейс то удаляем один символ
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

    # Нижний текст
    screen.blit(info_text, (50, 620))

    # Отрисовка окна настроек, если оно открыто
    if settings_window_open:
        draw_settings_window()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
# It's been 24 hours without my Roblox girlfriend, I can't go ahead with this any longer. My mental state is in complete and utter pandemonium. I cried myself to sleep 4 times today. I feel paranoid that my roblox girlfriend may never come back. My roblox girlfriend has the only thing that brings me joy in this cruel life for 7 years now and I won't be able to recover mentally or financially if it's gone. I've spent over $7,000 on my Roblox girlfriend this week alone. I even bought $500 worth of robux for my Roblox girlfriend, because I trust my roblox girlfriend. I told my mom through tears and she yelled at me calling me a "failure" and saying she knew she should have been on birth control. Although, My roblox girlfriend being gone has had it's positive impacts on me. My IQ has increased by 40 and I've been thinking more critically. When I saw the last “gtg” message of my roblox girlfriend, i vomited. I just hope she’ll come back, I even started praying again. I've been a dedicated Christian for 12 years and I began to pray to god in hopes that they my Roblox girlfriend will be back soon. I had to learn Arabic to pray to Allah. I hope my Roblox girlfriend comes back soon I don't know how much longer I can take this. 
