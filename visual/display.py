import time

from visual.button import Button
from visual.utils import *
from config import *
from simulation.cell import CellType


def run(simulation):
    pg.init()

    screen = pg.display.set_mode((WIDTH*pixel_size, HEIGHT*pixel_size), pg.RESIZABLE)

    reset_button = Button(screen, 15, pg.display.get_surface().get_size()[1] - 50, 75, 40,
                          "Reset", 24, (0, 0, 0), (0, 0, 0))
    pause_button = Button(screen, 15+75+15, pg.display.get_surface().get_size()[1] - 50, 95, 40,
                          "Play", 24, (0, 0, 0), (0, 0, 0))

    running = True
    lmb_pressed = False
    rmb_pressed = False
    paused = True
    mode = 1

    while running:
        screen.fill((255, 255, 255))  # Make background white

        if not paused:
            time.sleep(1 / FPS)
            simulation.run()
        grid = simulation.cells

        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # LMB pressed
                    lmb_pressed = True
                    display_grid_pos = get_grid_pos()
                    sim_grid_pos = (display_grid_pos[0] // pixel_size, display_grid_pos[1] // pixel_size)
                    if grid[sim_grid_pos[1], sim_grid_pos[0]].type == CellType.SOLID:
                        mode = 0  # With this mode it will remove blocks when dragged
                    else:
                        mode = 1  # With this mode it will add blocks
                    if reset_button.Rect.collidepoint(event.pos):
                        simulation.reset()
                        pg.display.flip()
                        mode = 0  # Don't draw on button when clicked
                    elif pause_button.Rect.collidepoint(event.pos):
                        if paused:
                            pause_button.change_text("Pause")
                        else:
                            pause_button.change_text("Play")
                        paused = not paused
                if event.button == 3:  # RMB
                    rmb_pressed = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:  # LMB released
                    lmb_pressed = False
                if event.button == 3:  # RMB
                    rmb_pressed = False
            elif event.type == pg.VIDEORESIZE:  # Move button so it is sticky to the bottom of the screen
                width, height = event.w, event.h
                screen = pg.display.set_mode((width, height), pg.RESIZABLE)
                reset_button.Rect.y = height - 50
                pause_button.Rect.y = height - 50

        reset_button.draw()
        pause_button.draw()

        if lmb_pressed:  # Define behavior for lmb pressed down
            display_grid_pos = get_grid_pos()
            sim_grid_pos = (display_grid_pos[0] // pixel_size, display_grid_pos[1] // pixel_size)
            if not mode:  # If block exists at pressed position then remove it
                simulation.set_cell_type(sim_grid_pos[1], sim_grid_pos[0], CellType.BLANK)
            else:
                # check if pressed on top of buttons
                if (not reset_button.Rect.collidepoint(display_grid_pos)
                        and not pause_button.Rect.collidepoint(display_grid_pos)):
                    simulation.set_cell_type(sim_grid_pos[1], sim_grid_pos[0], CellType.SOLID)

        if rmb_pressed:
            display_grid_pos = get_grid_pos()
            sim_grid_pos = (display_grid_pos[0] // pixel_size, display_grid_pos[1] // pixel_size)
            if not grid[sim_grid_pos[1], sim_grid_pos[0]].type == CellType.SOLID:
                simulation.add_liquid(sim_grid_pos[1], sim_grid_pos[0], ADDED_LIQUID_AMOUNT)

        for cell in grid.flatten():
            pixel_pos = (cell.y * pixel_size, cell.x * pixel_size)
            if cell.type == CellType.SOLID:
                pg.Surface.fill(screen, wall_color,
                                create_block(pixel_pos, pixel_size))
            elif cell.liquid > 0:
                pg.Surface.fill(screen, water_color,
                                create_block(pixel_pos, pixel_size))
        # Redraw
        pg.display.flip()

    pg.quit()
