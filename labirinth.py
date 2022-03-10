from copy import copy
import math
from tracemalloc import start
from turtle import width
from astar import CostFunction_t, State, Action, Problem


class LabState(State):
    problem: 'LabirinthProblem'
    x: int
    y: int

    def __init__(self, problem: 'LabirinthProblem', x: int, y: int):
        self.problem = problem
        self.x, self.y = x, y

    def is_final(self) -> bool:
        return (self.x, self.y) == self.problem.end_pos

    def is_invalid(self) -> bool:
        lab = self.problem.labirinth
        w, h = self.problem.width, self.problem.height
        x, y = self.x, self.y

        if x < 0 or x >= w or y < 0 or y >= h:
            return True
        return lab[self.y][self.x] != 0

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __str__(self):
        return f"[{self.x}, {self.y}]"


MOVES = {
    'north':        (0, -1, 1, '↑'),
    'north-east':   (1, -1, 2, '↗'),
    'east':         (1,  0, 1, '→'),
    'south-east':   (1,  1, 2, '↘'),
    'south':        (0,  1, 1, '↓'),
    'south-west':   (-1,  1, 2, '↙'),
    'west':         (-1,  0, 1, '←'),
    'north-west':   (-1, -1, 2, '↖'),
}

class LabAction(Action):
    dx: int
    dy: int
    name: str

    def __init__(self, name: str):
        self.name = name
        self.dx, self.dy, self.cost, _ = MOVES[name]

    def apply(self, state: LabState) -> LabState:
        x, y = state.x, state.y
        x, y = x + self.dx, y + self.dy

        new_state = LabState(state.problem, x, y)
        if new_state.is_invalid():
            return None
        new_state.parent = state
        new_state.action = self
        return new_state

    def __str__(self):
        return f"Move {self.name}"


class LabirinthProblem(Problem):
    labirinth: list[list[int]]
    width: int
    height: int

    def __init__(self, labirinth: list[list[int]],
                 heuristic: CostFunction_t,
                 end_pos: tuple[int, int], start_pos=(0, 0),
                 allow_diagonal = False):
        self.labirinth = labirinth
        self.width = len(labirinth[0])
        self.height = len(labirinth)
        self.heuristic = heuristic
        self.allow_diagonal = allow_diagonal

        self.initial_state = LabState(self, start_pos[0], start_pos[1])
        self.end_pos = end_pos

    def possible_actions(self, state: LabState):
        for move in MOVES:
            if not self.allow_diagonal and '-' in move:
                continue
            yield LabAction(move)


# Utility per risolvere un labirinto (sfrutta A*)
def solve_labirinth(labirinth, start_pos, end_pos, show_steps=True, allow_diagonal=True):
    def heuristic(state: LabState):
        return math.floor(math.sqrt((state.x - end_pos[0])**2 + (state.y - end_pos[1])**2))

    problem = LabirinthProblem(labirinth, heuristic, end_pos, start_pos, allow_diagonal)
    solution = problem.astar(show=False)

    if solution is None:
        print(" There is no solution!")
        return

    solved = copy(labirinth)
    x, y = start_pos
    cost = 0
    for i, a in enumerate(solution):
        solved[y][x] = MOVES[a.name][3]

        # Applica l'azione
        x += a.dx
        y += a.dy
        cost += a.cost

        if show_steps:
            print(f"{i:3}) {a}")

    solved[y][x] = "*"

    print(f"Solution is {len(solution)} steps (total cost={cost})")
    for row in solved:
        for x, n in enumerate(row):
            if n == 1: print("█", end="")
            elif n == 0: print(" ", end="")
            else: print(f"{n}", end="")
        print()



labirinth = [
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
]
start_pos = (0, 0)
end_pos = (4, 0)

solve_labirinth(labirinth, start_pos, end_pos, show_steps=False, allow_diagonal=True)


labirinth = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1],
    [1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
]
start_pos = (1, 1)
end_pos = (10, 7)
solve_labirinth(labirinth, start_pos, end_pos, show_steps=False, allow_diagonal=False)
