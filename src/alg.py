import math


def solve_quadratic(a: int, b: int, c: int):
    D = b**2 - 4 * a * c
    if D < 0:
        return None

    if D == 0:
        return -b / 2 * a

    return (-b + (D_root := math.sqrt(D))) / (double_a := 2 * a), (
        -b + D_root
    ) / double_a
