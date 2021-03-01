# Anonymous Functions as Expressions

Python treats functions as first class objects - you can assign them to variables, pass them to *other* functions, etc. This is a very powerful feature, which enables functions like `map()`, and many of the functions in the `itertools` module.

Typically, when you pass a function to another one, you will name the function you are passing. Having a function with a meaningful name is usually clearer, and allows you to test that function independently, if it is complex. But sometimes, the function you are passing is simple enough that this feels like overkill - for example, if you are using `map` to double the elements of a list, having to define an explicitly named `double` function can obscure the point of the code. It's quite hard to find simple examples here - in this particular case, a list comprehension is probably better than `map`, for example.

For cases where a named function is too much, Python has the `lambda` keyword to create anonymous functions: `lambda x: x*2`. This works fine, and supports cases where you want to use a "throwaway" single expression as a function. But there are regular debates on the Python mailing lists looking for "improved" ways of writing anonymous functions. While some are aimed at the limitations of `lambda` (only a single expression is allowed), many objections are simply about the "look" of a lambda expression.

This library offers an alternative to `lambda` syntax, by building expressions using "placeholder" variables. Such expressions generate the exact same code as the corresponding lambda expression, so they should be equivalent to using the corresponding lambda.

As an example, the following two definitions are equivalent:

```python
# Import a placeholder variable x
from fnexpr.vars import x

lambda_fn = lambda x: x*2
anon_fn = x*2

assert anon_fn(10) == lambda_fn(10)
```

To define an anonymous function using this module, you simply use the expression that forms the body of the lambda expression, having declared (imported) the variables used to be placeholders.

## Additional Features

The vast majority of uses for this library are expected to be single-argument functions. However, it can be used in more general cases if needed.

You can use as many placeholders in an expression as you like. Each placeholder will become an argument to the function:

```python
>>> from fnexpr.vars import x,y,z
>>> ((x + y) * z)(1, 2, 3)
9
```

Arguments can be called using positional or keyword parameters:

```python
>>> from fnexpr.vars import x,y,z
>>> ((x + y) * z)(y=1, z=2, x=3)
8
```

Arguments are expected in alphabetical order of placeholder (older versions of the library used the order in which placeholders were encountered, but that makes it impossible to write an equivalent to `lambda x, y: y - x`)

```python
from fnexpr.vars import x,y
(y - x)(1, 2)
1
```

The `fnexpr.vars` module declares placeholders called a, b, ... z, A, B, ... Z, _ and _0, _1, ... _9. That should be sufficient for most purposes, but if you prefer some other name, you can define your own:

```python
>>> from fnexpr import placeholder
>>> dummy = placeholder("dummy")
>>> (dummy + 2)(10)
12
```

## Limitations

Expressions are compiled into a function using operator overloading. As a result, placeholders (and subexpressions) cannot be used in operations that have no special method for overloading. So, for example, the following constructs do not work (assuming `x` is a placeholder):

* `x and True`
* `3 if x else 9`
* `1 < x < 10` (this expands to `1 < x and x < 10` which includes a conditional)
* `x(12)` (technically, there is a `__call__` method, but we use that for actually calling the anonymous function...)

As "normal" functions don't know about placeholders, constructs like `len(x)` don't work. As a workaround, `fnexpr.fn` creates an expression that calls a function:

```python
from fnexpr import fn
from fnexpr.vars import x

anon_expr = fn("len")(x)
assert anon_expr("abc") == (lambda x: len(x))("abc")
```

## Performance

As the compiled code is the same as `lambda`, the cost of executing an expression should be the same as the equivalent lambda. However, expressions are instances of a user-defined class, and so calls go through the normal `__call__` mechanism for classes. This introduces a small overhead for each call. Also, *building* the expression is slower, as it is done at runtime, where a `lambda` expression is built at compile time.