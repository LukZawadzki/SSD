import pygame as pg


class Button:
    def __init__(self, screen, x, y, width, height, text, text_size, text_color, button_color):
        self.Rect = pg.Rect(x, y, width, height)
        self.Font = pg.font.Font(None, text_size)
        self.Text = self.Font.render(text, True, text_color)
        self.screen = screen
        self.button_color = button_color

    def draw(self):
        pg.draw.rect(self.screen, self.button_color, self.Rect, 2)
        self.screen.blit(self.Text, (self.Rect.centerx - self.Text.get_width() // 2,
                                     self.Rect.centery - self.Text.get_height() // 2))
