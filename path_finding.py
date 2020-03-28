from search_algorithms import init_algorithm
import PySimpleGUI as sg
import random as rd
import platform
import pygame
import time
import os

# PySimpleGUI Look & Feel
sg.theme('DarkBrown1')

btn_font  = {'font': ('Lato', 12, 'italic'), 'pad': (5, 5)}

COMBO_TEXT = ( 44, 40, 37)
BACKGROUND = (192,192,192)

# ------------------------------------- Screen Settings ---------------------------------------
SCR_WIDTH = SCR_HEIGHT = 600
SCR_ROWS = 25 #25
SCR_COLS = 25 #25

# ------------------------------------- Maze ---------------------------------------
class Cell: # ENUM
  EMPTY = " "
  BLOCKED = "X"
  START = "S"
  GOAL  = "G"
  GOAL1 = "G1"
  GOAL2 = "G2"
  GOAL3 = "G3"
  PATH = "*"


class Maze:
  def __init__(self, rows = 25, cols = 25):
    self._rows = rows
    self._cols = cols

    self.diagonal = False
    self.random   = False
    self.ordered_search = False

    self.grid  = None

    self.start = None
    self.goals  = []
    self.visited = []

    self.clear_maze

  def add_start(self, row, col):
    self.clear_cell(row, col)
    self.grid[row][col] = Cell.START
    self.start = (row, col)
    self.visited.insert(0, (row, col))

  def add_goal(self, row, col):
    self.clear_cell(row, col)
    if len(self.goals) == 0:
      self.grid[row][col] = Cell.GOAL1
    elif len(self.goals) == 1:
      self.grid[row][col] = Cell.GOAL2
    else:
      self.grid[row][col] = Cell.GOAL3
    self.goals.append((row, col))
    self.visited.append((row, col))

  def add_blocked(self, row, col):
    self.clear_cell(row, col)
    self.grid[row][col] = Cell.BLOCKED

  def clear_cell(self, row, col):
    self.grid[row][col] = Cell.EMPTY

    if (row, col) == self.start:
      self.visited.remove(self.start)
      self.start = None
      
    if (row, col) in self.goals:
      if len(self.goals) > 1:
        self._reset_goals((row, col))
      self.goals.remove((row, col))
      self.visited.remove((row, col))

  def generate_maze(self, sparsness):
    self.clear_maze

    for r in range(self._rows):
      for c in range(self._cols):
        if rd.uniform(0, 1.0) < sparsness:
          self.grid[r][c] = Cell.BLOCKED

  def successors(self, pos):
    locations = []

    if pos[0] + 1 < self._rows and self.grid[pos[0] + 1][pos[1]] != Cell.BLOCKED:
      locations.append((pos[0] + 1, pos[1]))
    if pos[0] - 1 >= 0 and self.grid[pos[0] - 1][pos[1]] != Cell.BLOCKED:
      locations.append((pos[0] - 1, pos[1]))
    if pos[1] + 1 < self._cols and self.grid[pos[0]][pos[1] + 1] != Cell.BLOCKED:
      locations.append((pos[0], pos[1] + 1))
    if pos[1] - 1 >= 0 and self.grid[pos[0]][pos[1] - 1] != Cell.BLOCKED:
      locations.append((pos[0], pos[1] - 1))

    if self.diagonal:
      if (pos[0] - 1 >= 0 and pos[1] - 1 >= 0) and self.grid[pos[0] - 1][pos[1] - 1] != Cell.BLOCKED:
        locations.append((pos[0] - 1, pos[1] - 1))
      if (pos[0] + 1 < self._rows and pos[1] - 1 >= 0) and self.grid[pos[0] + 1][pos[1] - 1] != Cell.BLOCKED:
        locations.append((pos[0] + 1, pos[1] - 1))
      if (pos[0] - 1 >= 0 and pos[1] + 1 < self._cols) and self.grid[pos[0] - 1][pos[1] + 1] != Cell.BLOCKED:
        locations.append((pos[0] - 1, pos[1] + 1))
      if (pos[0] + 1 < self._rows and pos[1] + 1 < self._cols) and self.grid[pos[0] + 1][pos[1] + 1] != Cell.BLOCKED:
        locations.append((pos[0] + 1, pos[1] + 1))

    if self.random:
      rd.shuffle(locations)

    return locations

  def goal_test(self, pos):
    for goal in self.goals:
      if goal[0] == pos[0] and goal[1] == pos[1]:
        self.goals.remove(goal)
        self.start = goal
        return True
    return False

  @property  
  def clear_maze(self):
    self.grid = [[Cell.EMPTY for _ in range(self._cols)] for _ in range(self._rows)]
    self.start = None
    self.goals = []
    self.visited = []

  def _reset_goals(self, pos):
    id_g = self.visited.index(pos)

    for i in range(id_g + 1, len(self.goals)):
      x, y = self.visited[i]
      self.grid[x][y] = Cell.GOAL + str(i)


# ------------------------------------- Draw ---------------------------------------
class Draw:
  GOAL_IMG  = pygame.image.load(os.path.join('img', 'location.png'))
  START_IMG = pygame.image.load(os.path.join('img', 'origin.png'))
  EMPT_CLR = (235, 235, 235)
  BLCK_CLR = (  0,   0,   0)
  PATH_CLR = (115,   0, 230)
  SRC_CLRS = [(255, 77, 77), (51, 153, 255), (26, 255, 26), (172, 115, 57)]
  
  def __init__(self, surface, rows, cols):
    self.surface = surface
    self.rows = rows
    self.cols = cols

    self.delay = 0.05

    self.width = surface.get_width()
    self.height = surface.get_height()
    self.width_dist  = self.width  // cols
    self.height_dist = self.height // rows

  def draw_grid(self):
    self.surface.fill(self.EMPT_CLR)

    x, y = 0, 0
    for _ in range(self.rows):
      x += self.height_dist
      y += self.width_dist

      pygame.draw.line(self.surface, (0, 0, 0), (x, 0), (x, self.width))
      pygame.draw.line(self.surface, (0, 0, 0), (0, y), (self.height, y))

  def draw_maze(self, maze):
    grid = maze.grid

    for i, row in enumerate(grid):
      for j, v in enumerate(row):

        if v == Cell.BLOCKED:
          pygame.draw.rect(self.surface, self.BLCK_CLR, 
            (i * self.height_dist + 1, j * self.width_dist + 1, self.height_dist - 1, self.width_dist - 1))
        
        elif v.startswith(Cell.GOAL):
          pygame.draw.rect(self.surface, self.SRC_CLRS[int(v[1])],
            (i * self.height_dist + 1, j * self.width_dist + 1, self.height_dist - 1, self.width_dist - 1))
          self.surface.blit(self.GOAL_IMG, (i * self.height_dist + 3, j * self.width_dist + 3))
        
        elif v == Cell.EMPTY:
          pygame.draw.rect(self.surface, self.EMPT_CLR,
            (i * self.height_dist + 1, j * self.width_dist + 1, self.height_dist - 1, self.width_dist - 1))
        
        elif v == Cell.START:
          pygame.draw.rect(self.surface, self.SRC_CLRS[0],
            (i * self.height_dist + 1, j * self.width_dist + 1, self.height_dist - 1, self.width_dist - 1))
          self.surface.blit(self.START_IMG, (i * self.height_dist + 3, j * self.width_dist + 3))

  def draw_result(self, result, visited):
    total_dist = 0 - len(visited[2:])
    total_size = 0 - len(visited[2:])
    for dist, size, path in result:
      self._draw_path(path)
      total_dist += dist
      total_size += size

    for i, vis in enumerate(visited):
      self.surface.blit(self.GOAL_IMG if i != 0 else self.START_IMG, 
                        (vis[0] * self.height_dist + 3, vis[1] * self.width_dist + 3))

    window['-LBL_DIST-'].update(value=str(total_dist))
    window['-LBL_EXPL-'].update(value=str(total_size))

  def _draw_path(self, path):
    for p in path:  
      pygame.draw.rect(self.surface, (204, 51, 255),
        (p[0] * self.height_dist + 1, p[1] * self.width_dist + 1, self.height_dist - 1, self.width_dist - 1))

  def draw_search(self, pos, visited, start):
    pygame.draw.rect(self.surface, self.SRC_CLRS[visited.index(start)],
      (pos[0] * self.height_dist + 1, pos[1] * self.width_dist + 1, self.height_dist - 1, self.width_dist - 1))

    for vis in visited:
      self.surface.blit(self.GOAL_IMG if vis != start else self.START_IMG, 
                  (vis[0] * self.height_dist + 3, vis[1] * self.width_dist + 3))

    pygame.display.update()
    time.sleep(self.delay)


# ------------------------------------- Functions -------------------------------------
def change_cell(position, maze, cell_sign):
  width_dist  = SCR_WIDTH  // SCR_COLS
  height_dist = SCR_HEIGHT // SCR_ROWS
  i, j = position[0] // height_dist, position[1] // width_dist

  if cell_sign == Cell.GOAL:
    maze.add_goal(i, j)
  elif cell_sign == Cell.START:
    maze.add_start(i, j)
  elif cell_sign == Cell.BLOCKED:
    maze.add_blocked(i, j)
  elif cell_sign == Cell.EMPTY:
    maze.clear_cell(i, j)


# ------------------------------------- PySimpleGUI window layout and creation -------------------------------------
layout = [[sg.T(' ' * 50), sg.Text('Cells Explored:'), sg.Text('-', size=(3, 1), key='-LBL_EXPL-'), 
           sg.T('Distance:'), sg.T('-', size=(3, 1), key='-LBL_DIST-')],   
          [
           sg.Col([[sg.Graph((600, 600), (0, 0), (600, 600), background_color='lightblue', key='-GRAPH-')]]),
           sg.Col([#[sg.T(' ' * 4), sg.Button('Find Path',  key='-START-', size = (15, 1), disabled=True, **btn_font)],

                   [sg.Frame(title='Animation', relief=sg.RELIEF_SOLID, font=('italic'), title_location='n',
                             layout=[[sg.T(' ' * 3), sg.T('Delay:'), sg.T('0.05', key='-LBL_DEY-'), sg.T('msc')],
                                     [sg.Slider((.0, .1), size=(15, 14), default_value=0.05, pad=(8, 5), disable_number_display=True,
                                                 resolution=.01, orientation='h',  font=('Lato', 10), enable_events=True, key='-SLD_DEY-')],
                                     [sg.T(' '), sg.Button('Find Path',  key='-START-', size = (15, 1), disabled=True, **btn_font)]]
                              )],
                   [sg.Button('Start Point', key='-STRT_PNT-',  size = (10, 1), **btn_font),
                    sg.Button('Goal Point',  key='-GOAL_PNT-',  size = (10, 1), **btn_font)],
                   [sg.Button('Block Cell',  key='-BLCK_CELL-', size = (10, 1), **btn_font),
                    sg.Button('Clear Cell',  key='-CLR_CELL-',  size = (10, 1), **btn_font)],
                   [sg.T(' ' * 4), sg.Button('Clear Maze', key='-CLEAR-', size = (15, 1), **btn_font)],
                   [sg.Frame(title='Maze', relief=sg.RELIEF_SOLID, font=('italic'), title_location='n',
                            layout=[[sg.Slider((.0, .5), size=(15, 14), default_value=0.2, pad=(8, 5),
                                                resolution=.01, orientation='h',  font=('Lato', 10), key='-SLD_SPR-')],
                                    [sg.T(' '), sg.Button('Random Maze', key='-RND_MAZE-',  size=(15, 1), **btn_font)]]
                            )],
                   [sg.Frame(title='Algorithms', relief=sg.RELIEF_SOLID, font=('italic'), title_location='n',
                            layout=[[sg.Combo(['BFS', 'DFS', 'Greedy', 'Dijkstra', 'A*'], default_value='BFS', size=(10, 13), 
                                               readonly=True, pad=(47, 10), text_color=COMBO_TEXT, background_color=BACKGROUND,
                                               enable_events=True, key='-ALG-')],
                                    [sg.Radio("Closest",  pad=(9, 5), group_id='s', default=True, key='-S_CLO-'),
                                     sg.Radio("Ordered", pad=(9, 5), group_id='s', key='-S_ORD-')]]
                            )],
                   [sg.Frame(title='Direction', relief=sg.RELIEF_SOLID, font=('italic'), title_location='n',
                            layout=[[sg.Checkbox("Enable Diagonal", pad=(31, 5), key='-DIAG_SRC-', )],
                                    [sg.Checkbox("Enable Random",   pad=(31, 5), key='-RND_SRC-')]]
                            )],

                   [sg.Frame(title='Heuristic', relief=sg.RELIEF_SOLID, font=('italic'), title_location='n', visible=False, key='-HEU-',
                            layout=[[sg.Radio("Manhattan Distance", pad=(20, 5), group_id='h', key='-MHT-')],
                                    [sg.Radio("Euclidean Disance",  pad=(20, 5), group_id='h', default=True, key='-EUC-')]]
                            )]
                   ])
          ]]

window = sg.Window('Path Finding', layout, finalize=True)
graph = window['-GRAPH-']

# ------------------------------------- Magic code to integrate PyGame with tkinter -------------------------------------
embed = graph.TKCanvas
os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
if platform == 'Windows':
  os.environ['SDL_VIDEODRIVER'] = 'windib'
elif platform == 'Linux':
  os.environ['SDL_VIDEODRIVER'] = 'x11'

# ------------------------------------- PyGame Loop -------------------------------------
screen = pygame.display.set_mode((600, 600))
screen.fill(pygame.Color(235, 235, 235))
pygame.display.init()

maze = Maze(SCR_ROWS, SCR_COLS)
draw = Draw(screen, SCR_ROWS, SCR_COLS)
goal = 0
cell_sign = None

draw.draw_grid()

while True:

  # PySimpleGUI events
  event, values = window.read(timeout=10)
  if event == None:
    break

  if event == '-START-':
    maze.diagonal = values['-DIAG_SRC-']
    maze.random = values['-RND_SRC-']
    maze.ordered_search = values['-S_ORD-']

    draw.draw_maze(maze)
    window.disable()
    cell_sign = None

    if values['-MHT-']:
      heuristic = 'manhattan'
    else:
      heuristic = 'euclidean'

    result = init_algorithm(values['-ALG-'], heuristic, maze, draw.draw_search)
    
    if result:
      draw.draw_result(result, maze.visited)
#      draw.draw_path(path, maze.visited)
    window.enable()

  if event == '-SLD_DEY-':
    draw.delay = values['-SLD_DEY-']
    window['-LBL_DEY-'].update(value=str(values['-SLD_DEY-']))


  if event == '-RND_MAZE-':
    draw.draw_grid()
    maze.generate_maze(values['-SLD_SPR-'])
    draw.draw_maze(maze)

  if event == '-STRT_PNT-':
    cell_sign = Cell.START

  if event == '-BLCK_CELL-':
    cell_sign = Cell.BLOCKED

  if event == '-GOAL_PNT-':
    cell_sign = Cell.GOAL

  if event == '-CLR_CELL-':
    cell_sign = Cell.EMPTY

  if event == '-CLEAR-':
    maze.clear_maze
    window['-STRT_PNT-'].update(disabled=False)
    window['-GOAL_PNT-'].update(disabled=False)  
    draw.draw_maze(maze)
    cell_sign = None

  if event == '-ALG-':
    if values['-ALG-'] in ['A*', 'Greedy']:
      window['-HEU-'].update(visible=True)
      window['-DIAG_SRC-'].update(value=True)
    else:
      window['-HEU-'].update(visible=False)
      window['-DIAG_SRC-'].update(value=False)

  # Pygame events
  for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONUP and cell_sign:
      change_cell(pygame.mouse.get_pos(), maze, cell_sign)
      draw.draw_maze(maze)

      if maze.start:
        window['-STRT_PNT-'].update(disabled=True)
        if cell_sign == Cell.START: cell_sign = None
      else:
        window['-STRT_PNT-'].update(disabled=False)

      if len(maze.goals) == 3:
        window['-GOAL_PNT-'].update(disabled=True)
        if cell_sign == Cell.GOAL: cell_sign = None
      else:
        window['-GOAL_PNT-'].update(disabled=False)

      if maze.start and maze.goals:
        window['-START-'].update(disabled=False)      
      else:
        window['-START-'].update(disabled=True)

  pygame.display.update()

# SG
window.close()
