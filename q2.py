"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])

        self.goals = []
        self.boxes = []
        self.walls = []
        self.player_start = None

        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()

        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        # TODO: Implement parsing logic
        for i in range(self.N):
            for j in range(self.M):
                if self.grid[i][j]=="G":
                    self.goals.append((i, j))
                elif self.grid[i][j]=="B":
                    self.boxes.append((i, j))
                elif self.grid[i][j]=="P":
                    self.player_start = (i, j)
                elif self.grid[i][j]=="#":
                    self.walls.append((i, j))
        return

    # ---------------- Variable Encoding ----------------
    def var_player(self, x, y, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return (1 + 1000*x + 100*y + t)
        

    def var_box(self, b, x, y, t):
        """
        Variable ID for box b at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return (10000*(b+1) + 1000*x + 100*y + t)
        

    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        # 1. Initial conditions
        # 2. Player movement
        # 3. Box movement (push rules)
        # 4. Non-overlap constraints
        # 5. Goal conditions
        # 6. Other conditions

        # storing the valid positions (coordinates where wall is not there)
        valid_positions = []
        for i in range(self.N):
            for j in range(self.M):
                if (i, j) not in self.walls:
                    valid_positions.append((i, j))

        # initial conditions
        # initial position of player 
        self.cnf.append([self.var_player(self.player_start[0], self.player_start[1], 0)])   
        
        # initial positions of boxes    
        for b in range(0,self.num_boxes):
            self.cnf.append([self.var_box(b, self.boxes[b][0], self.boxes[b][1], 0)])    

        # coordinates of player lie within valid positions 
        for t in range(0,self.T+1):
            self.cnf.append([self.var_player(x, y, t) for (x,y) in valid_positions])
        
        #  at a given time, player is at atmost one cell       
        for t in range(self.T+1):
            for i in range(len(valid_positions)):
                for j in range(i+1, len(valid_positions)):
                    p1 = valid_positions[i]
                    p2 = valid_positions[j]

                    self.cnf.append([-self.var_player(p1[0], p1[1], t), -self.var_player(p2[0], p2[1], t)])

        # box coordinates lie within valid positions
        for t in range(0,self.T+1):
            for b in range(0, self.num_boxes):
                self.cnf.append([self.var_box(b, x, y, t) for x, y in valid_positions])
            
        # at a given time, box is at atmost one position
        for t in range(self.T+1):
            for b in range (self.num_boxes):
                for i in range(len(valid_positions)):
                    for j in range(i+1, len(valid_positions)):
                        p1 = valid_positions[i]
                        p2 = valid_positions[j]

                        self.cnf.append([-self.var_box(b, p1[0], p1[1], t), -self.var_box(b, p2[0], p2[1], t)])

        # player and box can't overlap
        for t in range(0,self.T+1):
            for x, y in valid_positions:
                for b in range(self.num_boxes):
                    self.cnf.append([-self.var_player(x,y,t), -self.var_box(b,x,y,t)])

        # boxes can't overlap
        for t in range(0,self.T+1):
            for x, y in valid_positions:
                for b1 in range(0, self.num_boxes-1):
                    for b2 in range(b1+1, self.num_boxes):
                        self.cnf.append([-self.var_box(b1, x, y, t), -self.var_box(b2, x, y, t)])

        # if player is at some position at t then he can be at the same position or any adjacent valid position at time t+1
        for t in range(self.T):
            for x, y in valid_positions:
                possible_next_positions = [-self.var_player(x, y, t), self.var_player(x, y, t+1)]

                for dx, dy in DIRS.values():
                    npx, npy = x + dx, y + dy
                    if(npx, npy) in valid_positions:
                        possible_next_positions.append(self.var_player(npx, npy, t+1))
                
                self.cnf.append(possible_next_positions)

        # if player-box-empty at t then at t+1 either box at same position and player at some other adjacent position or box goes
        # in the empty cell and player occupies box's position at t+1
        for t in range(0,self.T):
            for b in range(0,self.num_boxes):
                for x, y in valid_positions:
                    for (dx, dy) in DIRS.values():
                        bx, by = x+dx, y+dy
                        bx2, by2 = x+2*dx, y+2*dy

                        if (bx,by) in valid_positions and (bx2,by2) in valid_positions:

                            # precondition: player at (x,y) and box at (bx,by) at time t
                            precond = [-self.var_player(x,y,t), -self.var_box(b,bx,by,t)]

                            clause1 = [self.var_box(b,bx,by,t+1), self.var_player(bx,by,t+1)]
                            clause2 = [self.var_box(b,bx,by,t+1), self.var_box(b, bx2, by2, t+1)]

                            self.cnf.append(precond+clause1)
                            self.cnf.append(precond+clause2)


        # if box is not pushed then it stays in the same place
        for t in range(0, self.T):
            for b in range(0, self.num_boxes):
                for x, y in valid_positions:
                    stay_clause = [-self.var_box(b, x, y, t), self.var_box(b, x, y, t + 1)]

                    for dx, dy in DIRS.values():
                        px, py = x - dx, y - dy
                        nx, ny = x + dx, y + dy
                        if (px,py) in valid_positions and (nx,ny) in valid_positions:
                            stay_clause.append(self.var_player(px, py, t))
                    self.cnf.append(stay_clause)
        
        # goal condition
        for b in range(0,self.num_boxes):
            self.cnf.append([self.var_box(b,gx,gy,self.T) for (gx,gy) in self.goals])

        # return the cnf formula
        return self.cnf
    
def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    N, M, T = encoder.N, encoder.M, encoder.T

    # TODO: Map player positions at each timestep to movement directions
    moves = []
    positions = []

    # Extract player positions
    for t in range(0, T+1):
        found = False
        for x in range(0,N):
            for y in range(0,M):
                if (encoder.var_player(x, y, t)) in model:
                    positions.append((x,y))
                    found = True
                    break
            if found:
                break
                
    # Convert position differences into moves
    for t in range(0,T):
        x, y = positions[t]
        nx, ny = positions[t+1]
        if nx == x - 1: 
            moves.append("U")
        elif nx == x + 1: 
            moves.append("D")
        elif ny == y - 1: 
            moves.append("L")
        elif ny == y + 1: 
            moves.append("R")

    return moves


def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1

        model = solver.get_model()
        if not model:
            return -1

        return decode(model, encoder)
