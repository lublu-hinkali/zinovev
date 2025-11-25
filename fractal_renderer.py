import pygame
import json
from toothpick import Toothpick


class FractalRenderer:
    """
    Основной класс для рендеринга фрактала зубочисток с автоматическим зумом
    аттрибуты:
        config (dict): Конфигурация из JSON файла
        toothpicks (list): Список всех зубочисток
        current_generation (int): Текущее поколение
        running (bool): Флаг работы приложения
    """

    def __init__(self, config_path='config.json'):
        """
        Инициализация рендерера
        аргументы:
            config_path (str): Путь к конфигурационному файлу
        """
        self.load_config(config_path)
        self.setup_pygame()
        self.reset_fractal()

    def load_config(self, config_path):
        """Загрузка конфигурации из JSON файла"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def setup_pygame(self):
        """Инициализация pygame и создание окна"""
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.config['window_width'], self.config['window_height'])
        )
        pygame.display.set_caption('Фрактал Омара Пола - Toothpick Sequence')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

    def reset_fractal(self):
        """Сброс фрактала к начальному состоянию"""
        self.toothpicks = []
        self.current_generation = 0
        self.frame_counter = 0
        self.running = True

        # Добавляем первую вертикальную зубочистку в центре
        first_toothpick = Toothpick(
            0, 0,
            self.config['toothpick_length'],
            'V'
        )
        self.toothpicks.append(first_toothpick)

        # Для отслеживания использованных конечных точек
        self.used_endpoints = set()

    def get_bounds(self):
        """
        Вычисляет границы всех зубочисток для автоматического зума
        возвращает:
            tuple: (min_x, max_x, min_y, max_y)
        """
        if not self.toothpicks:
            return (-100, 100, -100, 100)

        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')

        for toothpick in self.toothpicks:
            endpoints = toothpick.get_endpoints()
            for x, y in endpoints:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

        return (min_x, max_x, min_y, max_y)

    def calculate_zoom(self, bounds):
        """
        Вычисляет параметры зума для отображения всех зубочисток
        аргументы:
            bounds (tuple): Границы (min_x, max_x, min_y, max_y)
        возвращает:
            tuple: (offset_x, offset_y, scale)
        """
        min_x, max_x, min_y, max_y = bounds
        padding = self.config['zoom_padding']

        width = max_x - min_x
        height = max_y - min_y

        # Вычисляем масштаб, чтобы все зубочистки поместились
        scale_x = (self.config['window_width'] - 2 * padding) / max(width, 1)
        scale_y = (self.config['window_height'] - 2 * padding) / max(height, 1)
        scale = min(scale_x, scale_y)

        # Вычисляем смещение для центрирования
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        return (center_x, center_y, scale)

    def generate_next_generation(self):
        """
        Генерирует следующее поколение зубочисток согласно правилам фрактала
        Для каждой свободной конечной точки добавляет перпендикулярную зубочистку
        """
        new_toothpicks = []

        # Собираем все занятые точки
        occupied_points = set()
        for toothpick in self.toothpicks:
            endpoints = toothpick.get_endpoints()
            occupied_points.add(endpoints[0])
            occupied_points.add(endpoints[1])

        # Для каждого конца зубочистки проверяем, свободен ли он
        for toothpick in self.toothpicks:
            endpoints = toothpick.get_endpoints()

            for endpoint in endpoints:
                # Проверяем, использовали ли мы уже эту точку
                if endpoint in self.used_endpoints:
                    continue

                # Подсчитываем, сколько зубочисток касаются этой точки
                touching_count = 0
                for other in self.toothpicks:
                    other_endpoints = other.get_endpoints()
                    if endpoint in other_endpoints:
                        touching_count += 1

                # Если точка касается ровно одной зубочистки, она свободна
                if touching_count == 1:
                    # Создаем новую зубочистку перпендикулярно
                    new_direction = 'H' if toothpick.direction == 'V' else 'V'
                    new_toothpick = Toothpick(
                        endpoint[0],
                        endpoint[1],
                        self.config['toothpick_length'],
                        new_direction
                    )

                    # Проверяем, не существует ли уже такая зубочистка
                    if new_toothpick not in self.toothpicks and new_toothpick not in new_toothpicks:
                        new_toothpicks.append(new_toothpick)
                        self.used_endpoints.add(endpoint)

        self.toothpicks.extend(new_toothpicks)
        self.current_generation += 1

    def draw(self):
        """Отрисовка всех зубочисток с автоматическим зумом"""
        self.screen.fill(tuple(self.config['background_color']))

        if self.config['auto_zoom_enabled']:
            bounds = self.get_bounds()
            target_offset_x, target_offset_y, target_scale = self.calculate_zoom(bounds)

            # Плавное изменение зума
            if not hasattr(self, 'current_offset_x'):
                self.current_offset_x = target_offset_x
                self.current_offset_y = target_offset_y
                self.current_scale = target_scale
            else:
                zoom_speed = self.config['zoom_speed']
                self.current_offset_x += (target_offset_x - self.current_offset_x) * zoom_speed
                self.current_offset_y += (target_offset_y - self.current_offset_y) * zoom_speed
                self.current_scale += (target_scale - self.current_scale) * zoom_speed

            offset_x = self.current_offset_x - self.config['window_width'] / (2 * self.current_scale)
            offset_y = self.current_offset_y - self.config['window_height'] / (2 * self.current_scale)
        else:
            offset_x = -self.config['window_width'] / 2
            offset_y = -self.config['window_height'] / 2
            self.current_scale = 1.0

        # Рисуем все зубочистки
        for toothpick in self.toothpicks:
            toothpick.draw(
                self.screen,
                tuple(self.config['toothpick_color']),
                self.config['toothpick_thickness'],
                offset_x,
                offset_y,
                self.current_scale
            )

        # Отображаем информацию
        info_text = self.font.render(
            f'Generation: {self.current_generation} | Toothpicks: {len(self.toothpicks)}',
            True,
            (255, 255, 0)
        )
        self.screen.blit(info_text, (10, 10))

        pygame.display.flip()

    def handle_events(self):
        """Обработка событий pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Генерация следующего поколения по пробелу
                    if self.current_generation < self.config['max_generations']:
                        self.generate_next_generation()
                elif event.key == pygame.K_r:
                    # Сброс по клавише R
                    self.reset_fractal()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def run(self):
        """Основной цикл приложения"""
        while self.running:
            self.handle_events()

            # Автоматическая генерация поколений
            if self.current_generation < self.config['max_generations']:
                self.frame_counter += 1
                if self.frame_counter >= self.config['generation_delay']:
                    self.generate_next_generation()
                    self.frame_counter = 0

            self.draw()
            self.clock.tick(self.config['fps'])

        pygame.quit()
