from visual import display
from simulation.cell import CellType
from simulation.simulation import Simulation

simulation = Simulation()

simulation.cells[2, 7].add_liquid(6.0)
simulation.cells[1, 2].add_liquid(4.0)
simulation.cells[5, 7].set_type(CellType.SOLID)
simulation.cells[5, 6].set_type(CellType.SOLID)
simulation.cells[5, 8].set_type(CellType.SOLID)
simulation.cells[4, 5].set_type(CellType.SOLID)
simulation.cells[4, 9].set_type(CellType.SOLID)

simulation.run()

display.run(simulation)
