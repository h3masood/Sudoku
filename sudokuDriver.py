from sudokuSolver import *
import sys
import traceback

def main(argv=sys.argv):
	try:
		if len(argv) == 1:
			print 'Provide name of the sudoku problem input file'
			return
		for i in range(1, len(argv)):
			filename = argv[i]
			sudokuPuzzle = SudokuPuzzle(filename)
			#solved = sudokuPuzzle.solveVersionA()
			#solved = sudokuPuzzle.solveVersionB()
			solved = sudokuPuzzle.solveVersionC()
			if not solved:
				print 'Failed to solve the sudoku problem instance in file ' + filename
				return
			sudokuPuzzle.printGrid()
			print sudokuPuzzle.totalAssignments
	except AssignmentLimitReachedException as e:
		print 'Failed to solve the sudoku problem instance in file ' + filename
		print e.msg
	except:
		traceback.print_exc()

if __name__ == '__main__':
	main()
