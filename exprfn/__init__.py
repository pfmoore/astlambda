"""Anonymous functions as expressions.

Build anonymous functions (lambdas) by writing expressions using placeholders for variables.

>>> from exprfn.vars import x
>>> fn = (x * 12)
>>> fn(2)
24

"""

import ast
import sys

# Notes
#
# 1. For functions without a dunder, need something like F.mylen(x) (F turns mylen into an ast generator fn)

__version__ = "0.1"

_dummy_args = dict(lineno=0, col_offset=0, end_lineno=0, end_col_offset=0)

def _value_ast(val):
    if isinstance(val, ExprFn):
        return val

    if isinstance(val, tuple):
        elements = []
        names = dict()
        for v in val:
            a = _value_ast(v)
            elements.append(a.ast)
            names.update(a.names)
        new_ast = ast.Tuple(elts=elements, ctx=ast.Load(), **_dummy_args)
    elif isinstance(val, list):
        elements = []
        names = dict()
        for v in val:
            a = _value_ast(v)
            elements.append(a.ast)
            names.update(a.names)
        new_ast = ast.List(elts=elements, ctx=ast.Load(), **_dummy_args)
    elif isinstance(val, set):
        elements = []
        names = dict()
        for v in val:
            a = _value_ast(v)
            elements.append(a.ast)
            names.update(a.names)
        new_ast = ast.Set(elts=elements, **_dummy_args)
    elif isinstance(val, dict):
        keys = []
        values = []
        names = dict()
        for k, v in val.items():
            ka = _value_ast(k)
            va = _value_ast(v)
            keys.append(ka.ast)
            values.append(va.ast)
            names.update(ka.names)
            names.update(va.names)
        new_ast = ast.Dict(keys=keys, values=values, **_dummy_args)
    elif isinstance(val, slice):
        names = dict()
        new_ast = ast.Slice(**_dummy_args)
        if val.start is not None:
            a = _value_ast(val.start)
            names.update(a.names)
            new_ast.lower = a.ast
        if val.stop is not None:
            a = _value_ast(val.stop)
            names.update(a.names)
            new_ast.upper = a.ast
        if val.step is not None:
            a = _value_ast(val.step)
            names.update(a.names)
            new_ast.step = a.ast
    else:
        names = dict()
        new_ast = ast.Constant(val, kind=None, **_dummy_args)

    return ExprFn(new_ast, names)
        

def _index_expr(idx):
    if isinstance(idx, slice):
        names = dict()
        new_ast = ast.Slice(**_dummy_args)
        if idx.start is not None:
            a = _value_ast(idx.start)
            names.update(a.names)
            new_ast.lower = a.ast
        if idx.stop is not None:
            a = _value_ast(idx.stop)
            names.update(a.names)
            new_ast.upper = a.ast
        if idx.step is not None:
            a = _value_ast(idx.step)
            names.update(a.names)
            new_ast.step = a.ast

    elif isinstance(idx, tuple):
        elements = []
        names = dict()
        for v in idx:
            a, n = _index_expr(v)
            elements.append(a)
            names.update(n)
        # ExtSlice should be replaced with Tuple in 3.9+
        if sys.version_info >= (3, 9):
            new_ast = ast.Tuple(elts=elements, ctx=ast.Load(), **_dummy_args)
        else:
            new_ast = ast.ExtSlice(dims=elements, **_dummy_args)

    elif idx == Ellipsis and sys.version_info < (3, 9):
        new_ast = ast.Index(value=ast.Ellipsis(**_dummy_args), **_dummy_args)
        names = []

    else:
        a = _value_ast(idx)
        new_ast, names = a.ast, a.names
        if sys.version_info < (3, 9):
            new_ast = ast.Index(value=new_ast)

    return new_ast, names

def _unop(op):
    def dunder(self):
        new_ast = ast.UnaryOp(
            op=op(),
            operand=self.ast,
            **_dummy_args
        )
        return type(self)(ast=new_ast, names=self.names)
    return dunder

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
            rhs = _value_ast(other).ast
            # TODO: Names?
        if rev:
            lhs, rhs = rhs, lhs
        return cls(ast=ast.BinOp(
            left = lhs,
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
            rhs = _value_ast(other).ast
            # TODO: Names?
        return cls(ast=ast.Compare(
            left = self.ast,
            ops = [op()],
            comparators = [rhs],
            **_dummy_args
        ), names=names)
    return dunder

class ExprFn:
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

    __pos__ = _unop(ast.UAdd)
    __neg__ = _unop(ast.USub)
    ## __abs__ = ???
    __invert__ = _unop(ast.Invert)

    __lt__ = _cmpop(ast.Lt)
    __le__ = _cmpop(ast.LtE)
    __eq__ = _cmpop(ast.Eq)
    __ne__ = _cmpop(ast.NotEq)
    __gt__ = _cmpop(ast.Gt)
    __ge__ = _cmpop(ast.GtE)

    __contains__ = _cmpop(ast.In)

    def __bool__(self):
        raise ValueError("Anonymous functions cannot be used in conditionals. Did you use a chained comparison?")

    def __repr__(self):
        # ast.unparse new in 3.9...
        try:
            expr = ast.unparse(self.ast)
        except AttributeError:
            expr = ast.dump(self.ast)

        return f"<ExprFn: {expr}>"

    def __getitem__(self, idx):
        idx_ast, idx_names = _index_expr(idx)
        names = self.names.copy()
        names.update(idx_names)
        new_ast = ast.Subscript(
            value=self.ast,
            slice=idx_ast,
            ctx=ast.Load(),
            **_dummy_args
        )
        return type(self)(ast=new_ast, names=names)
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
        code = compile(expr_ast, "", "eval")
        self._fn = eval(code)

    def __call__(self, *args, **kw):
        return self.fn(*args, **kw)

def past(a):
    # indent new in 3.9
    print(ast.dump(a.ast, indent=4))

if __name__ == "__main__":
    x = ExprFn.name("x")
    i = ExprFn.name("i")
    a = x[1:i]
    past(a)
    print(a)
    print(a([1,2,3,4,5], 3))
