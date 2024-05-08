# Global variables used by the game
import config as cf

window_size = cf.window_default_size
win_width, win_height = window_size[0], window_size[1]
middle = (win_width // 2, win_height // 2)

window = None
clock = None

running = False
has_start = False
# In game
inputs = {}
fps = cf.fps
dt = 1/fps
time_factor = cf.time_factor
wait_key, t_key = True, 0

cursor = (0, 0)
info_txt = ""
seg_to_draw = []
points_to_draw = []

id = 0
grid = [[[] for col in range(cf.grid_factor)] for line in range(cf.grid_factor)]
entities = {}
entities_list = []

n_acceleration = 0
