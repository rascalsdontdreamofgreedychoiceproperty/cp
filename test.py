import sys
import os
import copy
import pytest
import pdb

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dpll.solver import solve, get_vars
from app.sudoku.solver import solve_sudoku, example_board
from app.sudoku.backtracking import solve_sudoku as backtracking_solve_sudoku
from app.vertexcover.solver import solve_vertex_cover
from app.vertexcover.backtracking import find_minimum_vertex_cover as backtracking_solve_vertex_cover
from parser.cnf_parser import parse_dimacs_cnf
from parser.sudoku_parser import parse_sudoku_csv
from parser.clq_parser import parse_dimacs_clq

#breakpoint()
graph = parse_dimacs_clq("tests/dimacs_mvc/johnson8-2-4.clq")
print(backtracking_solve_vertex_cover(graph))
