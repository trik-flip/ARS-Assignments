def rosenbrock(x, y, a=1, b=100):
    """Min at (x=a, y=a**2)"""
    return (a - x) ** 2 + b * (y - x**2) ** 2
