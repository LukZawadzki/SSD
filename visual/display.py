from visual.button import Button
from visual.utils import *
from config import *
from simulation.cell import CellType
from simulation.cell import Cell


def run(simulation):
    pg.init()

    screen = pg.display.set_mode((WIDTH * PIXEL_SIZE, HEIGHT * PIXEL_SIZE), pg.RESIZABLE)

    reset_button = Button(screen, 15, pg.display.get_surface().get_size()[1] - 50, 75, 40,
                          "Reset", 24, (0, 0, 0), (0, 0, 0))
    pause_button = Button(screen, 15+75+15, pg.display.get_surface().get_size()[1] - 50, 95, 40,
                          "Play", 24, (0, 0, 0), (0, 0, 0))

    running = True
    lmb_pressed = False
    rmb_pressed = False
    paused = True
    mode = 1

    clock = pg.time.Clock()
    font = pg.font.Font(None, 36)

    cycle = 0
    grid = simulation.cells
    unsettled_cells = [cell for row in grid for cell in row if not cell.settled]
    while running:
        screen.fill((255, 255, 255))  # Make background white

        if not paused:
            # time.sleep(1 / FPS)
            clock.tick(FPS)
            simulation.run()
            cycle += 1
            grid = simulation.cells
            unsettled_cells = [cell for row in grid for cell in row if not cell.settled]

        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # LMB pressed
                    lmb_pressed = True
                    display_grid_pos = get_grid_pos()
                    sim_grid_pos = (display_grid_pos[0] // PIXEL_SIZE, display_grid_pos[1] // PIXEL_SIZE)
                    if grid[sim_grid_pos[1], sim_grid_pos[0]].type == CellType.SOLID:
                        mode = 0  # With this mode it will remove blocks when dragged
                    else:
                        mode = 1  # With this mode it will add blocks
                    if reset_button.Rect.collidepoint(event.pos):
                        simulation.reset()
                        pg.display.flip()
                        cycle = 0
                        mode = 0  # Don't draw on button when clicked
                        unsettled_cells = []
                        simulation.run()
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

        if lmb_pressed:  # Define behavior for lmb pressed down
            display_grid_pos = get_grid_pos()
            sim_grid_pos = (display_grid_pos[0] // PIXEL_SIZE, display_grid_pos[1] // PIXEL_SIZE)
            if not mode:  # If block exists at pressed position then remove it
                simulation.set_cell_type(sim_grid_pos[1], sim_grid_pos[0], CellType.BLANK)
                # Update display even if simulation is paused
                for cell in unsettled_cells:
                    if cell.x == sim_grid_pos[1] and cell.y == sim_grid_pos[0]:
                        cell.type = CellType.BLANK
                        cell.liquid = 0
                        break
            else:
                # check if pressed on top of buttons
                if (not reset_button.Rect.collidepoint(display_grid_pos)
                        and not pause_button.Rect.collidepoint(display_grid_pos)):
                    simulation.set_cell_type(sim_grid_pos[1], sim_grid_pos[0], CellType.SOLID)
                    # Update display even when simulation is paused
                    # FIXME: when adding walls while sim is running, it only draws every other wall,
                    #  but when water is splashed it refreshes itself and draws it fully
                    found_cell = False

                    # NOTE: seems to work fine with below code commented out, but I thought that it'd be
                    # impossible without it to add block on water, but somehow it seems to work?

                    # for cell in unsettled_cells:
                    #     if cell.x == sim_grid_pos[1] and cell.y == sim_grid_pos[0]:
                    #         cell.type = CellType.SOLID
                    #         cell.liquid = 0
                    #         found_cell = True
                    #         break
                    if not found_cell:
                        cell_to_add = Cell(sim_grid_pos[1], sim_grid_pos[0], CellType.SOLID)
                        cell_to_add.settled = False
                        unsettled_cells.append(cell_to_add)

                    # TODO: Still when moving mouse fast it skips to draw some cells, but water reveals them

        if rmb_pressed:
            display_grid_pos = get_grid_pos()
            sim_grid_pos = (display_grid_pos[0] // PIXEL_SIZE, display_grid_pos[1] // PIXEL_SIZE)
            if not grid[sim_grid_pos[1], sim_grid_pos[0]].type == CellType.SOLID:
                simulation.add_liquid(sim_grid_pos[1], sim_grid_pos[0], ADDED_LIQUID_AMOUNT)
                # Update display even when simulation is paused
                found_cell = False
                for cell in unsettled_cells:
                    if cell.x == sim_grid_pos[1] and cell.y == sim_grid_pos[0]:
                        cell.add_liquid(ADDED_LIQUID_AMOUNT)
                        found_cell = True
                        break
                if not found_cell:
                    cell_to_add = Cell(sim_grid_pos[1], sim_grid_pos[0], CellType.BLANK)
                    cell_to_add.add_liquid(ADDED_LIQUID_AMOUNT)
                    unsettled_cells.append(cell_to_add)

        for cell in unsettled_cells:
            pixel_pos = (cell.y * PIXEL_SIZE, cell.x * PIXEL_SIZE)
            top_occupied = True if cell.top and cell.top.liquid > 0 else False
            if cell.type == CellType.SOLID:  # Walls
                pg.Surface.fill(screen, wall_color,
                                create_block(pixel_pos, PIXEL_SIZE, PIXEL_SIZE))
            elif cell.liquid > 0:  # Water
                scaled_color = calc_color_from_pressure(cell.liquid)
                if not top_occupied:
                    pg.Surface.fill(screen, scaled_color,
                                    create_block(pixel_pos, PIXEL_SIZE, min(PIXEL_SIZE, cell.liquid*PIXEL_SIZE)))
                else:
                    pg.Surface.fill(screen, scaled_color,
                                    create_block(pixel_pos, PIXEL_SIZE, PIXEL_SIZE))
        # Redraw
        display_fps(clock, font, screen)
        pg.display.set_caption(f'current cycle: {cycle}')
        reset_button.draw()
        pause_button.draw()
        pg.display.flip()

    pg.quit()
