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
    COMPRESSION_MAX
)


class Simulation:
    def __init__(self):
        self.cells: CellGrid = np.array(
            [[Cell(x, y, CellType.BLANK) for y in range(WIDTH)] for x in range(HEIGHT)],
            dtype=Cell
        )
        self.diffs = np.zeros((HEIGHT, WIDTH))
        for cell in self.cells.flatten():
            self.initiate_cell_neighbors(cell)

    def initiate_cell_neighbors(self, cell: Cell):
        """Initializes the neighbors of a cell."""

        if cell.x - 1 >= 0:
            cell.top = self.cells[cell.x - 1, cell.y]

        if cell.x + 1 < HEIGHT:
            cell.bottom = self.cells[cell.x + 1, cell.y]

        if cell.y - 1 >= 0:
            cell.left = self.cells[cell.x, cell.y - 1]

        if cell.y + 1 < WIDTH:
            cell.right = self.cells[cell.x, cell.y + 1]

    @staticmethod
    def calculate_vertical_flow_value(remaining_liquid: float, destination: 'Cell'):
        """Calculates how much liquid should flow to the destination cell."""

        total = remaining_liquid + destination.liquid

        if total <= LIQUID_MAX:
            return LIQUID_MAX
        elif total < 2 * LIQUID_MAX + COMPRESSION_MAX:
            return (LIQUID_MAX * LIQUID_MAX + total * COMPRESSION_MAX) / (LIQUID_MAX + COMPRESSION_MAX)
        else:
            return (total + COMPRESSION_MAX) / 2

    @staticmethod
    def constrain_flow(flow: float, remaining_liquid: float) -> float:
        """Constraints the flow."""

        return min(max(flow, 0), min(FLOW_MAX, remaining_liquid))

    def flow_bottom(self, cell: Cell) -> float:
        """Flows the liquid to the bottom cell."""

        if cell.bottom is None or cell.bottom.type == CellType.SOLID:
            return 0

        flow = self.calculate_vertical_flow_value(cell.liquid, cell.bottom) - cell.bottom.liquid
        if cell.bottom.liquid > 0 and flow > FLOW_MIN:
            flow *= FLOW_SPEED

        flow = self.constrain_flow(flow, cell.liquid)

        if flow:
            self.diffs[cell.x, cell.y] -= flow
            self.diffs[cell.bottom.x, cell.bottom.y] += flow
            cell.bottom.settled = False

        return flow

    def flow_left(self, cell: Cell, remaining_liquid: float) -> float:
        """Flows the liquid to the left cell."""

        if cell.left is None or cell.left.type == CellType.SOLID:
            return 0

        flow = (remaining_liquid - cell.left.liquid) / 4
        if flow > FLOW_MIN:
            flow *= FLOW_SPEED

        flow = self.constrain_flow(flow, remaining_liquid)

        if flow:
            self.diffs[cell.x, cell.y] -= flow
            self.diffs[cell.left.x, cell.left.y] += flow
            cell.left.settled = False

        return flow

    def flow_right(self, cell: Cell, remaining_liquid: float) -> float:
        """Flows the liquid to the right cell."""

        if cell.right is None or cell.right.type == CellType.SOLID:
            return 0

        flow = (remaining_liquid - cell.right.liquid) / 3
        if flow > FLOW_MIN:
            flow *= FLOW_SPEED

        flow = self.constrain_flow(flow, remaining_liquid)

        if flow:
            self.diffs[cell.x, cell.y] -= flow
            self.diffs[cell.right.x, cell.right.y] += flow
            cell.right.settled = False

        return flow

    def flow_top(self, cell: Cell, remaining_liquid: float) -> float:
        """Flows the liquid to the top cell under pressure."""

        if cell.top is None or cell.top.type == CellType.SOLID:
            return 0

        flow = remaining_liquid - self.calculate_vertical_flow_value(remaining_liquid, cell.top)
        if flow > FLOW_MIN:
            flow *= FLOW_SPEED

        flow = self.constrain_flow(flow, remaining_liquid)

        if flow:
            self.diffs[cell.x, cell.y] -= flow
            self.diffs[cell.top.x, cell.top.y] += flow
            cell.top.settled = False

        return flow

    def run(self):
        """Runs the simulation."""

        print(self.cells)

        steps = 30
        while steps > 0:
            steps -= 1
            for x in range(HEIGHT):
                for y in range(WIDTH):
                    cell: Cell = self.cells[x, y]

                    if cell.settled:
                        continue

                    if not cell.liquid:
                        continue

                    if cell.liquid < LIQUID_MIN:
                        cell.liquid = 0
                        continue

                    start_liquid = cell.liquid
                    remaining_liquid = cell.liquid

                    remaining_liquid -= self.flow_bottom(cell)
                    if remaining_liquid < LIQUID_MIN:
                        self.diffs[x, y] -= remaining_liquid
                        continue

                    remaining_liquid -= self.flow_left(cell, remaining_liquid)
                    if remaining_liquid < LIQUID_MIN:
                        self.diffs[x, y] -= remaining_liquid
                        continue

                    remaining_liquid -= self.flow_right(cell, remaining_liquid)
                    if remaining_liquid < LIQUID_MIN:
                        self.diffs[x, y] -= remaining_liquid
                        continue

                    remaining_liquid -= self.flow_top(cell, remaining_liquid)
                    if remaining_liquid < LIQUID_MIN:
                        self.diffs[x, y] -= remaining_liquid
                        continue

                    if remaining_liquid != start_liquid:
                        cell.unsettle_neighbors()

            for x in range(HEIGHT):
                for y in range(WIDTH):
                    diff = self.diffs[x, y]
                    if diff:
                        self.cells[x, y].liquid += diff

            self.diffs = np.zeros((HEIGHT, WIDTH))

            print()
            print(self.cells)
