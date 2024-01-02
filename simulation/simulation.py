import numpy as np

from .cell import Cell, CellType, CellGrid
from config import (
    WIDTH,
    HEIGHT,
    LIQUID_MAX,
    LIQUID_MIN,
    FLOW_MAX,
    FLOW_MIN,
    FLOW_SPEED,
    COMPRESSION_MAX,
    ITERATIONS_PER_FRAME,
    SOURCE_LIQUID_PER_ITERATION,
    DRAIN_LIQUID_PER_ITERATION
)


class Simulation:
    def __init__(self):
        self.cells: CellGrid = np.array(
            [[Cell(x, y, CellType.BLANK) for y in range(WIDTH)] for x in range(HEIGHT)],
            dtype=Cell
        )
        self.diffs = np.zeros((HEIGHT, WIDTH))
        for cell in self.cells.flatten():
            self._init_cell_neighbors(cell)

        self.compression_max = COMPRESSION_MAX
        self.flow_speed = FLOW_SPEED
        self.iterations_per_frame = ITERATIONS_PER_FRAME

    def _init_cell_neighbors(self, cell: Cell):
        """Initializes the neighbors of a cell."""

        if cell.x - 1 >= 0:
            cell.top = self.cells[cell.x - 1, cell.y]

        if cell.x + 1 < HEIGHT:
            cell.bottom = self.cells[cell.x + 1, cell.y]

        if cell.y - 1 >= 0:
            cell.left = self.cells[cell.x, cell.y - 1]

        if cell.y + 1 < WIDTH:
            cell.right = self.cells[cell.x, cell.y + 1]

    def _calculate_vertical_flow_value(self, remaining_liquid: float, destination: Cell):
        """Calculates how much liquid the destination cell can take."""

        total = remaining_liquid + destination.liquid

        if total <= LIQUID_MAX:
            return LIQUID_MAX
        elif total < 2 * LIQUID_MAX + self.compression_max:
            return (LIQUID_MAX * LIQUID_MAX + total * self.compression_max) / (LIQUID_MAX + self.compression_max)
        else:
            return (total + self.compression_max) / 2

    @staticmethod
    def _constrain_flow(flow: float, remaining_liquid: float) -> float:
        """Constraints the flow."""

        return min(max(flow, 0), min(FLOW_MAX, remaining_liquid))

    def _flow_bottom(self, cell: Cell) -> float:
        """Flows the liquid to the bottom cell."""

        if cell.bottom is None or cell.bottom.type != CellType.BLANK:
            return 0

        flow = self._calculate_vertical_flow_value(cell.liquid, cell.bottom) - cell.bottom.liquid
        if cell.bottom.liquid > 0 and flow > FLOW_MIN:
            flow *= self.flow_speed

        flow = self._constrain_flow(flow, cell.liquid)

        if flow:
            self.diffs[cell.x, cell.y] -= flow
            self.diffs[cell.bottom.x, cell.bottom.y] += flow
            cell.flowing_down = True
            cell.bottom.unsettle()

        return flow

    def _flow_left(self, cell: Cell, remaining_liquid: float) -> float:
        """Flows the liquid to the left cell."""

        if cell.left is None or cell.left.type != CellType.BLANK:
            return 0

        flow = (remaining_liquid - cell.left.liquid) / 4
        if flow > FLOW_MIN:
            flow *= self.flow_speed

        flow = self._constrain_flow(flow, remaining_liquid)

        if flow:
            self.diffs[cell.x, cell.y] -= flow
            self.diffs[cell.left.x, cell.left.y] += flow
            cell.left.unsettle()

        return flow

    def _flow_right(self, cell: Cell, remaining_liquid: float) -> float:
        """Flows the liquid to the right cell."""

        if cell.right is None or cell.right.type != CellType.BLANK:
            return 0

        flow = (remaining_liquid - cell.right.liquid) / 3
        if flow > FLOW_MIN:
            flow *= self.flow_speed

        flow = self._constrain_flow(flow, remaining_liquid)

        if flow:
            self.diffs[cell.x, cell.y] -= flow
            self.diffs[cell.right.x, cell.right.y] += flow
            cell.right.unsettle()

        return flow

    def _flow_top(self, cell: Cell, remaining_liquid: float) -> float:
        """Flows the liquid to the top cell under pressure."""

        if cell.top is None or cell.top.type != CellType.BLANK:
            return 0

        flow = remaining_liquid - self._calculate_vertical_flow_value(remaining_liquid, cell.top)
        if flow > FLOW_MIN:
            flow *= self.flow_speed

        flow = self._constrain_flow(flow, remaining_liquid)

        if flow:
            self.diffs[cell.x, cell.y] -= flow
            self.diffs[cell.top.x, cell.top.y] += flow
            cell.top.unsettle()

        return flow

    def _handle_source(self, source: Cell):
        """Handles a source cell."""

        cells_to_flow = []

        if source.top and source.top.type == CellType.BLANK:
            cells_to_flow.append(source.top)

        if source.bottom and source.bottom.type == CellType.BLANK:
            cells_to_flow.append(source.bottom)

        if source.left and source.left.type == CellType.BLANK:
            cells_to_flow.append(source.left)

        if source.right and source.right.type == CellType.BLANK:
            cells_to_flow.append(source.right)

        liquid_each_cell = SOURCE_LIQUID_PER_ITERATION / len(cells_to_flow)

        for cell in cells_to_flow:
            cell.settled = False
            self.diffs[cell.x, cell.y] += liquid_each_cell

    def _handle_drain(self, drain: Cell):
        """Handles a drain cell."""

        cells_to_flow = []

        if drain.top and drain.top.type == CellType.BLANK:
            cells_to_flow.append(drain.top)

        if drain.bottom and drain.bottom.type == CellType.BLANK:
            cells_to_flow.append(drain.bottom)

        if drain.left and drain.left.type == CellType.BLANK:
            cells_to_flow.append(drain.left)

        if drain.right and drain.right.type == CellType.BLANK:
            cells_to_flow.append(drain.right)

        liquid_each_cell = DRAIN_LIQUID_PER_ITERATION / len(cells_to_flow)

        for cell in cells_to_flow:
            cell.settled = False
            self.diffs[cell.x, cell.y] -= min(liquid_each_cell, cell.liquid)

    def add_liquid(self, x: int, y: int, amount: float):
        """Adds liquid to the target cell."""

        self.cells[x, y].add_liquid(amount)

    def set_cell_type(self, x: int, y: int, _type: CellType):
        """Sets the type of the target cell."""

        self.cells[x, y].set_type(_type)

    def reset(self):
        """Resets the simulation."""

        for row in self.cells:
            for cell in row:
                cell.liquid = 0
                cell.type = CellType.BLANK

    def run(self) -> set[Cell]:
        """Runs `ITERATIONS_PER_FRAME` steps of the simulation. Returns the cells which need to be displayed."""

        cells_to_display = set()

        for i in range(1, self.iterations_per_frame + 1):
            for row in self.cells:
                for cell in row:
                    if i == self.iterations_per_frame and (cell.type == CellType.SOLID or cell.liquid >= LIQUID_MIN):
                        cells_to_display.add(cell)

                    if cell.type == CellType.SOURCE:
                        self._handle_source(cell)
                        continue

                    if cell.type == CellType.DRAIN:
                        self._handle_drain(cell)
                        continue

                    if cell.settled:
                        continue

                    if not cell.liquid:
                        continue

                    if cell.liquid < LIQUID_MIN:
                        cell.liquid = 0
                        continue

                    x, y = cell.x, cell.y

                    start_liquid = cell.liquid
                    remaining_liquid = cell.liquid

                    if cell.flowing_down:
                        cell.flowing_down = False

                    remaining_liquid -= self._flow_bottom(cell)
                    if i == self.iterations_per_frame and cell.bottom and not cell.bottom.settled:
                        cells_to_display.add(cell.bottom)

                    if remaining_liquid < LIQUID_MIN:
                        self.diffs[x, y] -= remaining_liquid
                        continue

                    remaining_liquid -= self._flow_left(cell, remaining_liquid)
                    if i == self.iterations_per_frame and cell.left and not cell.left.settled:
                        cells_to_display.add(cell.left)

                    if remaining_liquid < LIQUID_MIN:
                        self.diffs[x, y] -= remaining_liquid
                        continue

                    remaining_liquid -= self._flow_right(cell, remaining_liquid)
                    if i == self.iterations_per_frame and cell.right and not cell.right.settled:
                        cells_to_display.add(cell.right)

                    if remaining_liquid < LIQUID_MIN:
                        self.diffs[x, y] -= remaining_liquid
                        continue

                    remaining_liquid -= self._flow_top(cell, remaining_liquid)
                    if i == self.iterations_per_frame and cell.top and not cell.top.settled:
                        cells_to_display.add(cell.top)

                    if remaining_liquid < LIQUID_MIN:
                        self.diffs[x, y] -= remaining_liquid
                        continue

                    if remaining_liquid != start_liquid:
                        cell.unsettle_neighbors()
                        if i == self.iterations_per_frame:
                            if cell.top:
                                cells_to_display.add(cell.top)

                            if cell.bottom:
                                cells_to_display.add(cell.bottom)

                            if cell.left:
                                cells_to_display.add(cell.left)

                            if cell.right:
                                cells_to_display.add(cell.right)
                    else:
                        cell.settle_count += 1
                        if cell.settle_count >= 10:
                            cell.settled = True

            for x in range(HEIGHT):
                for y in range(WIDTH):
                    diff = self.diffs[x, y]
                    if diff:
                        self.cells[x, y].liquid += diff

            self.diffs = np.zeros((HEIGHT, WIDTH))

        return cells_to_display

