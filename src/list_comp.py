a = [
    {"age": 16, "name": "Костя"},
    {"age": 22, "name": "Миша"},
]
b = [person["name"] for person in a if person["age"] < 18]


q = [1, 2, 3, 4, 5]
z = [number**2 if (number % 2 == 0) else number ** 3 for number in q]

# condition ? (if true) : (if false)
# 3 < a ? "Привет" : "Пока"

# (if true) if condition else (if false)
# "Привет" if 3 < a else "Пока"

tt = [[1, 2, 3], [3, 4, 5]]
t = [sum([el**2 for el in list_]) for list_ in tt]
print(t)
dt = [("Костя", 16), ("Давид", 16)]
d = {
    name: {"age": age, "is_legal_age": age >= 18}
    for name, age in dt
    if name.startswith("Д")
}
print(d)
