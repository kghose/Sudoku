"""
Data structures:

grid - sudoku grid is a 9x9 list of lists of lists. The innermost list is the
candidate solutions to a cell. If there is only one entry then it is a filled
cell, if there is more then it is an empty cell and those are the possibilities.

branch_stack - a dictionary containing a list of the current branch path and
lists of the branch grids

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
def exact_cover(grid, row, col):
  to_discard = []
  #For a given cell go through the row and column looking for other cells that
  #have a single element. Eliminate that element
  for c in xrange(9):
    if c == col:
      continue
    if len(grid[row][c]) == 1:
      to_discard += grid[row][c]

  for r in xrange(9):
    if r == row:
      continue
    if len(grid[r][col]) == 1:
      to_discard += grid[r][col]

  #Look in the 3x3 subgrid this cell belongs to for similar eliminations
  r_start = (row/3)*3
  c_start = (col/3)*3
  rows = xrange(r_start, r_start+3)
  cols = xrange(c_start, c_start+3)
  for r in rows:
    for c in cols:
      if r != row or c != col:
        if len(grid[r][c]) == 1:
          to_discard += grid[r][c]

  for td in to_discard:
    if td in grid[row][col]:
      grid[row][col].remove(td)

  return grid

def reduce_cell(o_grid, row, col):
  """Given a cell try and reduce the choices using Sudoku rules."""
  changed = False
  invalid = False
  solved = False
  grid = copy.deepcopy(o_grid)
  ol = len(grid[row][col])
  if ol > 1:
    grid = exact_cover(grid, row, col)
  nl = len(grid[row][col])
  if nl == 0: invalid = True
  if nl == 1:
    solved = True
    if ol > 1: changed = True #We just solved it

  return grid, changed, invalid, solved


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

def flood_fill(row, col, path=[]):
  """If a cell has been filled in at row,col use this to add the cells to be
  checked nd then use a flood fill to add to the current path."""





def solve_step(grid, row=0, col=0):
  """
  Start the solver with row=col=0, changed=False, solved=True
  """
  grid, changed, invalid, solved = reduce_cell(grid, row, col)
  sweep = False
  col += 1
  if col > 8:
    col = 0
    row += 1
  if row > 8: #Finished a sweep
    row = 0
    sweep = True

  return grid, row, col, changed, solved, invalid, sweep

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



# Utility function for main loop
def hypothesis(current_node):
  grid = current_node['grid']
  row = 0
  col = 0
  return grid, row, col


if __name__ == "__main__":

  grid = empty_grid()
  #grid = example_grid()
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
  hyp = False #Just used to indicate if we are in a hypothesis branch for plotting
  h_rows = []
  h_cols = []
  grid_solved = True #We flip this if any one cell is not solved and check it at the end of each sweep
  grid_changed = False
  grid, row, col, cell_changed, cell_solved, cell_invalid, sweep = solve_step(grid)
  while not (sweep and grid_solved):
    c = 'y'
    if grid_changed: c = 'b'
    if cell_invalid: c = 'r'
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
      hyp = True

    if sweep:
      sweep = False
      grid_solved = True #In preparation for another run
      if not grid_changed: #At the end of what we can do without branching
        current_node = branch(grid, current_node)
        current_node = current_node['children'][0]
        grid, row, col = hypothesis(current_node)
        hyp = True
      else:
        grid_changed = False #Should go for another run

    grid, row, col, cell_changed, cell_solved, cell_invalid, sweep = \
      solve_step(grid, row, col)
    if cell_changed: grid_changed = True
    if not cell_solved: grid_solved = False

    time.sleep(.1)
