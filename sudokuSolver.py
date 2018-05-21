import sys
import traceback


class AssignmentLimitReachedException(Exception):
	def __init__(self, msg):
		self.msg = msg

class Cell:
	def __init__(self, row, col, state, domain):
		self.row = row
		self.col = col
		self.state = state
		self.domain = domain


class SudokuPuzzle:
	def __init__(self, filename):
		self.grid = [[]] # stores the state of the puzzle
		self.totalAssignments = 0 # count of assignments made to solve the given instance
		try:
			# read in the grid layout from file and initialize grid
			gridInput = open(filename, "r")
			domain = '123456789'
			i = 0 # to track the row we are in
			for line in gridInput:
				tokens = line.split() # tokenize line
				if not tokens: # check if tokens is empty
					continue
				self.grid.append([])
				row = self.grid[i]
				if i <= 8: # we only expect to read in the initial state of the puzzle, ignore rest
					for j in range(9):
						state = tokens[j]
						copy = (domain + '.')[:-1] # create new copy of domain
						assert id(copy) != id(domain)
						if state != '0':
							copy = copy.replace(state, '') # remove state from domain
						cell = Cell(i, j, state, copy)
						row.append(cell)
					i += 1
				#print 'New iteration i value is ' + str(i)
		except:
			traceback.print_exc()

	# printGrid()
	# prints the state of sudoku grid
	def printGrid(self):
		try:
			grid = self.grid
			for i in range(9):
				for j in range(9):
					print grid[i][j].state,
				print '\n'
		except IndexError:
			traceback.print_exc()

	# solveVersionA
	# returns: false if sudoku cannot be solved and true when it is solved
	# This version uses ONLY search + backtracking to solve the problem
	def solveVersionA(self):
		try:
			nxtEmptyCell = self.findEmptyCell()
			if nxtEmptyCell == [-1,-1]:
				# all cell assignments complete
				return True # problem solved
			for assignment in range(1,10):
				value = str(assignment)
				if self.isValidAssignment(nxtEmptyCell, value):
					# This is a promising assignment so lets try to find
					# a solution for the entire grid from this cell value assignment
					# Also, simple backtracking search does not make use of domain
					# state at any time t so I am being lazy and not updating the domain
					# of the dependent cells (something which I should logically be doing)
					cell = self.grid[nxtEmptyCell[0]][nxtEmptyCell[1]]
					cell.state = value
					cell.domain = cell.domain.replace(value, '') # update domain
					self.totalAssignments += 1
					if self.totalAssignments >= 10000:
						errorMsg = '10000 assignments reached but no solution has been found'
						raise AssignmentLimitReachedException(errorMsg)
					if self.solveVersionA():
						return True
					else:
						cell.state = '0'
						cell.domain += value
						# explore next promising value assignment (backtracking)
			return False # could noy solve problem
		except AssignmentLimitReachedException as exp:
			raise
		except:
			traceback.print_exc()


	# solveVersionB
	# returns: True if problem instance is solved, false otherwise
	# This version uses search + backtracking + forward checking to solve the problem
	def solveVersionB(self):
		try:
			nxtEmptyCell = self.findEmptyCell()
			if nxtEmptyCell == [-1,-1]:
				return True # problem solved
			cell = self.grid[nxtEmptyCell[0]][nxtEmptyCell[1]]
			domain = cell.domain
			for assignment in range(1,10):
				value = str(assignment)
				if self.isValidAssignment(nxtEmptyCell, value):
					# this is a promising assignment so lets try to find
					# a solution from this value assignment
					cell = self.grid[nxtEmptyCell[0]][nxtEmptyCell[1]]
					cell.state = value
					#cell.domain = cell.domain.replace(cell.domain, '') # update domain
					ret = self.deleteFromDomainOfDependents(cell, value) # deleting this assignment
					                                                     # from dependents' domains
					rollback = ret[1]
					#if ret[0]:
						#print 'MISSED A POTENTIAL DEAD END'
					if self.isDeadEnd(cell, value):
						cell.state = '0'
						domain = domain.replace(value, '')
						cell.domain = domain
						self.revertDomainOfDependents(rollback, value)
						continue
					self.totalAssignments += 1
					if self.totalAssignments >= 10000:
						errorMsg = '10000 assignments reached but no solution has been found'
						raise AssignmentLimitReachedException(errorMsg)
					if self.solveVersionA():
						return True
					else:
						cell.state = '0'
						domain = domain.replace(value, '')
						cell.domain = domain
						self.revertDomainOfDependents(rollback, value)
						# explore next value assignment (backtracking)
			return False
		except AssignmentLimitReachedException as exp:
			raise
		except:
			traceback.print_exc()



	# solveVersionC
	# returns: True if problem instance is solved, false otherwise
	# This version uses search + backtracking + forward checking +
	# heuristics (most restricted variable, most constraining value (for tie breaking),
	# and least constrained value) to solve the problem
	def solveVersionC(self):
		try:
			nxtEmptyCell = self.heuristicallySelectNextCell()
			if nxtEmptyCell == []:
				nxtEmptyCell = self.findEmptyCell()
				if nxtEmptyCell == [-1,-1]:
					# all cell assignments complete
					return True

			cell = self.grid[nxtEmptyCell[0]][nxtEmptyCell[1]]
			domain = cell.domain
			for assignment in range(1,10):
				value = str(assignment)
				if self.isValidAssignment(nxtEmptyCell, value):
					# this is a promising assignment so lets try to find
					# a solution from this value assignment
					# Also, simple backtracking search does not make use of domain
					# state at any time t so I am being lazy and not updating the domain
					# of the dependent cells (something which I should logically be doing)
					cell = self.grid[nxtEmptyCell[0]][nxtEmptyCell[1]]
					cell.state = value
					cell.domain = cell.domain.replace(value, '') # update domain
					ret = self.deleteFromDomainOfDependents(cell, value)
					rollback = ret[1]
					if ret[0]:
						print 'MISSED A POTENTIAL DEAD END'
					if self.isDeadEnd(cell, value):
						print 'HIT DEAD END'
						cell.state = '0'
						domain = domain.replace(value, '')
						cell.domain = domain
						self.revertDomainOfDependents(rollback, value)
						continue
					self.totalAssignments += 1
					if self.totalAssignments >= 10000:
						errorMsg = '10000 assignments reached but no solution has been found'
						raise AssignmentLimitReachedException(errorMsg)
					if self.solveVersionA():
						return True
					else:
						cell.state = '0'
						domain = domain.replace(value, '')
						cell.domain = domain
						self.revertDomainOfDependents(rollback, value)
						# explore next promising value assignment (backtracking)
			return False
		except AssignmentLimitReachedException as exp:
			raise
		except:
			print 'Error in solveVersionB()'
			traceback.print_exc()


	# isDeadEnd
	# returns True if the assignment to visiting (cell) causes
	# the domain of any dependent cells to become empty thus,
	# signalling that this assignment does not result in a solution,
	# returns False otherwise
	def isDeadEnd(self, visiting, assignment):
		try:
			grid = self.grid
			for i in range(9):
				for j in range(9):
					if i == visiting.row and j == visiting.col:
						continue # ignore currently considered cell
					cell = grid[i][j]
					if cell.state == '0':
						domain = cell.domain
						domain = (domain + '.')[:-1]
						domain = domain.replace(assignment, '')
						if len(domain) == 0:
							return True
			return False
		except IndexError:
			print 'Invalid index access in isDeadEnd()'

	# deleteFromDomainOfDependents
	# deletes assignment from domain of cell's dependents
	# returns True if any one of the dependent is left with an empty domain
	# after deletion and False otherwise
	def deleteFromDomainOfDependents(self, cell, assignment):
		try:
			# check if domain of any of the cells in the row is exhausted
			changed = {}
			row = self.grid[cell.row]
			for i in range(9):
				if i != cell.col and row[i].state == '0':
					row[i].domain = row[i].domain.replace(assignment, '')
					changed[cell.row] = i
					if len(row[i].domain) == 0:
						return [True, changed]
			# check if domain of any of the cells in the col is exhausted
			grid = self.grid
			for i in range(9):
				if i != cell.row and grid[i][cell.col].state == '0':
					grid[i][cell.col].domain = grid[i][cell.col].domain.replace(assignment,'')
					changed[i] = cell.col
					if len(grid[i][cell.col].domain) == 0:
						return [True, changed]

			# check if domain of any of the cells in the sub-grid is exhausted
			rowBoundary = (cell.row / 3) * 3
			colBoundary = (cell.col / 3) * 3
			for i in range(3):
					for j in range(3):
						if i != cell.row and j != cell.col and grid[rowBoundary+i][colBoundary+j] == '0':
							grid[rowBoundary+i][colBoundary+j].domain = grid[rowBoundary+i][colBoundary+j].domain.replace(assignment, '')
							changed[rowBoundary+i] = [colBoundary+j]
							if len(grid[rowBoundary+i][colBoundary+j].domain) == 0:
								return [True, changed]
			return [False, {}]
		except IndexError:
			print 'Invalid index access in deleteFromDomainOfDependents()'
			traceback.print_exc()

	# revertDomainOfDependents
	def revertDomainOfDependents(self, revert, assignment):
		try:
			# check if domain of any of the cells in the row is exhausted
			for key in revert.keys():
				row = key
				col = revert[key]
				cell = self.grid[row][col]
				cell.domain += assignment
		except IndexError:
			print 'Invalid index access in deleteFromDomainOfDependents()'
			traceback.print_exc()

	# findEmptyCell
	# returns location of the first empty cell in format [row_pos,col_pos]
	# and [-1,-1] if no cell is empty
	def findEmptyCell(self):
		try:
			grid = self.grid
			for i in range(9):
				for j in range(9):
					if grid[i][j].state == '0':
						return [i,j]
			return [-1,-1]
		except IndexError:
			print 'Invalid index access in findEmptyCell()'
			traceback.print_exc()

	# finds the most restricted cell i.e. the cell which has the fewest options in
	# its domain of legal assignments
	def heuristicallySelectNextCell(self):
		try:
			grid = self.grid
			mrvSoFar = []
			mrvValue = 10 # this is fine since the domain of any X(ij) can be at most of length 9
			retVal = []
			for i in range(9):
				for j in range(9):
					cell = grid[i][j]
					length = len(cell.domain)
					if length < mrvValue:
						mrvValue = length
						mrvSoFar = [[cell.row, cell.col]]
					elif length == mrvValue:
						mrvSoFar.append([cell.row, cell.col])
			length = len(mrvSoFar)
			if length == 0:
				retVal = []
			elif length == 1:
				retVal = mrvSoFar[0]
			else:
				retVal = self.findMostConstrainingCell(mrvSoFar)
			return retVal
		except IndexError:
			traceback.print_exc()

	# findMostConstrainingCell
	def findMostConstrainingCell(self, mrvLocation):
		try:
			grid = self.grid
			first = mrvLocation[0]
			cell = grid[first[0]][first[1]]
			retVal = mrvLocation[0]
			constraintScore = self.computeConstraintScore(cell)
			for loc in mrvLocation:
				if loc == first:
					continue
				cell = grid[loc[0]][loc[1]]
				score = self.computeConstraintScore(cell) # initialization
				if score > constraintScore:
					constraintScore = score
					retVal = loc
			return retVal
		except IndexError:
			print 'Invalid index access in findEmptyCell()'
			traceback.print_exc()


	def computeConstraintScore(self, cell):
		try:
			rowScore = 0
			colScore = 0
			subGridScore = 0
			row = cell.row
			col = cell.col
			rowBoundary = (cell.row / 3) * 3
			colBoundary = (cell.col / 3) * 3
			grid = self.grid
			# compute rowScore
			for i in range(9):
				if i == col:
					continue # ignore own's constraint value
				tmp = grid[row][i]
				if tmp.state == '0':
					rowScore += len(tmp.domain)

			# compute colScore
			for i in range(9):
				if i == row:
					continue
				tmp = grid[i][col]
				if tmp.state == '0':
					colScore += len(tmp.domain)

			# compute subGridScore
			for i in range(3):
				for j in range(3):
					if i == row and j == col:
						continue
					tmp = grid[rowBoundary+i][colBoundary+j]
					if tmp.state == '0':
						subGridScore +=  len(tmp.domain)

			return rowScore + colScore + subGridScore
		except IndexError:
			print 'Invalid index access in findEmptyCell()'
			traceback.print_exc()

	# isValidAssignment(nxtEmptyCell, assignment)
	# return boolean value representative of validity/invalidity of 'assignment'
	# at cell location 'nxtEmptyCell'. Furthermore, if the assignment is valid then
	def isValidAssignment(self, nxtEmptyCell, assignment):
		try:
			cell = self.grid[nxtEmptyCell[0]][nxtEmptyCell[1]]
			#assert cell.state == '0' #check to see if nxtEmptyCell location is unassigned (uber-defensive)
			rowConstraintHolds = self.rowConstraintHolds(cell, assignment)
			colConstraintHolds = self.colConstraintHolds(cell, assignment)
			subGridConstraintHolds = self.subGridConstraintHolds(cell, assignment)
			if rowConstraintHolds and colConstraintHolds and subGridConstraintHolds:
				return True
			return False
		except IndexError:
			print 'Invalid index access in isValidAssignment()'
			traceback.print_exc()
		except:
			print 'Error in isValidAssignment()'
			traceback.print_exc()

	# rowConstraintHolds(cell, assignment)
	# returns True if row constraint holds, False if violated
	def rowConstraintHolds(self, cell, assignment):
		try:
			row = self.grid[cell.row]
			for i in range(9):
				if i != cell.col and row[i].state == assignment:
					return False # constraint violated
			return True
		except IndexError:
			print 'Invalid index access in rowConstraintHolds()'
		except:
			print 'Error in rowConstraintHolds()'

	# colConstraintHolds(cell, assignment)
	# returns True if column constraint holds, False if violated
	def colConstraintHolds(self, cell, assignment):
		try:
			grid = self.grid
			for i in range(9):
				if i != cell.row and grid[i][cell.col].state == assignment:
					return False # constrain violated
			return True
		except IndexError:
			print 'Invalid index access in colConstraintHolds()'
		except:
			print 'Error in colConstraintHolds()'

	# subGridConstraintHolds(cell, assignment)
	# returns True if sub-grid constraint holds, False if violated
	def subGridConstraintHolds(self, cell, assignment):
		try:
			# index of upper and left boundaries of the sub-grid
			rowBoundary = (cell.row / 3) * 3
			colBoundary = (cell.col / 3) * 3
			grid = self.grid
			for i in range(3):
				for j in range(3):
					if i != cell.row and j != cell.col and grid[rowBoundary+i][colBoundary+j].state == assignment:
						return False
			return True
		except IndexError:
			print 'Invalid index access in subGridConstraintHolds()'
		except:
			print 'Error in subGridConstraintHolds()'
