import ast

_dummy_args = dict(lineno=0, col_offset=0, end_lineno=0, end_col_offset=0)

def _binop(op):
    def dunder(self, other):
        if isinstance(other, Expr):
            rhs = other.ast
        else:
            rhs = ast.Constant(other, **_dummy_args)
        return Expr(ast.BinOp(
            left = self.ast,
            op = op(),
            right = rhs,
            **_dummy_args
        ))
    return dunder

class Expr:
    def __init__(self, ast):
        self.ast = ast
        self._fn = None
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
    #__divmod__ = _binop(ast.FloorDiv)
    __pow__ = _binop(ast.Pow)
    __lshift__ =_binop(ast.LShift)
    __rshift__ = _binop(ast.RShift)
    __and__ = _binop(ast.BitAnd)
    __or__ = _binop(ast.BitOr)
    __xor__ = _binop(ast.BitXor)

    def _compile_fn(self):
        lambda_ast = ast.Lambda(
            args = ast.arguments(
                posonlyargs = [],
                args = [ast.arg(arg="x", **_dummy_args)],
                kwonlyargs = [],
                kw_defaults = [],
                defaults = []
            ),
            body = self.ast,
            **_dummy_args
        )
        expr_ast = ast.Expression(body=lambda_ast, **_dummy_args)
        print(ast.dump(expr_ast))
        code = compile(expr_ast, "", "eval")
        self._fn = eval(code)

    def __call__(self, *args, **kw):
        return self.fn(*args, **kw)

if __name__ == "__main__":
    x = Expr(ast.Name("x", ast.Load(), **_dummy_args))
    print(((x+12)//9)(9))