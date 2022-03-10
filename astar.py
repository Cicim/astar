from abc import abstractmethod
from typing import Callable, Generator
import time

class State:
    parent: 'State' = None  # Stato di partenza per arrivare a questo stato
    action: 'Action' = None  # Azione per passare da parent a questo stato

    @abstractmethod
    def is_invalid(self) -> bool:
        """Ritorna se questo stato è invalido, ovvero se non rispetta qualche vincolo"""
        return True

    @abstractmethod
    def is_final(self) -> bool:
        """Ritorna se questo stato è finale, ovvero se è una soluzione valida"""
        return True


class Action:
    cost: int = 1

    @abstractmethod
    def apply(self, state: State) -> State:
        """
        Prova ad applicare questa azione allo stato.

        Se questa azione non dovesse essere valida, o dovesse portare
        ad uno stato invalido, riporta `None`, altrimenti riporta
        lo stato a cui arriva, al quale viene aggiunta l'informazione
        dello stato di partenza e l'azione applicata. """

        return None


CostFunction_t = Callable[[State], int]


class StatePQueue:
    array: list[State]
    cost: CostFunction_t

    def __init__(self, cost: CostFunction_t):
        self.array = []
        self.cost = cost

    def is_root(self, i: int) -> bool:
        return i == 0

    def parent(self, i: int) -> int:
        return (i - 1) >> 1

    def left(self, i: int) -> int | None:
        if 2 * i + 1 >= len(self.array):
            return None
        return 2 * i + 1

    def right(self, i: int) -> int | None:
        if 2 * i + 2 >= len(self.array):
            return None
        return 2 * i + 2

    def __getitem__(self, i: int) -> State:
        return self.array[i]

    def __setitem__(self, i: int, state: State):
        self.array[i] = state

    def cost_by_index(self, i: int) -> int:
        return self.cost(self[i])

    def swap(self, a: int, b: int):
        temp = self[a]
        self[a] = self[b]
        self[b] = temp

    def insert(self, state: State):
        # Trova il nuovo ultimo nodo in cui aggiungere il nuovo elemento
        w = len(self.array)
        # Inserisci l'elemento nella posizione trovata
        self.array.append(state)
        # Ripristina la proprietà di ordinamento con UpHeap sul nuovo nodo
        self._upheap(w)

    def _upheap(self, z: int):
        # Ripristina la proprietà di min-heap dopo l'inserimento
        if self.is_root(z):
            return

        par = self.parent(z)
        if self.cost_by_index(par) > self.cost_by_index(z):
            self.swap(par, z)
            self._upheap(par)

    def remove(self):
        # Trova l'elemento corrente
        w = len(self.array) - 1

        self.swap(0, w)
        # Rimuovi l'elemento più piccolo
        el = self.array.pop()

        self._downheap(0)

        return el

    def _downheap(self, z: int):
        l = self.left(z)
        r = self.right(z)

        # Ripristina la proprietà di min-heap dopo la rimozione
        if l == None:
            return

        small = l
        if r != None:
            if self.cost_by_index(r) < self.cost_by_index(l):
                small = r

        if self.cost_by_index(small) < self.cost_by_index(z):
            self.swap(z, small)
            self._downheap(small)

    def empty(self):
        return len(self.array) == 0

    def __str__(self):
        s = ""
        for i in self.array:
            s += f"{i} "
        return s


class SState(State):
    def __init__(self, a: int): self.a = a
    def __str__(self): return f"{self.a}"


class Problem:
    """Definizione del problema di ricerca da risolvere"""
    initial_state: State
    heuristic: CostFunction_t

    def __init__(self, heuristic: CostFunction_t):
        self.heuristic = heuristic

    @abstractmethod
    def possible_actions(self, state: State) -> Generator[Action, None, None]:
        """Ritorna le azioni possibili a partire dallo stato dato"""
        return None

    def astar(self, state: State = None, show=True) -> list[Action]:
        """
        Risolve il problema con A* e riporta il percorso 
        per arrivare alla soluzione come lista di azioni:

        + `state`: stato dal quale far partire l'algoritmo
                    (di default lo stato definito come `initial_state` per il problema)
        + `show`: se mostrare i passi mentre esegue (default `False`)

        Riporta un percorso di azioni per arrivare alla soluzione
        a partire dallo stato iniziale passato come ingresso,
        oppure `None` se non è stato possibile arrivare ad una soluzione.
        """
        if not state:
            state = self.initial_state
        if state.is_final():
            if show: print("You started from a final state!")
            return []

        # Memorizza gli stati visitati come coppie (hash dello stato, g per lo stato)
        cost_to_reach: dict[int, int] = {hash(state): 0}

        # Frontiera: dove inserire ed estrarre gli stati da analizzare
        fringe: StatePQueue = StatePQueue(
            lambda s: self.heuristic(s) + cost_to_reach[hash(s)])
            
        fringe.insert(state)

        # Oggetto della classe State con i riferimenti per ricostruire il percorso
        final_state: State = None

        # Tempo impiegato dall'algoritmo (in passi e secondi)
        extracted_count = 0
        start_time = time.perf_counter()

        # Finché ci sono stati nella frontiera
        while not fringe.empty() and not final_state:
            extracted = fringe.remove()
            extracted_count += 1

            if show:
                print()
                print(f"Popped n = `{extracted}`")
                print(f" with h(n)={self.heuristic(extracted)}, g(n)={cost_to_reach[hash(extracted)]}")
                print("Applyable actions:")

            for a in self.possible_actions(extracted):
                # Prova ad applicare l'azione a allo stato estratto
                new_state = a.apply(extracted)

                # Se questa porta ad uno stato valido
                if new_state != None:
                    if show:
                        print(f" > {a}")

                    # Se questo stato è finale, interrompi il ciclo
                    if new_state.is_final():
                        final_state = new_state
                        if show:
                            print(f"    Final state `{new_state}`")
                        break

                    # Che non è già stato visitato
                    if cost_to_reach.get(hash(new_state), None) == None:
                        # Aggiungilo alla lista degli stati visitati
                        cost_to_reach[hash(new_state)] = cost_to_reach[hash(
                            extracted)] + a.cost
                        # ...e alla frontiera
                        fringe.insert(new_state)

                        if show:
                            print(f"    Reached `{new_state}`")
                    else:
                        if show:
                            print("    ALREADY VISITED!")
        elapsed = time.perf_counter() - start_time
        print(
            f"Parsed {extracted_count} states in {round(elapsed * 1000 * 100) / 100} ms")

        # Se sei arrivato ad uno stato finale
        if final_state == None:
            if show: print("... but no solution was found")
            return None
        # Ricostruisci la sequenza di azioni
        actions: list[Action] = []
        current_state = final_state

        while current_state.parent != None:
            actions.insert(0, current_state.action)
            current_state = current_state.parent

        return actions
