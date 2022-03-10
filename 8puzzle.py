from enum import Enum
from astar import Action, Problem, State

class PuzzleState(State):
    # Caselle in ordine di x + y
    slots: tuple[int, int, int, int, int, int, int, int, int]

    def __init__(self, slots):
        assert(len(slots) == 9)
        self.slots = tuple(slots)

    def empty_slot(self):
        """Ritorna la posizione della casella vuota"""
        for i, v in enumerate(self.slots):
            if v == 0: return i
        raise ValueError("Invalid state! There is no empty slot!")

    def is_final(self) -> bool:
        return self.slots == (1, 2, 3, 4, 5, 6, 7, 8, 0)

    def is_invalid(self) -> bool:
        # Qui è inutile controllare la validità dello stato, perchè non è
        # mai possibile giungere ad uno stato invalido tramite le azioni
        # definite in basso

        # Deve esserci uno per ogni numero da 0 a 8
        for i in range(9):
            if i not in self.slots: return True
        return False

    def __hash__(self) -> int:
        return hash(self.slots)

    def __str__(self) -> str:
        def f(n): 
            return str(n) if n else '-'
        s = self.slots
        return f"{f(s[0])} {f(s[1])} {f(s[2])} || {f(s[3])} {f(s[4])} {f(s[5])} || {f(s[6])} {f(s[7])} {f(s[8])}"

class PuzzleMoves(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    
    def direction(move: 'PuzzleMoves') -> tuple[int, int]:
        if move == PuzzleMoves.UP: return 0, -1
        elif move == PuzzleMoves.DOWN: return 0, 1
        elif move == PuzzleMoves.LEFT: return -1, 0
        elif move == PuzzleMoves.RIGHT: return 1, 0
        else: raise ValueError(f"Unknown PuzzleMove {move}")

class PuzzleAction(Action):
    # Direzione in cui muovere lo spazio vuoto
    move: PuzzleMoves

    def __init__(self, move: PuzzleMoves):
        self.move = move

    def index_to_coords(i: int) -> tuple[int, int]:
        return i % 3, i // 3
    def coords_to_index(x: int, y: int) -> int:
        return y * 3 + x

    def apply(self, state: PuzzleState) -> State:
        x, y = PuzzleAction.index_to_coords(state.empty_slot())
        dx, dy = PuzzleMoves.direction(self.move)
        # Assicurati che la mossa sia valida
        if not(0 <= x + dx < 3) or not(0 <= y + dy < 3):
            return None

        slots = list(state.slots)
        # Scambia la casella x,y con la casella x+dx,y+dy
        a = PuzzleAction.coords_to_index(x, y)
        b = PuzzleAction.coords_to_index(x+dx, y+dy)
        temp = slots[a]
        slots[a] = slots[b]
        slots[b] = temp

        new_state = PuzzleState(slots)
        new_state.parent = state
        new_state.action = self

        # Lo stato è ancora sicuramente valido
        return new_state

    def __str__(self):
        return f"Move {self.move.name}"

class EightPuzzleProblem(Problem):
    initial_state = PuzzleState((7, 2, 4, 5, 0, 6, 8, 3, 1))

    def possible_actions(self, state: PuzzleState):
        for i in PuzzleMoves:
            yield PuzzleAction(i)

def misplaced_tiles(state: PuzzleState):
    h = 0
    for i, v in enumerate(state.slots):
        if i != v - 1:
            h += 1
    return h

print("Solving with h(n) = number of misplaced tiles")
problem = EightPuzzleProblem(misplaced_tiles)
sol1 = problem.astar(show=False)
if sol1 is None: print("  No solution found!")
else: print(f"Solution is {len(sol1)} steps")


def total_manhattan_distance(state: PuzzleState):
    h = 0
    for i, v in enumerate(state.slots):
        x, y = PuzzleAction.index_to_coords(i)
        ax, ay = PuzzleAction.index_to_coords(v - 1 if v != 0 else 8)
        h += abs(x - ax) + abs(y - ay)
    return h
print()
print("Solving with h(n) = total Manhattan distance")
problem = EightPuzzleProblem(total_manhattan_distance)
sol2 = problem.astar(show=False)
if sol2 is None: print("  No solution found!")
else: 
    print(f"Best solution in {len(sol2)} steps:")
    state = problem.initial_state
    for i, a in enumerate(sol2):
        state = a.apply(state)
        print(f"{i:3}) {a}")

        sstr = '\n     '.join(str(state).split(' || '))
        print("     " + sstr)