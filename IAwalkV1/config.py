# configuration (non-mutable)

game_name = "Flow"
version = 1.0

debug = False
full_debug = False

nb_cluster = 5
nb_body = 6

collision = False

modes = ['rectangle', 'circle', 'corridor']
gravity_modes = ['no', 'down', 'right-middle', 'central', 'extern', 'right', 'left', 'up', 'cursor']
mode = 'rectangle'
gravity_mode = 'down'

window_default_size = (1300, 850)
fullscreen = False
fps, dt_ref = 120, 1/120
time_factor = 2
fps_treshold = 0.25
persistence = 255

circle_base_radius = 400
rect_base_size = (1200, 400)
corridor_base_height = 800
particle_base_size = 6

grid_factor = min(window_default_size) // particle_base_size + 1

gravity = 1000/time_factor
viscosity = 0.005

start_pos = (150, 540)
target = 1100
