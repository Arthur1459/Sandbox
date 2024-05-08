# Game configuration (Must be non-mutable)
from pygame import font as f
f.init()

game_name = "WS1"
version = 1.0

window_default_size = (825, 825)
fullscreen = False
default_font = f.Font("ressources/pixel.ttf", 16)  # set the font

fps = 60
step_by_step = True

mutation_size, traitor_proba = 10, 1
commun_energy_lost, replication_lost, reproduction_lost, attack_lost = 5, 0.4, 0.6, 0.9
attack_recuperation = 1
food_growth = 0.1

germs, altruist_germs, selfish_germs = 10, 0, 0
rocs_proportion, roc_size = 75, 10

n = 12
grid_line, grid_col = n**2 + 1, n**2 + 1
grid_size = (grid_line, grid_col)
cell_default_size = window_default_size[0] // grid_line

cell_default_color = (255, 255, 255)
