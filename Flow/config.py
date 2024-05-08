# configuration (non-mutable)

game_name = "Flow"
version = 1.0

debug = False
full_debug = False


modes = ['rectangle', 'circle', 'corridor']
gravity_modes = ['no', 'down', 'right-middle', 'central', 'extern', 'right', 'left', 'up', 'cursor']
mode = 'rectangle'
gravity_mode = 'down'

window_default_size = (1200, 850)
fullscreen = False
fps, dt_ref = 120, 1/120
time_factor = 2
fps_treshold = 0.25
persistence = 255

circle_base_radius = 400
rect_base_size = (1000, 800)
corridor_base_height = 800
particle_base_size = 8

grid_factor = min(window_default_size) // particle_base_size + 1

gravity = 200
viscosity = 0.005

