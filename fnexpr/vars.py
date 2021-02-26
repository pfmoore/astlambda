from . import FnExpr

for name in "abcdefghijklmnopqrstuvwxyz_":
    globals()[name] = FnExpr.name(name)

for n in range(10):
    name = f"_{n}"
    globals()[name] = FnExpr.name(name)
