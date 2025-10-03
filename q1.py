"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List
import math

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""

    # TODO: implement encoding and solving using PySAT

    cnf1 = CNF()

    n = len(grid)
    sqrt_n = int(math.sqrt(n))

    # each row must contain all numbers
    for row in range(1,n+1):
        for num in range(1,n+1):
            cnf1.append([100*row+10*column+num for column in range(1,n+1)])

    # each column must contain all numbers
    for column in range(1,n+1):
        for num in range(1,n+1):
            cnf1.append([100*row+10*column+num for row in range(1,n+1)])
    
    # each 3x3 subgrid must contain all numbers
    for rownums in range(1,n+1,sqrt_n):
        for colnums in range(1,n+1,sqrt_n):
            for num in range(1,n+1):
                cnf1.append([100*(rownums+dr)+10*(colnums+dc)+num for dr in range(sqrt_n) for dc in range(sqrt_n)])
    
    # each cell can contain only one number
    for row in range(1,n+1):
        for column in range(1,n+1):
            for num1 in range(1,n+1):
                for num2 in range(num1+1,n+1):
                    cnf1.append([-(100*row+10*column+num1), -(100*row+10*column+num2)])
    
    # initial conditions
    for row in range(0,n):
        for column in range(0,n):
            if grid[row][column] != 0:
                cnf1.append([100*(row+1)+10*(column+1)+grid[row][column]])

    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf1.clauses)
        if solver.solve():
            model = solver.get_model()

            ans = [[0 for i in range(n)] for j in range(n)]

            for value in model:
                if value>0:
                    num = value%10
                    column = (value//10)%10
                    row = value//100
                    if 1<=row<=n and 1<=column<=n and 1<=num<=n:
                        ans[row-1][column-1] = num
            return ans

        else:
            return grid

