from visual.utils import *
from config import *
import pygame_widgets
import pygame as pg
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox


class CustomSlider:
    def __init__(self, screen: pg.Surface, font:pg.font, x: int, y: int, width: int,
                 height: int, min_value: float, max_value: float, step: float, text: str):
        pg.font.init()
        self.screen = screen
        self.font = font
        self.x = x
        self.y = y

        self.slider = Slider(self.screen, x, y, width, height, min=min_value, max=max_value, step=step)
        self.output = TextBox(self.screen, x + width//2 - 10, y-height-10, 25, 25, fontSize=14)
        self.output.disable()
        self.slider_text = self.font.render(text, False, (0, 0, 0))

    def draw(self) -> None:
        self.screen.blit(self.slider_text, (self.x-10, self.y + 20))
        self.output.setText(round(self.slider.getValue(), 1))

    def get_value(self, precision=1) -> float:
        return round(self.slider.getValue(), precision)
