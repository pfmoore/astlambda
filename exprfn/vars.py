from . import AstGen

for name in "abcdefghijklmnopqrstuvwxyz":
    globals()[name] = AstGen.name(name)