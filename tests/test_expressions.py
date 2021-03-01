import ast
from fnexpr import FnExpr
import pytest

EXPRESSIONS = [expr.strip() for expr in """\
    a+3
    (a/2)+7
    a < 9
    (~a) & (a|4)
    a.foo
    a[12]
    a.foo + a.bar
    a[1:2]
    a[...,12:9]
    [1, 2, a] + a
""".splitlines() if not expr.startswith("#")]

@pytest.mark.parametrize("expr", EXPRESSIONS)
def test_ast(expr):
    from fnexpr.vars import a
    ast_expr = eval(expr, {"a": a})
    lambda_expr = eval("lambda a: " + expr, {})
    assert ast_expr.fn.__code__ == lambda_expr.__code__

def test_fn():
    from fnexpr import fn
    from fnexpr.vars import x
    ast_expr = fn("len")(x + "abc")
    lambda_expr = lambda x: len(x + "abc")
    assert ast_expr("123") == lambda_expr("123")
