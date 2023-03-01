class Velocity:
    def __init__(self, left=0, right=0) -> None:
        self.left = left
        self.right = right

    left: float
    right: float

    def is_straight(self):
        return round(self.left, 1) == round(self.right, 1)

    def __eq__(self, __o: object) -> bool:
        assert isinstance(__o, Velocity)
        return self.left == __o.left and self.right == __o.right
