import ast
from exprfn import ExprFn
import pytest

EXPRESSIONS = """\
    a+3
    (a/2)+7
    a < 9
    (~a) & (a|4)
    a.foo
    a[12]
    a.foo + a.bar
    a[1:2]
    a[...,12:9]
""".splitlines()

@pytest.mark.parametrize("expr", EXPRESSIONS)
def test_ast(expr):
    from exprfn.vars import a
    ast_expr = eval(expr, {"a": a})
    lambda_expr = eval("lambda a: " + expr, {})
    assert ast_expr.fn.__code__ == lambda_expr.__code__
