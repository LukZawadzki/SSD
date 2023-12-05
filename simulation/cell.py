from enum import Enum
from typing import Any

import numpy as np


class CellType(Enum):
    BLANK = 0
    SOLID = 1


class Cell:
    def __init__(self, x: int, y: int, _type: CellType):
        self.x = x
        self.y = y
        self.type = _type
        self.liquid = 0
        self.settled = True

        self.top: Cell | None = None
        self.bottom: Cell | None = None
        self.left: Cell | None = None
        self.right: Cell | None = None

        self.liquid_to_add = 0
        self.next_type = _type

    def __repr__(self):
        # return f'<Cell x={self.x} y={self.y} liquid={self.liquid}>'
        return (f'{self.liquid:.1f}' if self.liquid else '' if self.type == CellType.BLANK else 'XXX').center(3)

    def add_liquid(self, amount: float):
        """Adds liquid to the cell."""

        self.liquid += amount
        self.settled = False

    def set_type(self, new_type: CellType):
        """Sets the type of the cell."""

        self.type = new_type
        if self.type == CellType.SOLID:
            self.liquid = 0

        self.unsettle_neighbors()

    def unsettle_neighbors(self):
        """Unsettles the cell's neighbors."""

        if self.top:
            self.top.settled = False

        if self.bottom:
            self.bottom.settled = False

        if self.left:
            self.left.settled = False

        if self.right:
            self.right.settled = False


CellGrid = np.ndarray[Any, np.dtype[Cell]]  # TODO: make the type hints actually work
