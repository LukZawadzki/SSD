import pygame as pg

# Constants
screen_size = [700, 700]

pixel_size = 10
wall_color = (0, 0, 0)  # Black
water_color = (173, 216, 230)  # Light Blue


def create_block(position, size):
    block = pg.Rect(position[0], position[1], size, size)
    return block


def get_grid_pos():
    pos = pg.mouse.get_pos()  # Get current mouse position

    # Change coordinates to grid - so that when pressed in [0, pixel_size) pos stays as 0,
    # in [pixel_size, 2*pixel_size) it equals 1*pixel_size and so on
    return (pos[0] // pixel_size) * pixel_size, (pos[1] // pixel_size) * pixel_size
