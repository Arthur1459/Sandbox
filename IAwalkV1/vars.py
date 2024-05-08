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
time_factor = cf.time_factor
fps, low_fps = cf.fps, False
dt, t = cf.dt_ref * time_factor, 0
dt_list = []
wait_key, t_key, key_reset = True, 0, False

make_geo, make_multi_geo, geo_pt_1, geo_pt_2, st_1, st_2, geo_pts = False, False, None, None, False, False, []

cursor = (0, 0)
info_txt = ""
seg_to_draw = []
points_to_draw = []

mode = cf.mode
gravity_mode = cf.gravity_mode
slow_mo, slow_factor = True, 0.05

circle_radius = cf.circle_base_radius
rect_size = cf.rect_base_size
corridor_height = cf.corridor_base_height
particle_size = cf.particle_base_size

id = 0
grid = [[[] for col in range(cf.grid_factor)] for line in range(cf.grid_factor)]
entities = {}
entities_list = []
geo = {}
geo_list = []

bodies = []
gen_buffer = [[] for i in range(cf.nb_cluster)]
best_gen_archive = []
best_gen, best_score = None, None
cluster, cluster_time = 0, 0
