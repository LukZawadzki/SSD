import pygame as pg
from config import *


def display_fps(clock, font, screen):
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (0,0,0))
    screen.blit(fps_text, (10, 10))


def create_block(position, width, height):
    return pg.Rect(position[0], position[1]+PIXEL_SIZE-height, width, height+1)


def get_grid_pos():
    pos = pg.mouse.get_pos()  # Get current mouse position

    # Change coordinates to grid - so that when pressed in [0, pixel_size) pos stays as 0,
    # in [pixel_size, 2*pixel_size) it equals 1*pixel_size and so on
    return (pos[0] // PIXEL_SIZE) * PIXEL_SIZE, (pos[1] // PIXEL_SIZE) * PIXEL_SIZE


def calc_color_from_pressure(pressure):
    f = min(pressure/4, 1)
    r = int(WATER_COLOR[0] + (DARK_WATER_COLOR[0] - WATER_COLOR[0]) * f)
    g = int(WATER_COLOR[1] + (DARK_WATER_COLOR[1] - WATER_COLOR[1]) * f)
    b = int(WATER_COLOR[2] + (DARK_WATER_COLOR[2] - WATER_COLOR[2]) * f)
    return r, g, b
