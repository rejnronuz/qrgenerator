import pygame
import qrcode
import os
import shutil
import sys
from platformdirs import user_documents_path
from dataclasses import dataclass

@dataclass
class Theme:
    background: tuple
    text: tuple 
    input_color: tuple
    button: tuple
    border: tuple
    qr_fill: tuple
    qr_bg: tuple
    theme_btn_bg: tuple
    button_inactive: tuple
    err: tuple

class QRGenerator:
    WINDOW_SIZE = (700, 700)
    FONT_SIZE = 32
    QR_SIZE = (340, 340)
    BUTTON_SIZE = (175, 40)
    ICON_SIZE = (40, 40)
    
    def __init__(self):
        pygame.init()
        pygame.scrap.init()
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption("QrGenerator")
        self.font = pygame.font.Font(None, self.FONT_SIZE)
        self.clock = pygame.time.Clock()
        
        # Определения тем
        self.light_theme = Theme(
            background=(210, 210, 210),
            text=(40, 40, 40),
            input_color=(200, 200, 200),
            button=(0, 120, 215),
            border=(40, 40, 40),
            qr_fill=(40, 40, 40),
            qr_bg=(255, 255, 255),
            theme_btn_bg=(220, 220, 220),
            button_inactive=(157, 169, 227),
            err=(219, 70, 59)
        )
        
        self.dark_theme = Theme(
            background=(30, 30, 30),
            text=(210, 210, 210),
            input_color=(60, 60, 60),
            button=(0, 80, 160),
            border=(210, 210, 210),
            qr_fill=(210, 210, 210),
            qr_bg=(30, 30, 30),
            theme_btn_bg=(80, 80, 80),
            button_inactive=(157, 169, 227),
            err=(219, 70, 59)
        )
        
        self.current_theme = self.dark_theme
        self.is_dark_theme = True
        
        self._load_assets()
        self._init_state()
        self._create_rects()
        self._update_texts()

    def _load_assets(self):
        """Загрузка и масштабирование ассетов"""
        assets = {
            'moon': 'Assets/moon.png',
            'sun': 'Assets/sun.png', 
            'settings_dark': 'Assets/settingslight.png',
            'settings_light': 'Assets/settingsdark.png',
            'toggle_light': 'Assets/togglelight.png',
            'toggle_dark': 'Assets/toggledark.png'
        }
        
        try:
            self.images = {
                k: pygame.transform.scale(
                    pygame.image.load(v).convert_alpha(),
                    self.ICON_SIZE
                ) for k, v in assets.items()
            }
            # Присвоение часто используемых ссылок на изображения
            self.sun_img = self.images['sun']
            self.moon_img = self.images['moon']
            self.settings_light = self.images['settings_light']
            self.settings_dark = self.images['settings_dark']
            self.toggle_light = self.images['toggle_light']
            self.toggle_dark = self.images['toggle_dark']
            
        except Exception as e:
            print(f"Не удалось загрузить ассеты: {e}")
            pygame.quit()
            sys.exit(1)

    def _init_state(self):
        """Инициализация переменных состояния приложения"""
        self.active = False
        self.qrcode_image = None
        self.input_text = ""
        self.settings_window_open = False
        self.color_dropdown_open = False
        self.backcolor_dropdown_open = False
        self.saving_inside_documents = False
        self.color = 'black'
        self.backcolor = 'white'
        self.available_colors = ['black', 'white', 'red', 'green', 'blue', 'yellow']

    def _create_rects(self):
        """Создание всех прямоугольников pygame, используемых в интерфейсе"""
        self.input_rect = pygame.Rect(50, 100, 350, 40)
        self.button_rect = pygame.Rect(50, 165, *self.BUTTON_SIZE)
        self.clear_rect = pygame.Rect(230, 165, *self.BUTTON_SIZE)
        self.preview_rect = pygame.Rect(50, 260, 350, 350)
        self.theme_btn_rect = pygame.Rect(600, 20, 50, 50)
        self.settings_btn_rect = pygame.Rect(600, 80, 50, 50)
        self.save_btn_rect = pygame.Rect(410, 568, 275, 40)
        self.check_rect_folder = pygame.Rect(200, 405, 50, 50)
        self.check_rect_document = pygame.Rect(200, 335, 50, 50)

    def _update_texts(self):
        """Обновление всех текстовых поверхностей с текущей темой"""
        theme = self.current_theme
        self.title_text = self.font.render("Введите текст для генерации QR-кода:", True, theme.text)
        self.button_text = self.font.render("Сгенерировать", True, theme.text)
        self.preview_title = self.font.render("Предпросмотр:", True, theme.text)
        self.info_text = self.font.render(
            "Готовый QR-код будет сохранен в " + 
            ("документы" if self.saving_inside_documents else "папку 'Results'"),
            True, theme.text
        )
        self.clear_text = self.font.render("Очистить", True, theme.text)
        self.save_text = self.font.render("Сохранить", True, theme.text)
        self.settings_title = self.font.render("Настройки", True, theme.text)
        self.color_label = self.font.render("Цвет кода:", True, theme.text)
        self.backcolor_label = self.font.render("Цвет фона:", True, theme.text)
        self.save_settings_text = self.font.render("Сохранить", True, theme.text)
        self.choice_text = self.font.render("Сохранить в документы", True, theme.text)
        self.choice_text_folder = self.font.render("Сохранить в папку Results", True, theme.text)
        self.error_setting_text = self.font.render("Папка документы не найдена", True, theme.err)

    def update_theme_texts(self):
        self._update_texts()

    def get_documents_path(self):
        return user_documents_path()

    def create_folder(self):
        script_dir = os.path.abspath(sys.argv[0])
        folder_path = os.path.join(script_dir, 'Results')
        
        if not os.path.isdir(folder_path):
            try:
                os.mkdir(folder_path)
            except OSError as error:
                print(f"Ошибка создания директории: {error}")

    def move_file(self, file_path, use_documents):
        if use_documents:
            target_path = self.get_documents_path()
        else:
            if getattr(sys, 'frozen', False): # Определяет путь к папке Results рядом с исполняемым файлом или скриптом
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            target_path = os.path.join(base_path, 'Results')
            os.makedirs(target_path, exist_ok=True)

        if not os.path.isfile(file_path):
            return False

        filename = os.path.basename(file_path)
        destination = os.path.join(target_path, filename)

        try:
            shutil.move(file_path, destination)
            return True
        except Exception as e:
            print(f"Ошибка перемещения файла: {e}")
            return False

    def generate_qrcode_preview(self, text):
        if not text:
            return None
            
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=self.color, back_color=self.backcolor)
        img_rgb = img.convert("RGB")
        data = img_rgb.tobytes()
        pygame_surface = pygame.image.fromstring(data, img_rgb.size, "RGB")
        return pygame.transform.scale(pygame_surface, (340, 340))

    def save_qr_code(self, text):
        if not text:
            return
            
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=self.color, back_color=self.backcolor)
        img.save("qrcode.png")
        self.create_folder()
        self.move_file("qrcode.png", self.saving_inside_documents)

    def draw_settings_window(self):
        """Отрисовка окна настроек"""
        settings_rect = pygame.Rect(150, 150, 400, 400)
        pygame.draw.rect(self.screen, self.current_theme.background, settings_rect)
        pygame.draw.rect(self.screen, self.current_theme.border, settings_rect, 2)
        
        self.screen.blit(self.settings_title, (settings_rect.x + 20, settings_rect.y + 20))
        
        color_rect = pygame.Rect(settings_rect.x + 50, settings_rect.y + 80, 150, 40)
        pygame.draw.rect(self.screen, self.color if self.color != 'white' else (200, 200, 200), color_rect)
        pygame.draw.rect(self.screen, self.current_theme.border, color_rect, 2)
        
        self.screen.blit(self.color_label, (settings_rect.x + 50, settings_rect.y + 60))
        self.screen.blit(self.save_settings_text, (settings_rect.x + 50, settings_rect.y + 145))
        
        pygame.draw.rect(self.screen, self.current_theme.button, self.check_rect_document)
        pygame.draw.rect(self.screen, self.current_theme.button, self.check_rect_folder)

        toggle_image = self.toggle_dark if self.is_dark_theme else self.toggle_light
        if self.saving_inside_documents:
            self.screen.blit(toggle_image, self.check_rect_document)
        else:
            self.screen.blit(toggle_image, self.check_rect_folder)

        self.screen.blit(self.choice_text, (settings_rect.x + 115, settings_rect.y + 197))
        if not os.path.exists(self.get_documents_path()):
            self.screen.blit(self.error_setting_text, (settings_rect.x + 30, settings_rect.y + 347))
        self.screen.blit(self.choice_text_folder, (settings_rect.x + 115, settings_rect.y + 267))

        if self.color_dropdown_open:
            for i, color in enumerate(self.available_colors):
                item_rect = pygame.Rect(color_rect.x, color_rect.y + (i + 1) * 40, 150, 40)
                pygame.draw.rect(self.screen, color if color != 'white' else (200, 200, 200), item_rect)
                pygame.draw.rect(self.screen, self.current_theme.border, item_rect, 2)

        backcolor_rect = pygame.Rect(settings_rect.x + 200, settings_rect.y + 80, 150, 40)
        pygame.draw.rect(self.screen, self.backcolor if self.backcolor != 'white' else (200, 200, 200), backcolor_rect)
        pygame.draw.rect(self.screen, self.current_theme.border, backcolor_rect, 2)
        self.screen.blit(self.backcolor_label, (settings_rect.x + 200, settings_rect.y + 60))

        if self.backcolor_dropdown_open:
            for i, color in enumerate(self.available_colors):
                item_rect = pygame.Rect(backcolor_rect.x, backcolor_rect.y + (i + 1) * 40, 150, 40)
                pygame.draw.rect(self.screen, color if color != 'white' else (200, 200, 200), item_rect)
                pygame.draw.rect(self.screen, self.current_theme.border, item_rect, 2)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
                
            if event.type == pygame.KEYDOWN and self.active:
                self.handle_key_input(event)
                
        return True

    def handle_mouse_click(self, mouse_pos):
        self.active = self.input_rect.collidepoint(mouse_pos)

        if self.button_rect.collidepoint(mouse_pos):
            self.qrcode_image = self.generate_qrcode_preview(self.input_text)

        if self.save_btn_rect.collidepoint(mouse_pos):
            self.save_qr_code(self.input_text)

        if self.clear_rect.collidepoint(mouse_pos):
            self.input_text = ""
            self.qrcode_image = None

        if self.theme_btn_rect.collidepoint(mouse_pos):
            self.is_dark_theme = not self.is_dark_theme
            self.current_theme = self.dark_theme if self.is_dark_theme else self.light_theme
            self.update_theme_texts()

        if self.settings_btn_rect.collidepoint(mouse_pos):
            self.settings_window_open = not self.settings_window_open

        if self.settings_window_open:
            self.handle_settings_interaction(mouse_pos)

    def handle_settings_interaction(self, mouse_pos):
        color_rect = pygame.Rect(200, 230, 150, 40)
        backcolor_rect = pygame.Rect(350, 230, 150, 40)

        if color_rect.collidepoint(mouse_pos):
            self.color_dropdown_open = not self.color_dropdown_open
            self.backcolor_dropdown_open = False
        elif backcolor_rect.collidepoint(mouse_pos):
            self.backcolor_dropdown_open = not self.backcolor_dropdown_open
            self.color_dropdown_open = False
        elif self.color_dropdown_open:
            self.handle_color_selection(mouse_pos)
        elif self.backcolor_dropdown_open:
            self.handle_backcolor_selection(mouse_pos)
        else:
            self.color_dropdown_open = False
            self.backcolor_dropdown_open = False

        self.handle_saving_preference(mouse_pos)

    def handle_color_selection(self, mouse_pos):
        for i, color in enumerate(self.available_colors):
            item_rect = pygame.Rect(200, 270 + i * 40, 150, 40)
            if item_rect.collidepoint(mouse_pos):
                self.color = color
                self.color_dropdown_open = False

    def handle_backcolor_selection(self, mouse_pos):
        for i, color in enumerate(self.available_colors):
            item_rect = pygame.Rect(350, 270 + i * 40, 150, 40)
            if item_rect.collidepoint(mouse_pos):
                self.backcolor = color
                self.backcolor_dropdown_open = False

    def handle_saving_preference(self, mouse_pos):
        if self.check_rect_folder.collidepoint(mouse_pos) and self.saving_inside_documents:
            self.saving_inside_documents = False
            self.update_theme_texts()
        elif self.check_rect_document.collidepoint(mouse_pos) and not self.saving_inside_documents:
            if os.path.exists(self.get_documents_path()):
                self.saving_inside_documents = True
                self.update_theme_texts()

    def handle_key_input(self, event):
        if event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
            self.paste_from_clipboard()
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        elif not (event.mod & pygame.KMOD_CTRL and event.key == pygame.K_v):
            self.input_text += event.unicode

    def paste_from_clipboard(self):
        clipboard_text = pygame.scrap.get(pygame.SCRAP_TEXT)
        if clipboard_text:
            try:
                pasted_text = clipboard_text.decode('utf-8').replace('\x00', '')
                self.input_text += pasted_text
            except UnicodeDecodeError:
                pass

    def draw_interface(self):
        self.screen.fill(self.current_theme.background)
        
        self.screen.blit(self.title_text, (50, 50))
        
        pygame.draw.rect(self.screen, self.current_theme.input_color if self.active else self.current_theme.background, self.input_rect)
        pygame.draw.rect(self.screen, self.current_theme.border, self.input_rect, 2)
        text_surface = self.font.render(self.input_text, True, self.current_theme.text)
        self.screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        
        pygame.draw.rect(self.screen, self.current_theme.button, self.button_rect)
        self.screen.blit(self.button_text, (self.button_rect.x + 5, self.button_rect.y + 10))
        
        pygame.draw.rect(self.screen, self.current_theme.button, self.save_btn_rect)
        self.screen.blit(self.save_text, (self.save_btn_rect.x + 75, self.save_btn_rect.y + 10))
        
        pygame.draw.rect(self.screen, self.current_theme.button, self.clear_rect)
        self.screen.blit(self.clear_text, (self.clear_rect.x + 40, self.clear_rect.y + 10))
        
        pygame.draw.rect(self.screen, self.current_theme.border, self.preview_rect, 2)
        self.screen.blit(self.preview_title, (50, 230))
        
        pygame.draw.rect(self.screen, self.current_theme.theme_btn_bg, self.theme_btn_rect)
        theme_icon = self.sun_img if self.is_dark_theme else self.moon_img
        self.screen.blit(theme_icon, (self.theme_btn_rect.x + 5, self.theme_btn_rect.y + 5))
        
        pygame.draw.rect(self.screen, self.current_theme.theme_btn_bg, self.settings_btn_rect)
        settings_icon = self.settings_light if self.is_dark_theme else self.settings_dark
        self.screen.blit(settings_icon, (self.settings_btn_rect.x + 5, self.settings_btn_rect.y + 5))
        
        if self.qrcode_image:
            self.screen.blit(self.qrcode_image, (self.preview_rect.x + 5, self.preview_rect.y + 5))
            
        self.screen.blit(self.info_text, (50, 620))
        
        if self.settings_window_open:
            self.draw_settings_window()

    def run(self):
        """Главный цикл приложения"""
        running = True
        while running:
            running = self.handle_events()
            self.draw_interface()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

if __name__ == "__main__":
    app = QRGenerator()
    app.run()
