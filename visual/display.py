import pygame_widgets

from config import *
from simulation import Simulation, Cell, CellType
from .button import Button
from .slider import CustomSlider
from .utils import *


def run(simulation: Simulation):
    pg.init()
    pg.font.init()

    screen = pg.display.set_mode((WIDTH * PIXEL_SIZE, HEIGHT * PIXEL_SIZE + 125))

    reset_button = Button(screen, 15, pg.display.get_surface().get_size()[1] - 50, 75, 40,
                          "Reset", 24, (0, 0, 0), (0, 0, 0))
    pause_button = Button(screen, 15+75+15, pg.display.get_surface().get_size()[1] - 50, 95, 40,
                          "Play", 24, (0, 0, 0), (0, 0, 0))

    running = True
    lmb_pressed = False
    rmb_pressed = False
    s_pressed = False
    d_pressed = False
    paused = True
    placing_mode = True

    my_font = pg.font.SysFont('Arial', 16, True)

    clock = pg.time.Clock()
    font = pg.font.Font(None, 36)

    added_liquid_slider = CustomSlider(screen, my_font, 170, pg.display.get_surface().get_size()[1] - 95,
                                       120, 20, 0.1, 10, 0.1, "Add liquid amount", ADDED_LIQUID_AMOUNT)
    compression_slider = CustomSlider(screen, my_font, 320, pg.display.get_surface().get_size()[1] - 95,
                                      120, 20, 0.1, 1, 0.05, "Fluid compression", COMPRESSION_MAX)

    flow_slider = CustomSlider(screen, my_font, 20, pg.display.get_surface().get_size()[1] - 95,
                               120, 20, 0.1, 1, 0.1, "Flow rate", FLOW_SPEED)
    iterations_slider = CustomSlider(screen, my_font, 470, pg.display.get_surface().get_size()[1] - 95,
                                     120, 20, 1, 6, 1, "Sim speed", ITERATIONS_PER_FRAME)

    info_text = my_font.render("Hold 's' or 'd' to create source or drain", False, (0, 0, 0))

    prev_compression, current_compression = COMPRESSION_MAX, COMPRESSION_MAX
    prev_flow, current_flow = FLOW_SPEED, FLOW_SPEED
    prev_iter, current_iter = ITERATIONS_PER_FRAME, ITERATIONS_PER_FRAME
    prev_sim_grid_pos: tuple[int, int] | None = None

    cycle = 0
    grid = simulation.cells
    cells_to_display = set([cell for row in grid for cell in row if not cell.settled])
    while running:
        screen.fill((255, 255, 255))  # Make background white
        screen.blit(info_text, (250, pg.display.get_surface().get_size()[1] - 30))
        pg.draw.line(screen, (0, 0, 0), (0, HEIGHT*PIXEL_SIZE), (WIDTH*PIXEL_SIZE, HEIGHT*PIXEL_SIZE))

        if not paused:
            # time.sleep(1 / FPS)
            clock.tick(FPS)
            cells_to_display = simulation.run()
            cycle += 1

        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # LMB pressed
                    lmb_pressed = True
                    display_grid_pos = get_grid_pos()
                    sim_grid_pos = (display_grid_pos[0] // PIXEL_SIZE, display_grid_pos[1] // PIXEL_SIZE)
                    if display_grid_pos[1] < HEIGHT*PIXEL_SIZE:  # Check if within simulation space
                        if grid[sim_grid_pos[1], sim_grid_pos[0]].type in [CellType.SOLID, CellType.DRAIN, CellType.SOURCE]:
                            placing_mode = False  # With this mode it will remove blocks when dragged
                        else:
                            placing_mode = True
                    if reset_button.Rect.collidepoint(event.pos):
                        simulation.reset()
                        pg.display.flip()
                        cycle = 0
                        placing_mode = 0  # Don't draw on button when clicked
                        cells_to_display = simulation.run()
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
                    prev_sim_grid_pos = None
                if event.button == 3:  # RMB
                    rmb_pressed = False
            elif event.type == pg.KEYDOWN:  # Keyboard press
                if event.key == pg.K_s:
                    s_pressed = True
                elif event.key == pg.K_d:
                    d_pressed = True
            elif event.type == pg.KEYUP:
                if event.key == pg.K_s:
                    s_pressed = False
                elif event.key == pg.K_d:
                    d_pressed = False

        added_liquid_slider.draw()
        compression_slider.draw()
        flow_slider.draw()
        iterations_slider.draw()

        current_flow = flow_slider.get_value(2)
        current_iter = int(iterations_slider.get_value())
        current_compression = compression_slider.get_value(2)

        if current_flow != prev_flow:
            simulation.flow_speed = current_flow
            prev_flow = current_flow

        if current_iter != prev_iter:
            simulation.iterations_per_frame = current_iter
            prev_iter = current_iter

        if current_compression != prev_compression:
            simulation.compression_max = current_compression
            prev_compression = current_compression

        liquid_amount = added_liquid_slider.get_value()
        pygame_widgets.update(events)

        if lmb_pressed:  # Define behavior for lmb pressed down
            display_grid_pos = get_grid_pos()

            if display_grid_pos[1] < HEIGHT*PIXEL_SIZE and 0 <= display_grid_pos[0] < WIDTH*PIXEL_SIZE:
                sim_grid_pos = (display_grid_pos[0] // PIXEL_SIZE, display_grid_pos[1] // PIXEL_SIZE)
                pos_changed = sim_grid_pos != prev_sim_grid_pos
                prev_sim_grid_pos = sim_grid_pos

                if not placing_mode and pos_changed:  # If block exists at pressed position then remove it
                    simulation.set_cell_type(sim_grid_pos[1], sim_grid_pos[0], CellType.BLANK)
                    # Update display even if simulation is paused
                    cell_to_delete = next(
                        (
                            cell for cell in cells_to_display 
                            if cell.x == sim_grid_pos[1] and cell.y == sim_grid_pos[0]
                        ), None
                    )
                    if cell_to_delete:
                        cells_to_display.remove(cell_to_delete)

                elif pos_changed:
                    # check if pressed on top of buttons
                    if (not reset_button.Rect.collidepoint(display_grid_pos)
                            and not pause_button.Rect.collidepoint(display_grid_pos)):
                        if s_pressed:
                            simulation.set_cell_type(sim_grid_pos[1], sim_grid_pos[0], CellType.SOURCE)
                            cell_to_add = Cell(sim_grid_pos[1], sim_grid_pos[0], CellType.SOURCE)
                            cell_to_add.settled = False
                        elif d_pressed:
                            simulation.set_cell_type(sim_grid_pos[1], sim_grid_pos[0], CellType.DRAIN)
                            cell_to_add = Cell(sim_grid_pos[1], sim_grid_pos[0], CellType.DRAIN)
                            cell_to_add.settled = False
                        else:
                            simulation.set_cell_type(sim_grid_pos[1], sim_grid_pos[0], CellType.SOLID)
                            cell_to_add = Cell(sim_grid_pos[1], sim_grid_pos[0], CellType.SOLID)
                            cell_to_add.settled = False
                        cells_to_display.add(cell_to_add)

        if rmb_pressed:
            display_grid_pos = get_grid_pos()
            if display_grid_pos[1] < HEIGHT * PIXEL_SIZE and 0 <= display_grid_pos[0] < WIDTH*PIXEL_SIZE:
                sim_grid_pos = (display_grid_pos[0] // PIXEL_SIZE, display_grid_pos[1] // PIXEL_SIZE)
                if not grid[sim_grid_pos[1], sim_grid_pos[0]].type in [CellType.SOLID, CellType.DRAIN, CellType.SOURCE]:
                    simulation.add_liquid(sim_grid_pos[1], sim_grid_pos[0], liquid_amount)

                    if paused:
                        # Update display even when simulation is paused
                        found_cell = False
                        for cell in cells_to_display:
                            if cell.x == sim_grid_pos[1] and cell.y == sim_grid_pos[0]:
                                found_cell = True
                                break

                        if not found_cell:
                            cell_to_add = Cell(sim_grid_pos[1], sim_grid_pos[0], CellType.BLANK)
                            cell_to_add.add_liquid(liquid_amount)
                            cells_to_display.add(cell_to_add)

        # print(len(cells_to_display))
        for cell in cells_to_display:
            pixel_pos = (cell.y * PIXEL_SIZE, cell.x * PIXEL_SIZE)
            is_falling = cell.top and cell.top.liquid and cell.top.flowing_down

            if cell.type == CellType.SOLID:  # Walls
                pg.Surface.fill(screen, WALL_COLOR, create_block(pixel_pos, PIXEL_SIZE, PIXEL_SIZE))
            elif cell.type == CellType.SOURCE:
                pg.Surface.fill(screen, SOURCE_COLOR, create_block(pixel_pos, PIXEL_SIZE, PIXEL_SIZE))
            elif cell.type == CellType.DRAIN:
                pg.Surface.fill(screen, DRAIN_COLOR, create_block(pixel_pos, PIXEL_SIZE, PIXEL_SIZE))
            elif cell.liquid > LIQUID_MIN:  # Water
                scaled_color = calc_color_from_pressure(cell.liquid)
                if not is_falling:
                    pg.Surface.fill(
                        screen,
                        scaled_color,
                        create_block(pixel_pos, PIXEL_SIZE, min(PIXEL_SIZE, cell.liquid*PIXEL_SIZE))
                    )
                else:
                    pg.Surface.fill(
                        screen,
                        scaled_color,
                        create_block(pixel_pos, PIXEL_SIZE, PIXEL_SIZE)
                    )

        # Redraw
        display_fps(clock, font, screen)
        pg.display.set_caption(f'Current cycle: {cycle}')
        reset_button.draw()
        pause_button.draw()
        pg.display.flip()

    pg.quit()
