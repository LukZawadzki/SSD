from visual.button import Button
from visual.utils import *


def run():
    pg.init()

    screen = pg.display.set_mode(screen_size, pg.RESIZABLE)

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
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # LMB pressed
                    lmb_pressed = True
                    grid_pos = get_grid_pos()
                    if wall_blocks.get(grid_pos) is not None:
                        mode = 0  # With this mode it will remove blocks when dragged
                    else:
                        mode = 1  # With this mode it will add blocks
                    if reset_button.Rect.collidepoint(event.pos):
                        reset()
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

        if not paused:
            if lmb_pressed:  # Define behavior for lmb pressed down
                grid_pos = get_grid_pos()

                if not mode:  # If block exists at pressed position then remove it
                    try:
                        wall_blocks.pop(grid_pos)
                    except KeyError:
                        pass
                else:
                    if not reset_button.Rect.collidepoint(grid_pos) and not pause_button.Rect.collidepoint(grid_pos):
                        wall_blocks.update({grid_pos: create_block(grid_pos, pixel_size)})  # else add it
                        try:
                            water_blocks.pop(grid_pos)  # Try to remove water if adding wall on top of it
                        except KeyError:
                            pass

            if rmb_pressed:
                grid_pos = get_grid_pos()
                if grid_pos not in wall_blocks.keys():  # Don't put water on walls
                    water_blocks.update({grid_pos: create_block(grid_pos, pixel_size)})

        for key in wall_blocks.keys():
            pg.Surface.fill(screen, wall_color, wall_blocks[key])  # Add every wall to surface
        for key in water_blocks.keys():
            pg.Surface.fill(screen, water_color, water_blocks[key])
        # Redraw
        pg.display.flip()

    pg.quit()
