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
    lambda_expr = ast.parse("lambda a: " + expr, mode="eval").body.body
    assert ast.dump(ast_expr.ast) == ast.dump(lambda_expr)
