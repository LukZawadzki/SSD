import pygame as pg

# Constants
screen_size = [700, 700]

pixel_size = 10
wall_color = (0, 0, 0)  # Black
water_color = (173, 216, 230)  # Light Blue
dark_water = (0, 25, 50)


def create_block(position, size):
    block = pg.Rect(position[0], position[1], size, size)
    return block


def get_grid_pos():
    pos = pg.mouse.get_pos()  # Get current mouse position

    # Change coordinates to grid - so that when pressed in [0, pixel_size) pos stays as 0,
    # in [pixel_size, 2*pixel_size) it equals 1*pixel_size and so on
    return (pos[0] // pixel_size) * pixel_size, (pos[1] // pixel_size) * pixel_size


def calc_color_from_pressure(pressure):
    f = min(pressure/4, 1)
    r = int(water_color[0] + (dark_water[0] - water_color[0])*f)
    g = int(water_color[1] + (dark_water[1] - water_color[1])*f)
    b = int(water_color[2] + (dark_water[2] - water_color[2])*f)
    return r, g, b
