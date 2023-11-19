from numba import njit
import numpy as np
import glm
import math
from nanostack_module.stack_builder import stack_builder


#stack_csv_path = r"C:\Users\egurtan\Desktop\NEW_TEST\NanotechGame-main\MOSFET\stack_description_mosfet.csv"
stack_csv_path = r"C:\Users\egurtan\Desktop\NEW_TEST\NanotechGame-main\DEMO\stack_description_heitz.csv"


grid_states, material_df = stack_builder(stack_csv_path)
grid = grid_states[-1]

WIN_RES = glm.vec2(1600,900)
# chunk
CHUNK_SIZE = max(grid.num_x,grid.num_y,grid.num_z)#max([grid.num_x, grid.num_y, grid.num_z])#20
H_CHUNK_SIZE = CHUNK_SIZE // 2
CHUNK_AREA = CHUNK_SIZE * CHUNK_SIZE
CHUNK_VOL = CHUNK_AREA * CHUNK_SIZE

ASPECT_RATIO = WIN_RES.x / WIN_RES.y
FOV_DEG = 50
V_FOV = glm.radians(FOV_DEG)  # vertical FOV
H_FOV = 2 * math.atan(math.tan(V_FOV * 0.5) * ASPECT_RATIO)  # horizontal FOV
NEAR = 0.1
FAR = 2000.0
PITCH_MAX = glm.radians(89)

# player
PLAYER_SPEED = 0.05
PLAYER_ROT_SPEED = 0.003
PLAYER_POS = glm.vec3(H_CHUNK_SIZE, CHUNK_SIZE, 1.5*CHUNK_SIZE)
MOUSE_SENSITIVITY = 0.002

BG_COLOR = glm.vec3(0.1, 0.16, 0.25)

#######
# max_dimension =
# CHUNK_SIZE = max_dimension
# CHUNK_VOL = max_dimension ** 3

