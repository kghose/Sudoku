"""
To create animation with good definition:

ffmpeg  -r 4 -qscale 2 -i frame%06d.png sudoku_simple.mp4
"""

import matplotlib
matplotlib.use("Agg")

import pylab, argparse, time

def algorithmx(M,R,C):
  """
  Recursive implementation of AlgroithmX
  M - constraint matrix - rows are possibilities, columns are cell/row/col/box constraints
  R - The identities of the rows left
  C - The identities of the columns left

  Returns
  sol - the solution rows
  Su - the backtracking tree
  """
  sol = None #Collection of solution rows
  Su = [] #Leaf
  if M.size:
    c = pylab.sum(M,axis=0).argmin()
    if pylab.sum(M[:,c]):
      for r in xrange(M.shape[0]):
        if M[r,c]:
          newM, newR, newC = algox_branch(M,R,C,r)
          sol, S = algorithmx(newM, newR, newC)
          Su.append([R[r], S]) #Visited children of this node
          if sol is not None:
            sol.append(R[r])
            break
  else:
    sol = [] #Leaf

  return sol,Su

def algox_branch(M,R,C,r):

  keep_c = []
  drop_c = []
  for col in xrange(M.shape[1]):
    if not M[r,col]:
      keep_c.append(col)
    else:
      drop_c.append(col)

  keep_r = []
  for row in xrange(M.shape[0]):
    keep = True
    for col in drop_c:
      if M[row,col]:
        keep = False
        break
    if keep:
      keep_r.append(row)

  newM = pylab.zeros((len(keep_r),len(keep_c)))
  for i,ro in enumerate(keep_r):
    for j,co in enumerate(keep_c):
      newM[i,j] = M[ro,co]

  if len(keep_r) and len(keep_c):
    newR = R[pylab.array(keep_r)]
    newC = C[pylab.array(keep_c)]
  else:
    newR = pylab.array([])
    newC = pylab.array([])
  return newM, newR, newC

def full_sudoku_constraint_matrix():
  C = pylab.arange(81*4)
  R = pylab.arange(9*9*9)
  M = pylab.zeros((9*9*9,9*9*4))
  for r in xrange(9):
    for c in xrange(9):
      for n in xrange(9):
        Mr = 81*r + 9*c + n
        M[Mr, 9*r + c] = 1 #Cell constraint
        M[Mr, 81 + 9*r + n] = 1 #Row constraint
        M[Mr, 2*81 + 9*c + n] = 1 #Col constraint
        b = (r // 3) * 3 + (c // 3) #Box no
        M[Mr, 3*81 + 9*b + n] = 1
  return M, R, C

def grid_from_constraint_matrix(R):
  """Numbering of R starts from 0."""
  grid = pylab.zeros((9,9),dtype=int)
  for ro in R:
    #81*r + 9*c + n = ro
    r = ro // 81
    c = (ro - 81 * r) // 9
    n = ro - 81*r - 9*c
    grid[r,c] = n + 1
  return grid

def constraint_matrix_from_grid(grid):
  """Empty cell = 0."""
  M, R, C = full_sudoku_constraint_matrix()
  for r in xrange(9):
    for c in xrange(9):
      if grid[r,c]:
        n = grid[r,c] - 1
        ro = 81*r + 9*c + n
        ro_n = pylab.find(R == ro)
        if ro_n.size:
          M, R, C = algox_branch(M,R,C,ro_n)

  return M, R, C

def load_grid(fname='ex1.txt'):
  grid = pylab.zeros((9,9),dtype=int)
  with open(fname,'r') as f:
    str = f.read().replace('\n', '').replace('-','').replace('|','').replace('+','').replace(' ','')
    for row in xrange(9):
      for col in xrange(9):
        n = row*9+col
        if '1' <= str[n] <= '9':
          grid[row, col] = int(str[n])

  return grid


def track_algorithm(Su, current_sol=[], Op=(0,0), Np=(0,0), plot_state=None):
  """Given a backtracking tree Su, containing constraint matrix row numbers
  and children visited during subtracking, reconstruct the search tree.
  Su - subtree of search
  current_sol - current solution vector of constraint matrix rows
  Op - coordinate of parent node of tree
  Np - coordinate of current node of tree.
  """
  #Handles
  HH = plot_state['handles']
  ax1 = HH['grid']
  ax2 = HH['tree']
  H_cp = HH.get('current position')
  x_lim = HH.get('xlim',10)
  H_er_no = HH.get('erasable numbers')

  pylab.axes(ax2)
  new_sol = list(current_sol)
  new_sol.append(Su[0])
  pylab.plot([Op[0], Np[0]],[Op[1], Np[1]],'o-',ms=2,color='gray',mfc='gray',mec='gray')

  if H_cp is not None:
    H_cp[0].remove()
  HH['current position'] = pylab.plot(Np[0],Np[1],'ko',label='current position')

  if Np[0]+10 > x_lim:
    x_lim = HH['xlim'] = Np[0]+10
  ax2.set_xlim([-10, x_lim])
  ax2.set_ylim([-10, Np[1]+10])

  grid = grid_from_constraint_matrix(new_sol)
  HH['erasable numbers'] = show_grid(ax1, grid, col = 'b', txt=H_er_no)

  pylab.draw()
  time.sleep(.01)

  nx = Np[0] + 5
  ny = Np[1]
  for n,ch in enumerate(Su[1]):
    Cp = (nx,ny + 10*n)
    ny = track_algorithm(ch, current_sol=new_sol, Op=Np, Np=Cp, plot_state=plot_state)

  return ny

# Display ----------------------------------------------------------------------
def setup_figure():
  w = 8.
  h = 4.
  fig = pylab.figure(figsize=(w,h))
  fig.subplots_adjust(left=0.0,bottom=0.0,right=1.0,top=1.0,wspace=0.0,hspace=0.0)

  ax1 = fig.add_axes([0,0,.5,1],label='grid')
  plot_grid_background(ax1)

  ax2 = fig.add_axes([.5,0,.5,1],label='tree')
  ax2.set_xticks([])
  ax2.set_yticks([])

  handles = {
    'fig': fig,
    'grid': ax1,
    'tree': ax2
  }
  return handles

def plot_grid_background(ax):
  pylab.axes(ax)
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

def show_grid(ax, grid, col = 'k', txt=None):
  """ax is obtained from plot_grid_background."""
  def show_cell(grid, r, c):
    txt = []
    cell = grid[r,c]
    y = (8-r)
    x = c
    if cell:
      txt += [pylab.text(x,y, cell, fontsize=24, color=col, horizontalalignment='center', verticalalignment='center')]
    return txt

  pylab.axes(ax)
  if txt is not None:
    for t in txt:
      t.remove()
  txt = []
  for r in xrange(9):
    for c in xrange(9):
      txt += show_cell(grid, r, c)
  return txt

def save_frame(base_name, frame_no):
  fname = "{bn}{fn:06d}.png".format(bn=base_name, fn=frame_no)
  pylab.savefig(fname)

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Graphical demonstration of AlgorithmX for Sudoku.')
  parser.add_argument('filename')
  args = parser.parse_args()

  fname = args.filename + '.txt'
  frame_path = '/tmp/sudoku/' + args.filename + '/'

  grid = load_grid(fname=fname)

  import os
  if not os.path.exists(frame_path):
    os.makedirs(frame_path)
  base_name = frame_path + 'frame'

  M, R, C = constraint_matrix_from_grid(grid)
  sol, Su = algorithmx(M,R,C)
  gridS = grid_from_constraint_matrix(sol)
  print grid + gridS

  handles = setup_figure()
  show_grid(handles['grid'], grid, col = 'k')
  frame_no = 0
  save_frame(base_name, frame_no)
  plot_state = {
    'handles': handles,
    'current position': None,
    'frame no': frame_no}
  track_algorithm(Su[0], plot_state=plot_state)