from collections import deque
from functools import cmp_to_key

class Sudoku:
    def __init__(self, grid):
        self.grid = grid
        self.size = len(grid)
        self.variables, self.domains, self.constraints = self.create_csp_representation()
        self.neighbors = self.compute_neighbors()

    def create_csp_representation(self):
        variables = [(i, j) for i in range(self.size) for j in range(self.size)]
        domains = {(i, j): {val for val in range(1, self.size + 1)} if self.grid[i][j] == 0 else {self.grid[i][j]} for i, j in variables}
        constraints = [((i, j), (i, k)) for i in range(self.size) for j in range(self.size) for k in range(j + 1, self.size)] + \
              [((i, j), (k, j)) for i in range(self.size) for j in range(self.size) for k in range(i + 1, self.size)] + \
              [((i, j), (i // 3 * 3 + k // 3, j // 3 * 3 + k % 3)) for i in range(self.size) for j in range(self.size) for k in range(9) if (i // 3 * 3 + k // 3, j // 3 * 3 + k % 3) != (i, j)]

        return variables, domains, constraints

    def compute_neighbors(self):
        neighbors = {v: set() for v in self.variables}
        for (v1, v2) in self.constraints:
            neighbors[v1].add(v2)
            neighbors[v2].add(v1)
        return neighbors

    def revise(self, xi, xj):
        revised = False
        for x in self.domains[xi].copy():
            if all(x == y for y in self.domains[xj]):
                self.domains[xi].remove(x)
                revised = True
        return revised

    def ac3(self, queue=None):
        if queue is None:
            queue = deque(self.constraints)
        while queue:
            (xi, xj) = queue.popleft()
            if self.revise(xi, xj):
                if len(self.domains[xi]) == 0:
                    return False
                for xk in self.neighbors[xi] - {xj}:
                    queue.append((xk, xi))
        return all(len(self.domains[v]) >= 1 for v in self.variables)
    
    def minimum_remaining_values(self, assignment):
       unassigned = [v for v in self.variables if v not in assignment]
       if not unassigned:
           return None

       mrv = lambda v: len(self.domains[v])
       return min(unassigned, key=mrv)
   
    def select_unassigned_variable(self, assignment):
        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            return None

        mrv = lambda v: len(self.domains[v])
        degree = lambda v: len(self.neighbors[v])
        unassigned.sort(key=cmp_to_key(lambda x, y: (mrv(x) - mrv(y)) or (degree(y) - degree(x))))
        return unassigned[0]

    def is_consistent(self, assignment, var, value):
        for neighbor in self.neighbors[var]:
            if assignment.get(neighbor) == value:
                return False
        return True

    def backtrack(self, assignment, failed_values=None, backtracks_count=None):
        if failed_values is None:
            failed_values = {v: set() for v in self.variables}
        if backtracks_count is None:
            backtracks_count = {v: 0 for v in self.variables}

        if len(assignment) == len(self.variables):
            return assignment, backtracks_count
        var = self.select_unassigned_variable(assignment)
        if var is None:
            return None, backtracks_count
        for value in self.domains[var]:
            if self.is_consistent(assignment, var, value):
                assignment[var] = value
                if self.ac3():
                    result, updated_backtracks_count = self.backtrack(assignment, failed_values, backtracks_count)
                    if result:
                        return result, updated_backtracks_count
                del assignment[var]
                failed_values[var].add(value)
                backtracks_count[var] += 1
        return None, backtracks_count

    def solve(self):
        assignment = {}
        self.ac3()
        solution, backtracks_count = self.backtrack(assignment)
        return solution, backtracks_count

    def printing(self, solution):
        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(solution[(i, j)])
            print(row)

initial_grid = [
    [7, 0, 0, 4, 0, 0, 0, 8, 6],
    [0, 5, 1, 0, 8, 0, 4, 0, 0],
    [0, 4, 0, 3, 0, 7, 0, 9, 0],
    [3, 0, 9, 0, 0, 6, 1, 0, 0],
    [0, 0, 0, 0, 2, 0, 0, 0, 0],
    [0, 0, 4, 9, 0, 0, 7, 0, 8],
    [0, 8, 0, 1, 0, 2, 0, 6, 0],
    [0, 0, 6, 0, 5, 0, 9, 1, 0],
    [2, 1, 0, 0, 0, 3, 0, 0, 5]
]

sudoku = Sudoku(initial_grid)
(solution, backtracks_count) = sudoku.solve()

print("Solution:")
sudoku.printing(solution)
print("\nVariables:\n", sudoku.variables)
print("\nDomains:\n", sudoku.domains)
print("\nConstraints:\n", sudoku.constraints)
print("\nBacktracks count:\n",backtracks_count)

xi = (0, 1)  # Choose a specific variable xi
xj = (0, 2)  # Choose a specific variable xj

revised_result = sudoku.revise(xi, xj)

print("\nBoolean result of the revise function:", revised_result)
print("\nAll variables have at least one value left in their domains: ", sudoku.ac3())
