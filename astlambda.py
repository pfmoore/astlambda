import ast

# Notes
#
# 1. For functions without a dunder, need something like F.mylen(x) (F turns mylen into an ast generator fn)
# 2. Better name for Expr - AstGen? Names as AstGen.name.x?


_dummy_args = dict(lineno=0, col_offset=0, end_lineno=0, end_col_offset=0)

def _binop(op, rev=False):
    def dunder(self, other):
        cls = type(self)
        names = self.names
        lhs = self.ast
        if isinstance(other, cls):
            rhs = other.ast
            if rev:
                names = other.names
                names.update(self.names)
            else:
                names.update(other.names)
        else:
            rhs = ast.Constant(other, **_dummy_args)
        if rev:
            lhs, rhs = rhs, lhs
        return cls(ast=ast.BinOp(
            left = self.ast,
            op = op(),
            right = rhs,
            **_dummy_args
        ), names=names)
    return dunder

def _cmpop(op):
    def dunder(self, other):
        cls = type(self)
        names = self.names
        if isinstance(other, cls):
            rhs = other.ast
            names.update(other.names)
        else:
            rhs = ast.Constant(other, **_dummy_args)
        return cls(ast=ast.Compare(
            left = self.ast,
            ops = [op()],
            comparators = [rhs],
            **_dummy_args
        ), names=names)
    return dunder

class AstGen:
    def __init__(self, ast, names):
        self.ast = ast
        # De-duplicate name list, relies on dict preserving insertion order
        self.names = dict.fromkeys(names)
        self._fn = None
    @classmethod
    def name(cls, name):
        return cls(ast.Name(name, ast.Load(), **_dummy_args), [name])
    @property
    def fn(self):
        if self._fn is None:
            self._compile_fn()
        return self._fn
    __add__ = _binop(ast.Add)
    __sub__ = _binop(ast.Sub)
    __mul__ = _binop(ast.Mult)
    __matmul__ = _binop(ast.MatMult)
    __truediv__ = _binop(ast.Div)
    __floordiv__ = _binop(ast.FloorDiv)
    __mod__ = _binop(ast.Mod)
    #__divmod__ = _binop(???)
    __pow__ = _binop(ast.Pow)
    __lshift__ =_binop(ast.LShift)
    __rshift__ = _binop(ast.RShift)
    __and__ = _binop(ast.BitAnd)
    __or__ = _binop(ast.BitOr)
    __xor__ = _binop(ast.BitXor)

    __radd__ = _binop(ast.Add, rev=True)
    __rsub__ = _binop(ast.Sub, rev=True)
    __rmul__ = _binop(ast.Mult, rev=True)
    __rmatmul__ = _binop(ast.MatMult, rev=True)
    __rtruediv__ = _binop(ast.Div, rev=True)
    __rfloordiv__ = _binop(ast.FloorDiv, rev=True)
    __rmod__ = _binop(ast.Mod, rev=True)
    #__rdivmod__ = _binop(???, rev=True)
    __rpow__ = _binop(ast.Pow, rev=True)
    __rlshift__ =_binop(ast.LShift, rev=True)
    __rrshift__ = _binop(ast.RShift, rev=True)
    __rand__ = _binop(ast.BitAnd, rev=True)
    __ror__ = _binop(ast.BitOr, rev=True)
    __rxor__ = _binop(ast.BitXor, rev=True)

    #__neg__ = ???
    #__pos__ = ???
    ## __abs__ = ???
    #__invert__ = ???

    __lt__ = _cmpop(ast.Lt)
    __le__ = _cmpop(ast.LtE)
    __eq__ = _cmpop(ast.Eq)
    __ne__ = _cmpop(ast.NotEq)
    __gt__ = _cmpop(ast.Gt)
    __ge__ = _cmpop(ast.GtE)

    __contains__ = _cmpop(ast.In)

    #__getitem__ = ???
    ##__setitem__ = ???
    ##__delitem__ = ???
    def __getattr__(self, name):
        new_ast = ast.Attribute(
            value = self.ast,
            attr = name,
            ctx = ast.Load(),
            **_dummy_args
        )
        return type(self)(ast=new_ast, names=self.names)
    #__setattr__ = ???
    #__delattr__ = ???

    # __call__ = ??? # this clashes with the call method below.

    def _compile_fn(self):
        lambda_ast = ast.Lambda(
            args = ast.arguments(
                posonlyargs = [],
                args = [ast.arg(arg=name, **_dummy_args) for name in self.names],
                kwonlyargs = [],
                kw_defaults = [],
                defaults = []
            ),
            body = self.ast,
            **_dummy_args
        )
        expr_ast = ast.Expression(body=lambda_ast, **_dummy_args)
        print(ast.dump(expr_ast, indent=4))
        code = compile(expr_ast, "", "eval")
        self._fn = eval(code)

    def __call__(self, *args, **kw):
        return self.fn(*args, **kw)

def past(a):
    print(ast.dump(a.ast, indent=4))

if __name__ == "__main__":
    x = AstGen.name("x")
    a = ((x+12)//9).a
    past(a)
    print(a(9))
