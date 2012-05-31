"""
To create animation with good definition:

ffmpeg  -r 4 -qscale 2 -i frame%06d.png sudoku_simple.mp4
"""

import matplotlib
matplotlib.use("Agg")

import pylab, argparse

def prt(R,C,r,op):
  """A simple plotting function we can use for debugging."""
  print R.size,C.size

def algorithmx(M,R,C, plotfun = prt):
  """plotfunc is the function we use for plotting the progress of the algorithm."""
  sol = None
  if M.size:
    c = pylab.sum(M,axis=0).argmin()
    if pylab.sum(M[:,c]):
      for r in xrange(M.shape[0]):
        if M[r,c]:
          newM, newR, newC = algox_branch(M,R,C,r)
          if plotfun:
            plotfun(R,C,r,'push')
          sol = algorithmx(newM, newR, newC, plotfun)
          if sol is not None:
            sol.append(R[r])
            break
          elif plotfun:
            plotfun(R,C,r,'pop')
  else:
    sol = [] #Leaf

  return sol

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

# Display ----------------------------------------------------------------------
def setup_figure():
  w = 5.
  h = 6.
  h1 = .25*w #81/324 - # max no of final constraint rows
  h0 = h - h1
  fig = pylab.figure(figsize=(w,h))
  fig.subplots_adjust(left=0.0,bottom=0.0,right=1.0,top=1.0,wspace=0.0,hspace=0.0)

  ax = fig.add_axes([0,0,1.,h0/h],label='grid')
  plot_grid_background(ax)
  ax_con = fig.add_axes([0,h0/h,1.,h1/h],label='constraint matrix')
  ax_con.set_xlim([0, 324])
  ax_con.set_ylim([0, 81])
  ax_con.set_xticks([])
  ax_con.set_yticks([])

  figure = {
    'fig': fig,
    'grid': ax,
    'constraint matrix': ax_con
  }
  return figure

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

def show_matrix(ax, R):
  P = pylab.zeros((2,R.size*4),dtype=int)
  for ron,ro in enumerate(R):
    #81*r + 9*c + n = ro
    r = ro // 81
    c = (ro - 81 * r) // 9
    n = ro - 81*r - 9*c
    y = ron
    P[:,4*ron] = [9*r + c, y] #Cell constraint
    P[:,4*ron+1] = [81 + 9*r + n, y] #Row constraint
    P[:,4*ron+2] = [2*81 + 9*c + n, y] #Col constraint
    b = (r // 3) * 3 + (c // 3) #Box no
    P[:,4*ron+3] = [3*81 + 9*b + n, y]

  pylab.axes(ax)
  lines = ax.get_lines()
  for line in lines:
    label = line.get_label()
    if label == 'current mat' or label == 'current row line':
      line.remove()

  pylab.plot(P[0,:], P[1,:], 's', ms=3, mfc='gray',mec='gray')
  pylab.plot(P[0,:], P[1,:], 'ks', ms=1, label='current mat')
  pylab.plot([0, 4*81], [len(R), len(R)], 'k:', label='current row line')

def show_algorithm_step(R,C,r,op='push'):
  """This is the plotting function we plug into the algorithm to visualize it."""

  global figure, erasable_numbers, chosenR, frame_no
  if op == 'push':
    chosenR.append(R[r])
  elif len(chosenR):
    chosenR.pop()

  frame_no += 1
  AchosenR = pylab.array(chosenR)

  grid = grid_from_constraint_matrix(AchosenR)
  erasable_numbers = show_grid(figure['grid'], grid, col = 'b', txt = erasable_numbers)

  show_matrix(figure['constraint matrix'], AchosenR)

  pylab.draw()
#  time.sleep(.01)
  save_frame()

def save_frame():
  global base_name, frame_no

  fname = "{bn}{fn:06d}.png".format(bn=base_name, fn=frame_no)
  pylab.savefig(fname)


if __name__ == "__main__":
  global figure, erasable_numbers, chosenR, frame_no, base_name
  erasable_numbers = None
  chosenR = []
  frame_no = 0

  parser = argparse.ArgumentParser(description='Graphical demonstration of AlgorithmX for Sudoku.')
  parser.add_argument('filename')
  args = parser.parse_args()

  fname = args.filename + '.txt'
  frame_path = '/tmp/sudoku/' + args.filename + '/'

  grid = load_grid(fname=fname)
  #frame_path = '/tmp/sudoku/ex2/'

  import os
  if not os.path.exists(frame_path):
    os.makedirs(frame_path)
  base_name = frame_path + 'frame'

  figure = setup_figure()
  show_grid(figure['grid'], grid, col = 'k')

  M, R, C = constraint_matrix_from_grid(grid)
  sol = algorithmx(M,R,C,plotfun=show_algorithm_step)
  #sol = algorithmx(M,R,C,plotfun=None)
  gridS = grid_from_constraint_matrix(sol)
  print grid + gridS
