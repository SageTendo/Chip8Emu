from pygame import display, draw, DOUBLEBUF, HWSURFACE


class Screen:
    def __init__(self):
        self.WIDTH = 64
        self.HEIGHT = 32
        self.scale_factor = 20
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        display.init()
        self.screen = display.set_mode((self.WIDTH * self.scale_factor, self.HEIGHT * self.scale_factor))

    def get_pixel(self, x, y):
        x_scale = x * self.scale_factor
        y_scale = y * self.scale_factor
        return self.screen.get_at((x_scale, y_scale))

    def set_pixel(self, x, y, color):
        x_base = x * self.scale_factor
        y_base = y * self.scale_factor
        draw.rect(self.screen, color, (x_base, y_base, self.scale_factor, self.scale_factor))

    def clear(self):
        self.screen.fill(self.BLACK)

    @staticmethod
    def refresh():
        display.flip()
