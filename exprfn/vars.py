from . import ExprFn

for name in "abcdefghijklmnopqrstuvwxyz":
    globals()[name] = ExprFn.name(name)