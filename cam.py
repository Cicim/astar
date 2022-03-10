# Implementazione della soluzione tramite A* del problema
# "Cannibali e Missionari"
from astar import Action, Problem, State


class CamState(State):
    ca: int
    cb: int
    ma: int
    mb: int
    boat: bool

    def __init__(self, ca: int, ma: int, cb: int, mb: int, boat: bool) -> None:
        self.ca = ca
        self.cb = cb
        self.ma = ma
        self.mb = mb
        self.boat = boat

    def is_invalid(self) -> bool:
        # Affinché questo stato sia valido devono valere le seguenti condizioni:
        # + il numero di cannibali totali deve essere 3
        # + il numero di missionari totali deve essere 3
        # + il numero di missionari o cannibali sulla prima o sulla seconda
        #   sponda del fiume deve essere compreso tra 0 e 3 (inclusi)
        # + su una sponda ci sono più cannibali che missionari
        return self.ca + self.cb != 3 or\
            self.ma + self.mb != 3 or\
            not(0 <= self.ca <= 3) or\
            not(0 <= self.cb <= 3) or\
            not(0 <= self.ma <= 3) or\
            not(0 <= self.mb <= 3) or\
            self.ma != 0 and self.ca != 0 and self.ca > self.ma or\
            self.mb != 0 and self.cb != 0 and self.cb > self.mb

    def is_final(self) -> bool:
        # Esiste una sola configurazione finale
        return (self.ca, self.ma, self.cb, self.mb) == (0, 0, 3, 3)

    def __hash__(self) -> int:
        return hash((self.ca, self.ma, self.cb, self.mb, self.boat))

    def __str__(self):
        bank1 = f"{'C '*self.ca} {'M '*self.ma}"
        river = "  B" if self.boat else "B  "
        bank2 = f"{'C '*self.cb} {'M '*self.mb}"

        return f"{bank1}|{river}|{bank2}"


class Carry(Action):
    """Azione che corrisponde a portare missionari e/o cannibali
       dalla riva A alla riva B del fiume"""
    cannibals: int
    missionaries: int

    def __init__(self, c: int, m: int):
        self.cannibals = c
        self.missionaries = m

    def apply(self, state: State):
        # Assicurati che l'azione sia valida
        if self.cannibals + self.missionaries > 2:
            return None

        new_state = CamState(state.ca - self.cannibals, state.ma - self.missionaries,
                             state.cb + self.cannibals, state.mb + self.missionaries,
                             True)

        if new_state.is_invalid():
            return None
        new_state.parent = state
        new_state.action = self
        return new_state

    def __str__(self):
        m = f"missionar{'y' if self.missionaries == 1 else 'ies'}"
        c = f"cannibal{'' if self.cannibals == 1 else 's'}"

        if self.cannibals == 0:
            return f"Carry {self.missionaries} {m}"
        elif self.missionaries == 0:
            return f"Carry {self.cannibals} {c}"
        else:
            return f"Carry {self.cannibals} {c} and {self.missionaries} {m}"


class CarryBack(Action):
    """Azione che corrisponde a portare missionari e/o cannibali
       dalla riva B alla riva A del fiume"""
    cannibals: int
    missionaries: int

    def __init__(self, c: int, m: int):
        self.cannibals = c
        self.missionaries = m

    def apply(self, state: State):
        # Assicurati che l'azione sia valida
        if self.cannibals + self.missionaries > 2:
            return None

        new_state = CamState(state.ca + self.cannibals, state.ma + self.missionaries,
                             state.cb - self.cannibals, state.mb - self.missionaries,
                             False)

        if new_state.is_invalid():
            return None
        new_state.parent = state
        new_state.action = self
        return new_state

    def __str__(self):
        m = f"missionar{'y' if self.missionaries == 1 else 'ies'}"
        c = f"cannibal{'' if self.cannibals == 1 else 's'}"

        if self.cannibals == 0:
            return f"Carry back {self.missionaries} {m}"
        elif self.missionaries == 0:
            return f"Carry back {self.cannibals} {c}"
        else:
            return f"Carry back {self.cannibals} {c} and {self.missionaries} {m}"


class CannibalsAndMissionaries(Problem):
    initial_state = CamState(3, 3, 0, 0, False)

    def possible_actions(self, state: State):
        # Se sei sulla prima sponda
        if not state.boat:
            # Riporta tutte le azioni di Carry
            for i in range(0, state.ca+1):
                for j in range(0, state.ma+1):
                    if 0 < i + j <= 2:
                        yield Carry(i, j)
        # Se sei sulla seconda sponda
        else:
            # Riporta tutte le azioni di CarryBack
            for i in range(0, state.cb+1):
                for j in range(0, state.mb+1):
                    if 0 < i + j <= 2:
                        yield CarryBack(i, j)


def heuristic(state: CamState):
    return state.ca + state.cb


problem = CannibalsAndMissionaries(heuristic)
solution = problem.astar(show=True)

print()
print("Objective:")
print(f" + Reach the state {CamState(0, 0, 3, 3, True)}")
print(f"Best solution in {len(solution)} steps:")
if solution is None:
    print(" No solution?")
else:
    state = problem.initial_state
    for i, step in enumerate(solution):
        print("\t", state)
        state = step.apply(state)
        print(f"{i+1:3}) {step}")
    print("\t", state)
