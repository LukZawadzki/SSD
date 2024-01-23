import pygame as pg
import math


class Recorder:
    def __init__(
        self, filename: str, font: pg.font.Font, cols: int = 5, frequency: int = 20
    ):
        self._filename = filename
        self._font = font
        self._surfaces: list[pg.Surface] = []
        self._cols = cols
        self._frequency = frequency
        self._start_cycle = 0

    def start(self):
        self._surfaces = []

    def stop(self):
        total = len(self._surfaces)
        cols = min(self._cols, total)
        rows = math.ceil(total / cols)

        surface = pg.Surface(
            size=(
                self._surfaces[0].get_width() * cols,
                self._surfaces[0].get_height() * rows,
            )
        )
        surface.fill((255, 255, 255))
        for i, s in enumerate(self._surfaces):
            x = (i % cols) * s.get_width()
            y = (i // cols) * s.get_height()
            surface.blit(s, (x, y))

        pg.image.save(surface, self._filename)
        self._surfaces = []

    def record(self, surface: pg.Surface, cycle: int):
        if cycle % self._frequency != 0:
            return

        if not self._surfaces:
            self._start_cycle = cycle

        surface = surface.copy()
        text = self._font.render(f"Cycle: {cycle - self._start_cycle}", True, (0, 0, 0))
        surface.blit(text, (10, 10))
        self._surfaces.append(surface.convert())
