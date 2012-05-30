import pylab, time

def prt(R,C,r,op):
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

def show_grid(grid, col = 'k', txt=None):
  """ax is obtained from plot_grid_background."""
  def show_cell(grid, r, c):
    txt = []
    cell = grid[r,c]
    y = (8-r)
    x = c
    if cell:
      txt += [pylab.text(x,y, cell, fontsize=24, color=col, horizontalalignment='center', verticalalignment='center')]

    return txt

  if txt is not None:
    for t in txt:
      t.remove()
  txt = []
  for r in xrange(9):
    for c in xrange(9):
      txt += show_cell(grid, r, c)
  return txt

def update_grid(R,C,r,op='push'):
  global erasable_numbers, chosenR, compute_step

  if op == 'push':
    chosenR.append(R[r])
    compute_step += 1
  else:
    chosenR.pop()

  grid = grid_from_constraint_matrix(pylab.array(chosenR))
  erasable_numbers = show_grid(grid, col = 'b', txt = erasable_numbers)
  pylab.draw()
  time.sleep(.1)

if __name__ == "__main__":
#  C = pylab.array([1,2,3,4,5,6,7])
#  R = pylab.array([1,2,3,4,5,6])
#
#  M = pylab.array([
#    [1,0,0,1,0,0,1],
#    [1,0,0,1,0,0,0],
#    [0,0,0,1,1,0,1],
#    [0,0,1,0,1,1,0],
#    [0,1,1,0,0,1,1],
#    [0,1,0,0,0,0,1]
#  ])
#  sol = algorithmx(M,R,C)
#  print sol

  global erasable_numbers, chosenR, compute_step
  erasable_numbers = None
  chosenR = []
  compute_step = 0

  plot_grid_background()
  grid = load_grid(fname='ex2.txt')
  show_grid(grid, col = 'k')

  M, R, C = constraint_matrix_from_grid(grid)
  sol = algorithmx(M,R,C,plotfun=update_grid)
  gridS = grid_from_constraint_matrix(sol)
  print grid + gridS

#  sol = algorithmx(M,R,C)
#  gridS = grid_from_constraint_matrix(sol)
#  print grid

#  M, R, C = full_sudoku_constraint_matrix()
#  #sol = algorithmx(M,R,C)
#  sol = [0,10]
