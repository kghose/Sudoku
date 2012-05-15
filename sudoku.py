"""
Data structures:

grid - sudoku grid is a 9x9 list of lists of lists. The innermost list is the
candidate solutions to a cell. If there is only one entry then it is a filled
cell, if there is more then it is an empty cell and those are the possibilities.

node = {
  'grid': this_child_grid,
  'parent': current_node,
  'row': b_row,
  'col': b_col,
  'n': n,
  'children': list of nodes
}
This is a node that makes up the tree of hypotheseses that we test

The search path is made up of list of these
search_path = {
  'row': ...,
  'col': ...,
  'value':
}

history - every change to the grid is put in the history. When we reach an
invalid solution and pick the next branch we actually insert a backtrack into
the history because this looks nice visually.

To create animation with good definition:

ffmpeg  -i test%06d.png -vcodec libx264 -x264opts keyint=123:min-keyint=20 -an sudoku.mkv


"""
#import matplotlib
#matplotlib.use("Agg")
import copy, pylab, time

# Initialization ---------------------------------------------------------------
def example_grid():
  grid = [
    [[5], [3], range(1,10), range(1,10), [7], range(1,10), range(1,10), range(1,10), range(1,10)],
    [[6], range(1,10), range(1,10), [1], [9], [5], range(1,10), range(1,10), range(1,10)],
    [range(1,10), [9], [8], range(1,10), range(1,10), range(1,10), range(1,10), [6], range(1,10)],
    [[8], range(1,10), range(1,10), range(1,10), [6], range(1,10), range(1,10), range(1,10), [3]],
    [[4], range(1,10), range(1,10), [8], range(1,10), [3], range(1,10), range(1,10), [1]],
    [[7], range(1,10), range(1,10), range(1,10), [2], range(1,10), range(1,10), range(1,10), [6]],
    [range(1,10), [6], range(1,10), range(1,10), range(1,10), range(1,10), [2], [8], range(1,10)],
    [range(1,10), range(1,10), range(1,10), [4], [1], [9], range(1,10), range(1,10), [5]],
    [range(1,10), range(1,10), range(1,10), range(1,10), [8], range(1,10), range(1,10), [7], [9]]
  ]
  return grid

def empty_grid():
  grid = [[range(1,10) for n in xrange(9)] for m in xrange(9)]
  return grid

def load_grid(fname='ex1.txt'):
  grid = empty_grid()
  with open(fname,'r') as f:
    str = f.read().replace('\n', '')
    for row in xrange(9):
      for col in xrange(9):
        n = row*9+col
        if '1' <= str[n] <= '9':
          grid[row][col] = [int(str[n])]
  return grid

# Manipulation -----------------------------------------------------------------
def branch(cg, current_node):
  """Simple minded to start with."""
  min_len = 10
  b_row = 0
  b_col = 0
  for row in xrange(9):
    for col in xrange(9):
      if 1 < len(cg[row][col]) < min_len:
        min_len = len(cg[row][col])
        b_row = row
        b_col = col
        #We will never call branch with a grid that is solved.

  n_branches = len(cg[b_row][b_col])
  child_nodes = []
  for n in xrange(n_branches):
    this_child_grid = copy.deepcopy(cg)
    this_child_grid[b_row][b_col] = [this_child_grid[b_row][b_col][n]]
    node = {
      'grid': this_child_grid,
      'parent': current_node,
      'row': b_row,
      'col': b_col,
      'n': n
    }
    child_nodes.append(node)

  for n in xrange(n_branches-1):
    child_nodes[n]['next'] = child_nodes[n+1]
  child_nodes[n_branches-1]['next'] = None

  current_node['children'] = child_nodes
  print 'Children', len(child_nodes)


  return current_node

def next_branch(current_node):
  """none means we are OUT"""
  node = current_node['next']
  parent = current_node['parent']
  while node is None and parent is not None:
    node = parent['next']
    parent = parent['parent']
  return node

def eliminate_this(grid, row, col, value):
  """Remove the given value from the cell if possible. If the cell is solved
  say so."""
  changed = False
  invalid = False
  solved = False
  #grid = copy.deepcopy(o_grid)
  ol = len(grid[row][col])
  if value in grid[row][col]:
    grid[row][col].remove(value)
  nl = len(grid[row][col])
  if nl == 0: invalid = True
  if nl == 1:
    solved = True
    if ol > 1: changed = True #We just solved it

  return grid, changed, invalid, solved


def flood_fill(row, col, value, search_path=None):
  """If a cell has been filled in at row,col use this to add the cells to be
  checked."""

  new_rows = []
  new_cols = []

  #Knockout the 3x3 subgrid (minus rows and cols which we do below)
  r_start = (row/3)*3
  c_start = (col/3)*3
  rows = xrange(r_start, r_start+3)
  cols = xrange(c_start, c_start+3)
  for r in rows:
    for c in cols:
      if r != row and c != col:
        new_rows.append(r)
        new_cols.append(c)

  #Traverse the row
  for c in xrange(9):
    if c == col:
      continue
    new_rows.append(row)
    new_cols.append(c)

  #Traverse the column
  for r in xrange(9):
    if r == row:
      continue
    new_rows.append(r)
    new_cols.append(col)

  if search_path is None:
    search_path =  {'rows': [],
                    'cols': [],
                    'values': []}

  search_path['rows'] += new_rows
  search_path['cols'] += new_cols
  search_path['values'] += [value]*len(new_cols)

  return search_path

def solve_step(grid, path_step=0, search_path=None):

  row = search_path['rows'][path_step]
  col = search_path['cols'][path_step]
  value = search_path['values'][path_step]

  grid, changed, invalid, solved = eliminate_this(grid, row, col, value)
  if changed:#We gotta add to the path (domino effect)
    search_path = flood_fill(row, col, grid[row][col][0], search_path)
    print 'Solved', row, col, '(', grid[row][col][0], ')'

  path_step += 1
  if path_step == len(search_path['rows']):
    sweep = True
    path_step = 0
  else:
    sweep = False

  return grid, path_step, search_path, changed, invalid, solved, sweep

# Display ----------------------------------------------------------------------
def plot_grid_background():
  fig = pylab.figure(figsize=(4,4))
  fig.subplots_adjust(left=0.0,bottom=0.0,right=1.0,top=1.0,wspace=0.0,hspace=0.0)
  ax = fig.add_subplot(111)
  ax.set_xlim([-.55,8.55])
  ax.set_ylim([-.55,8.55])
  ax.set_xticks([])
  ax.set_yticks([])
  for x in xrange(9):
    pylab.plot([x+.5,x+.5], [-.5,8.5],'k')
  for y in xrange(9):
    pylab.plot([-.5,8.5], [y+.5,y+.5],'k')
  for x in [-.5,2.5,5.5,8.5]:
    pylab.plot([x,x], [-.5,8.5],'k',lw=4)
  for y in [-.5,2.5,5.5,8.5]:
    pylab.plot([-.5,8.5], [y,y],'k',lw=4)
  return fig

def show_grid(grid, txt=None):
  """ax is obtained from plot_grid_background."""
  def show_cell(grid, r, c):
    txt = []
    cell = grid[r][c]
    y = (8-r)
    x = c
    if len(cell) == 0:
      txt += [pylab.text(x,y, 'X', fontsize=36, horizontalalignment='center', verticalalignment='center')]
    elif len(cell) == 1:
      txt += [pylab.text(x,y, cell[0], fontsize=24, horizontalalignment='center', verticalalignment='center')]
    else:
      for n in cell:
        no = int(n)
        dx = ((no-1) % 3)/3.0 -.33
        dy = .33 - ((no-1) / 3)/3.0
        txt += [pylab.text(x+dx,y+dy, no, fontsize=8, horizontalalignment='center', verticalalignment='center',color='b')]

    return txt

  if txt is not None:
    for t in txt:
      t.remove()
  txt = []
  for r in xrange(9):
    for c in xrange(9):
      txt += show_cell(grid, r, c)
  return txt

def highlight_cell(row=-1,col=-1,H=None,c='y'):
  if H is not None:
    for h in H:
      h.remove()
  x1 = col - .45
  x2 = col + .45
  y1 = 8 - row -.45
  y2 = 8 - row + .45
  return pylab.plot([x1,x2,x2,x1,x1], [y1,y1,y2,y2,y1],c,lw=2)

def mark_hypothesis_cells(current_node, H):
  if H is not None:
    for h in H:
      h.remove()

  rows = []
  cols = []
  node = current_node
  while node['parent'] is not None:
    rows.append(node['row'])
    cols.append(node['col'])
    node = node['parent']

  x = pylab.array(cols)
  y = 8 - pylab.array(rows)
  return pylab.plot(x,y,'yo-',ms=24,mfc=None)

def update_grid_plot(grid, row=-1,col=-1,txt=None,
                           c='y', H=None,
                           current_node=None, Hh=None,
                     base_name = 'test', frame_no = 0):
  txt = show_grid(grid,txt)
  H = highlight_cell(row,col,H,c)
  Hh = mark_hypothesis_cells(current_node, Hh)
  pylab.draw()
  pylab.show()
  fname = "{bn}{fn:06d}.png".format(bn=base_name, fn=frame_no)
  #pylab.savefig(fname)
  return txt, H, Hh

# Utility functions
def initial_flood_fill(grid):
  """Start us off by looking at the solved cells and then floodfilling from them."""
  search_path = None
  for r in xrange(9):
    for c in xrange(9):
      if len(grid[r][c]) == 1:
        search_path = flood_fill(r, c, grid[r][c][0], search_path)

  return search_path


def hypothesis(current_node):
  grid = current_node['grid']
  row = 0
  col = 0
  return grid, row, col


if __name__ == "__main__":

  #grid = empty_grid()
  grid = example_grid()
  #grid = load_grid(fname='ex2.txt')

  parent_node = {
    'grid': grid,
    'parent': None,
    'next': None
  }

  current_node = parent_node

  fig = plot_grid_background()
  pylab.ion()
  txt = show_grid(grid)
  H = None
  Hh = None

  """The reason for structuring the code as a single loop of single steps
  instead having a loop to do repeated sweeps and then another outer loop to do
  branching when needed is simply for display: we want to be able to see the
  result of each iteration.

  Therefore, hidden in this while loop are actually two logical loops. The inner
  loop terminates when all the cells have been swept once, and that is indicated
  by the 'sweep' flag being set. The outer loop terminates when we complete a
  sweep and the 'solved' flag is still set, indicating that all cells have been
  solved.
  """
  frame_no = 0
  search_path = initial_flood_fill(grid)
  path_step = 0
  grid_solved = True #We flip this if any one cell is not solved and check it at the end of each sweep
  sweep = False
  grid_changed = False
  cell_invalid = False
  while not (sweep and grid_solved):
    c = 'y'
    if grid_changed: c = 'b'
    if cell_invalid: c = 'r'
    row = search_path['rows'][path_step]
    col = search_path['cols'][path_step]
    txt, H, Hh = update_grid_plot(grid=grid,
                              row=row,col=col,txt=txt,c=c,H=H,
                              current_node=current_node,Hh=Hh,
                              frame_no = frame_no) #Show our handiwork
    frame_no += 1

    if cell_invalid:
      current_node = next_branch(current_node)
      if current_node is None: #No solution to this grid
        break
      grid, row, col = hypothesis(current_node)
      search_path = flood_fill(row, col, grid[row][col][0])
      path_step = 0
      grid_solved = True

    if sweep: #At the end of what we can do without branching
      sweep = False
      current_node = branch(grid, current_node)
      current_node = current_node['children'][0]
      grid, row, col = hypothesis(current_node)
      search_path = flood_fill(row, col, grid[row][col][0])
      path_step = 0
      grid_solved = True #In preparation for another run

    grid, path_step, search_path, cell_changed, cell_invalid, cell_solved, sweep =\
      solve_step(grid, path_step, search_path)

    #if cell_changed: grid_changed = True
    if not cell_solved: grid_solved = False

    time.sleep(.1)
