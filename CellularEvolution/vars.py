# Global variables used by the game
import config as cf

window_size = cf.window_default_size
win_width, win_height = window_size[0], window_size[1]

cell_size = cf.cell_default_size

window = None
clock = None

running = False
running_sym = False

# In game
inputs = {}
fps, next_step = 0, True

grids, grid_index = [[], []], 0
grid = grids[grid_index]

mode = 'potential'
food_factor = 1

info_txt = ""
nb_entity = 0
general_genetics = {'move': 0, 'replicate': 0, 'share': 0, 'attack': 0,
                    'soil_preference': 0, 'friend_preference': 0, 'attack_preference': 0}
nb_teams, teams = 0, {}
teams_colors = {}
