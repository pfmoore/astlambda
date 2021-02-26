from . import ExprFn

for name in "abcdefghijklmnopqrstuvwxyz_":
    globals()[name] = ExprFn.name(name)

for n in range(10):
    name = f"_{n}"
    globals()[name] = ExprFn.name(name)
