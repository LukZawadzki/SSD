from visual import display
from simulation.cell import CellType
from simulation.simulation import Simulation

simulation = Simulation()

simulation.add_liquid(2, 7, 6.0)
simulation.add_liquid(1, 2, 4.0)
simulation.set_cell_type(5, 7, CellType.SOLID)
simulation.set_cell_type(5, 6, CellType.SOLID)
simulation.set_cell_type(5, 8, CellType.SOLID)
simulation.set_cell_type(4, 5, CellType.SOLID)
simulation.set_cell_type(4, 9, CellType.SOLID)

display.run(simulation)
