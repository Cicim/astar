from enum import Enum
from astar import Action, CostFunction_t, Problem, State


class FroggerState(State):
    # Ogni stato deve avere un riferimento alla mappa per calcolare
    # se è valido o se è finale
    problem: 'FroggerProblem'

    x: int  # Posizione della rana sull'asse x
    y: int  # Posizione della rana sull'asse y
    t: int  # Posizione nel tempo della rana.
    # il range di questo valora cambia
    # a seconda della dimensione della mappa

    def __init__(self, problem: 'FroggerProblem', x: int, y: int, t: int):
        self.problem = problem
        self.x = x
        self.y = y
        self.t = t

    def is_final(self) -> bool:
        # Gli stati finali sono tutti quelli che terminano nella prima riga
        return self.y == 0

    def is_invalid(self) -> bool:
        # Assicurati che la rana sia entro i confini della mappa
        if self.x < 0 or self.x >= self.problem.width\
                or self.y < 0 or self.y >= self.problem.height:
            return True

        # Ottieni la riga in cui si trova la rana
        frog_row = self.problem.game_map[self.y]
        # Ottieni la posizione shiftata del tempo t
        # seguendo la direzione del traffico in questa riga
        d = self.problem.traffic_directions[self.y]

        x = self.x - d * self.t
        return frog_row[x % self.problem.width] == 1

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.t))

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.t})"


class FroggerMove(Enum):
    # 0-Nothing, 1-left, 2-up, 3-right, 4-down
    Nothing = 0
    Left = 1
    Up = 2
    Right = 3
    Down = 4


class FroggerAction(Action):
    move: FroggerMove

    def __init__(self, move: FroggerMove):
        self.move = move

    def apply(self, state: FroggerState) -> FroggerState:
        problem, x, y, t = state.problem, state.x, state.y, state.t

        # Muoviti nella direzione descritta
        if self.move == FroggerMove.Up:
            y -= 1
        elif self.move == FroggerMove.Down:
            y += 1
        elif self.move == FroggerMove.Left:
            x -= 2
        elif self.move == FroggerMove.Right:
            x += 2
        elif self.move == FroggerMove.Nothing:
            pass
        else:
            raise ValueError("Invalid move")

        # Incrementa il tempo (modulo larghezza della mappa)
        t = (t + 1) % problem.width

        new_state = FroggerState(problem, x, y, t)
        if new_state.is_invalid():
            return None
        new_state.parent = state
        new_state.action = self

        return new_state

    def __str__(self) -> str:
        if self.move == FroggerMove.Nothing:
            return "Do Nothing"
        return f"Move {self.move.name}"


class FroggerProblem(Problem):
    # Mappa del gioco
    game_map: list[list[int]]
    # Movimento delle macchine per ogni riga
    traffic_directions: list[int]

    width: int
    height: int

    def __init__(self, game_map: list[list[int]], car_moves: list[int], heuristic: CostFunction_t):
        super().__init__(heuristic)

        self.initial_state = FroggerState(self, 7, 7, 0)

        self.game_map = game_map
        self.traffic_directions = car_moves
        # Dimensioni della mappa di gioco
        self.width, self.height = len(game_map[0]), len(game_map)

    def possible_actions(self, _):
        for move in FroggerMove:
            yield FroggerAction(move)
