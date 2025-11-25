class Toothpick:
    """
    Класс, представляющий одну зубочистку в фрактале
    """

    def __init__(self, x, y, length, direction):
        """
        Инициализация зубочистки
        аргументы:
            x (float): X-координата центра
            y (float): Y-координата центра
            length (int): Длина зубочистки
            direction (str): Направление ('H' - горизонтальная  или 'V' - вертикальная)
        """
        self.x = x
        self.y = y
        self.length = length
        self.direction = direction

    def get_endpoints(self):
        """
        Возвращает координаты конечных точек зубочистки
            tuple: ((x1, y1), (x2, y2)) - координаты двух концов
        """
        half_length = self.length / 2

        if self.direction == 'H':
            return (
                (self.x - half_length, self.y),
                (self.x + half_length, self.y)
            )
        else:  # 'V'
            return (
                (self.x, self.y - half_length),
                (self.x, self.y + half_length)
            )

    def draw(self, surface, color, thickness, offset_x, offset_y, scale):
        """
        Рисует зубочистку на поверхности pygame с учетом трансформации
        аргументы:
            surface: Поверхность pygame для рисования
            color (tuple): RGB цвет
            thickness (int): Толщина линии
            offset_x (float): Смещение по X
            offset_y (float): Смещение по Y
            scale (float): Масштаб
        """
        import pygame

        endpoints = self.get_endpoints()
        p1 = (
            (endpoints[0][0] - offset_x) * scale,
            (endpoints[0][1] - offset_y) * scale
        )
        p2 = (
            (endpoints[1][0] - offset_x) * scale,
            (endpoints[1][1] - offset_y) * scale
        )

        pygame.draw.line(surface, color, p1, p2, max(1, int(thickness * scale)))

    def __eq__(self, other):
        """Сравнение зубочисток по координатам и направлению"""
        if not isinstance(other, Toothpick):
            return False
        return (self.x == other.x and
                self.y == other.y and
                self.direction == other.direction)

    def __hash__(self):
        """Хеш для использования в множествах"""
        return hash((self.x, self.y, self.direction))
