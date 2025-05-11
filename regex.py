"""
regex.py
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    """
    Abstract base class.
    """
    @abstractmethod
    def __init__(self) -> None:
        """
        Initialize a new state. To be implemented by subclasses.
        """
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        Checks whether the current character satisfies the condition of this state.
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        """
        function checks whether occured character is handled by current ctate
        """
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    """
    Represents the starting state.
    """
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return super().check_self(char)


class TerminationState(State):
    """
    Represents the accepting state.
    """
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char: str):
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """
    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return self.curr_sym == curr_char


class StarState(State):
    """
    Represents a '*' repetition state.
    """
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char):
        for state in self.next_states:
            if state.check_self(char):
                return True

        return False


class PlusState(State):
    """
    Represents a '+' repetition state.
    """
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char):
        return False


class RegexFSM:
    """
    Builds and evaluates a regex pattern.
    """
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        """
        Constructs the graph from the given regex expression.
        """
        self.fsm_head = StartState()
        self.curr_state = self.fsm_head

        current_state = self.curr_state

        index = 0
        while index < len(regex_expr):
            token = regex_expr[index]

            next_char_is_star = False
            if index + 1 < len(regex_expr):
                if regex_expr[index + 1] == '*':
                    next_char_is_star = True

            next_char_is_plus = False
            if index + 1 < len(regex_expr):
                if regex_expr[index + 1] == '+':
                    next_char_is_plus = True

            if next_char_is_star:
                char_state = self.__init_next_state(token, current_state, None)
                star_state = StarState(char_state)

                current_state.next_states.append(star_state)
                star_state.next_states.append(char_state)
                char_state.next_states.append(star_state)

                current_state = star_state
                index += 2

            elif next_char_is_plus:
                char_state = self.__init_next_state(token, current_state, None)
                plus_state = PlusState(char_state)

                current_state.next_states.append(char_state)
                char_state.next_states.append(plus_state)
                plus_state.next_states.append(char_state)

                current_state = plus_state
                index += 2

            else:
                new_state = self.__init_next_state(token, current_state, None)
                current_state.next_states.append(new_state)
                current_state = new_state
                index += 1

        termination_node = TerminationState()
        current_state.next_states.append(termination_node)

    def __init_next_state(
            self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        """
        Creates a new state based on the current regex token.
        """
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError()

        return new_state

    def get_closure(self, states: set[State]) -> set[State]:
        """
        Computes the epsilon closure for a given set of states.
        """
        closing = set(states)
        queue = list(states)

        while queue:
            current_state = queue.pop(0)

            if isinstance(current_state, (StarState, PlusState)):
                for next_state in current_state.next_states:
                    if next_state != current_state.checking_state:
                        if next_state not in closing:
                            closing.add(next_state)
                            queue.append(next_state)

            elif isinstance(current_state, StartState):
                for next_state in current_state.next_states:
                    if next_state not in closing:
                        closing.add(next_state)
                        queue.append(next_state)

        return closing

    def check_string(self, text_to_check: str) -> bool:
        """
        Evaluates whether the input string matches the compiled regex.
        """
        current_active_states = self.get_closure({self.curr_state})

        for char in text_to_check:
            next_active_states = set()

            for active_state in current_active_states:
                if isinstance(active_state, (StarState, PlusState)):
                    if active_state.checking_state.check_self(char):
                        for s in active_state.checking_state.next_states:
                            next_active_states.add(s)

                elif isinstance(active_state, (AsciiState, DotState)):
                    if active_state.check_self(char):
                        for s in active_state.next_states:
                            next_active_states.add(s)

            if not next_active_states:
                return False

            current_active_states = self.get_closure(next_active_states)

        for final_state in current_active_states:
            if isinstance(final_state, TerminationState):
                return True

        return False


# if __name__ == "__main__":
#     regex_pattern = "a*4.+hi"

#     regex_compiled = RegexFSM(regex_pattern)

#     print(regex_compiled.check_string("aaaaaa4uhi"))  # True
#     print(regex_compiled.check_string("4uhi"))  # True
#     print(regex_compiled.check_string("meow"))  # False