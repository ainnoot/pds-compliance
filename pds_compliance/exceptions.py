class MissingProbability(Exception):
    def __init__(self, c):
        super().__init__(f"Missing probability for {c=}.")


class InvalidProbability(Exception):
    def __init__(self, c, p):
        super().__init__(f"Probability should be in [0,1], found {p=} for {c=}.")
