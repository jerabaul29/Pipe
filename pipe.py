#!/usr/bin/env python
""" Infix programming toolkit

Module enabling a sh like infix syntax (using pipes).

= Introduction =
As an exemple, here is the solution for the 2nd Euler Project exercise :

"Find the sum of all the even-valued terms in Fibonacci
 which do not exceed four million."

Given fib a generator of fibonacci numbers :

euler2 = fib() | where(lambda x: x % 2 == 0)
               | take_while(lambda x: x < 4000000)
               | add


= Vocabulary =
 * a Pipe: a Pipe is a 'pipeable' function, somthing that you can pipe to,
           In the code '[1, 2, 3] | add' add is a Pipe
 * a Pipe function: A standard function returning a Pipe so it can be used like
           a normal Pipe but called like in : [1, 2, 3] | concat("#")


= Syntax =
The basic symtax is to use a Pipe like in a shell :
>>> [1, 2, 3] | add
6

A Pipe can be a function call, for exemple the Pipe function 'where' :
>>> [1, 2, 3] | where(lambda x: x % 2 == 0) #doctest: +ELLIPSIS
<generator object <genexpr> at ...>

A Pipe as a function is nothing more than a function returning
a specialized Pipe.


= Constructing your own =
You can construct your pipes using Pipe classe initialized with lambdas like :

stdout = Pipe(lambda x: sys.stdout.write(str(x)))
select = Pipe(lambda iterable, pred: (pred(x) for x in iterable))

Or using decorators :
@Pipe
def stdout(x):
    sys.stdout.write(str(x))

= Existing Pipes in this module =

stdout
    Outputs anything to the standard output
    >>> "42" | stdout
    42

lineout
    Outputs anything to the standard output followed by a line break
    >>> 42 | lineout
    42

as_list
    Outputs an iterable as a list
    >>> (0, 1, 2) | as_list
    [0, 1, 2]

as_tuple
    Outputs an iterable as a tuple
    >>> [1, 2, 3] | as_tuple
    (1, 2, 3)

as_dict
    Outputs an iterable of tuples as a dictionary
    [('a', 1), ('b', 2), ('c', 3)] | as_dict
    {'a': 1, 'b': 2, 'c': 3}

concat()
    Aggregates strings using given separator, or ", " by default
    >>> [1, 2, 3, 4] | concat
    '1, 2, 3, 4'
    >>> [1, 2, 3, 4] | concat("#")
    '1#2#3#4'

average
    Returns the average of the given iterable
    >>> [1, 2, 3, 4, 5, 6] | average
    3.5

netcat
    Open a socket on the given host and port, and send data to it,
    Yields host reponse as it come.
    netcat apply traverse to its input so it can take a string or
    any iterable.

    "GET / HTTP/1.0\r\nHost: google.fr\r\n\r\n" \
        | netcat('google.fr', 80)               \
        | concat                                \
        | stdout

netwrite
    Like netcat but don't read the socket after sending data

count
    Returns the length of the given iterable, counting elements one by one
    >>> [1, 2, 3, 4, 5, 6] | count
    6

add
    Returns the sum of all elements in the preceding iterable
    >>> (1, 2, 3, 4, 5, 6) | add
    21

first
    Returns the first element of the given iterable
    >>> (1, 2, 3, 4, 5, 6) | first
    1

chain
    Unfold preceding Iterable of Iterables
    >>> [[1, 2], [3, 4], [5]] | chain | concat
    '1, 2, 3, 4, 5'

    Warning : chain only unfold iterable containing ONLY iterables :
      [1, 2, [3]] | chain
          Gives a TypeError: chain argument #1 must support iteration
          Consider using traverse

traverse
    Recursively unfold iterables
    >>> [[1, 2], [[[3], [[4]]], [5]]] | traverse | concat
    '1, 2, 3, 4, 5'
    >>> squares = (i * i for i in range(3))
    >>> [[0, 1, 2], squares] | traverse | as_list
    [0, 1, 2, 0, 1, 4]

select()
    Apply a conversion expression given as parameter
    to each element of the given iterable
    >>> [1, 2, 3] | select(lambda x: x * x) | concat
    '1, 4, 9'

where()
    Only yields the matching items of the given iterable
    >>> [1, 2, 3] | where(lambda x: x % 2 == 0) | concat
    '2'

take_while()
    Like itertools.takewhile, yields elements of the
    given iterable while the predicat is true
    >>> [1, 2, 3, 4] | take_while(lambda x: x < 3) | concat
    '1, 2'

skip_while()
    Like itertools.dropwhile, skips elements of the given iterable
    while the predicat is true, then yields others
    >>> [1, 2, 3, 4] | skip_while(lambda x: x < 3) | concat
    '3, 4'

chain_with()
    Like itertools.chain, yields elements of the given iterable,
    then yields elements of its parameters
    >>> (1, 2, 3) | chain_with([4, 5], [6]) | concat
    '1, 2, 3, 4, 5, 6'

take()
    Yields the given quantity of elemenets from the given iterable, like head
    in shell script.
    >>> (1, 2, 3, 4, 5) | take(2) | concat
    '1, 2'

skip()
    Skips the given quantity of elements from the given iterable, then yields
    >>> (1, 2, 3, 4, 5) | skip(2) | concat
    '3, 4, 5'

islice()
    Just the itertools.islice
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) | islice(2, 8, 2) | concat
    '3, 5, 7'

izip()
    Just the itertools.izip
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | izip([9, 8, 7, 6, 5, 4, 3, 2, 1]) \
            | concat
    '(1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (9, 1)'

aggregate()
    Works as python reduce
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) | aggregate(lambda x, y: x * y)
    362880

    Simulate concat :
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | aggregate(lambda x, y: str(x) + ', ' + str(y))
    '1, 2, 3, 4, 5, 6, 7, 8, 9'

any()
    Returns True if any element of the given iterable satisfies the predicate
    >>> (1, 3, 5, 6, 7) | any(lambda x: x >= 7)
    True

    >>> (1, 3, 5, 6, 7) | any(lambda x: x > 7)
    False

all()
    Returns True if all elements of the given iterable
    satisfies the given predicate
    >>> (1, 3, 5, 6, 7) | all(lambda x: x < 7)
    False

    >>> (1, 3, 5, 6, 7) | all(lambda x: x <= 7)
    True

max()
    Returns the biggest element, using the given key function if
    provided (or else the identity)

    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | max(key=len)
    'qwerty'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | max()
    'zoog'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | max
    'zoog'

min()
    Returns the smallest element, using the key function if provided
    (or else the identity)

    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | min(key=len)
    'b'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | min
    'aa'

groupby()
    Like itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)
    (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | groupby(lambda x: x % 2 and "Even" or "Odd")
            | select(lambda x: "%s : %s" % (x[0], (x[1] | concat(', '))))
            | concat(' / ')
    'Even : 1, 3, 5, 7, 9 / Odd : 2, 4, 6, 8'

sort()
    Like Python's built-in "sorted" primitive. Allows cmp (Python 2.x
    only), key, and reverse arguments. By default sorts using the
    identity function as the key.

    >>> "python" | sort | concat("")
    'hnopty'
    >>> [5, -4, 3, -2, 1] | sort(key=abs) | concat
    '1, -2, 3, -4, 5'

reverse
    Like Python's built-in "reversed" primitive.
    >>> [1, 2, 3] | reverse | concat
    '3, 2, 1'

permutations()
    Returns all possible permutations
    >>> 'ABC' | permutations(2) | concat(' ')
    "('A', 'B') ('A', 'C') ('B', 'A') ('B', 'C') ('C', 'A') ('C', 'B')"

    >>> range(3) | permutations | concat('-')
    '(0, 1, 2)-(0, 2, 1)-(1, 0, 2)-(1, 2, 0)-(2, 0, 1)-(2, 1, 0)'

Euler project samples :

    # Find the sum of all the multiples of 3 or 5 below 1000.
    euler1 = (itertools.count() | select(lambda x: x * 3) | take_while(lambda x: x < 1000) | add) \
           + (itertools.count() | select(lambda x: x * 5) | take_while(lambda x: x < 1000) | add) \
           - (itertools.count() | select(lambda x: x * 15) | take_while(lambda x: x < 1000) | add)
    assert euler1 == 233168

    # Find the sum of all the even-valued terms in Fibonacci which do not exceed four million.
    euler2 = fib() | where(lambda x: x % 2 == 0) | take_while(lambda x: x < 4000000) | add
    assert euler2 == 4613732

    # Find the difference between the sum of the squares of the first one hundred natural numbers and the square of the sum.
    square = lambda x: x * x
    euler6 = square(itertools.count(1) | take(100) | add) - (itertools.count(1) | take(100) | select(square) | add)
    assert euler6 == 25164150


"""
from contextlib import closing
import socket
import itertools
from functools import reduce
import sys

try:
    import builtins
except ImportError:
    import __builtin__ as builtins


__author__ = 'Julien Palard <julien@eeple.fr>'
__credits__ = """Jerome Schneider, for its Python skillz,
and dalexander for contributing"""
__date__ = '10 Nov 2010'
__version__ = '1.3'

class Pipe:
    """
    Represent a Pipeable Element :
    Described as :
    first = Pipe(lambda iterable: next(iter(iterable)))
    and used as :
    print [1, 2, 3] | first
    printing 1

    Or represent a Pipeable Function :
    It's a function returning a Pipe
    Described as :
    select = Pipe(lambda iterable, pred: (pred(x) for x in iterable))
    and used as :
    print [1, 2, 3] | select(lambda x: x * 2)
    # 2, 4, 6
    """
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return self.function(other)

    def __call__(self, *args, **kwargs):
        return Pipe(lambda x: self.function(x, *args, **kwargs))

@Pipe
def take(iterable, qte):
    "Yield qte of elements in the given iterable."
    for item in iterable:
        if qte > 0:
            qte -= 1
            yield item
        else:
            return

@Pipe
def skip(iterable, qte):
    "Skip qte elements in the given iterable, then yield others."
    for item in iterable:
        if qte == 0:
            yield item
        else:
            qte -= 1

@Pipe
def all(iterable, pred):
    "Returns True if ALL elements in the given iterable are true for the given pred function"
    for x in iterable:
        if not pred(x):
            return False
    return True

@Pipe
def any(iterable, pred):
    "Returns True if ANY element in the given iterable is True for the given pred function"
    for x in iterable:
        if pred(x):
            return True
    return False

@Pipe
def average(iterable):
    """
    Build the average for the given iterable, starting with 0.0 as seed
    Will try a division by 0 if the iterable is empty...
    """
    total = 0.0
    qte = 0
    for x in iterable:
        total += x
        qte += 1
    return total / qte

@Pipe
def count(iterable):
    "Count the size of the given iterable, walking thrue it."
    count = 0
    for x in iterable:
        count += 1
    return count

@Pipe
def max(iterable, **kwargs):
    return builtins.max(iterable, **kwargs)

@Pipe
def min(iterable, **kwargs):
    return builtins.min(iterable, **kwargs)

@Pipe
def as_dict(iterable):
    return dict(iterable)

@Pipe
def permutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = list(range(n))
    cycles = list(range(n, n-r, -1))
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return

@Pipe
def netcat(to_send, host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((host, port))
        for data in to_send | traverse:
            s.send(data)
        while 1:
            data = s.recv(4096)
            if not data: break
            yield data

@Pipe
def netwrite(iterable, host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((host, port))
        for data in to_send | traverse:
            s.send(data)

@Pipe
def traverse(args):
    for arg in args:
        try:
            if isinstance(arg, str):
                yield arg
            else:
                for i in arg | traverse:
                    yield i
        except TypeError:
            # not iterable --- output leaf
            yield arg

@Pipe
def concat(iterable, separator=", "):
    return separator.join(map(str,iterable))

@Pipe
def as_list(iterable):
    return list(iterable)

@Pipe
def as_tuple(iterable):
    return tuple(iterable)

@Pipe
def stdout(x):
    sys.stdout.write(str(x))

@Pipe
def lineout(x):
    sys.stdout.write(str(x) + "\n")

@Pipe
def add(x):
    return sum(x)

@Pipe
def first(iterable):
    return next(iter(iterable))

@Pipe
def chain(iterable):
    return itertools.chain(*iterable)

@Pipe
def select(iterable, selector):
    return (selector(x) for x in iterable)

@Pipe
def where(iterable, predicate):
    return (x for x in iterable if (predicate(x)))

@Pipe
def take_while(iterable, predicate):
    return itertools.takewhile(predicate, iterable)

@Pipe
def skip_while(iterable, predicate):
    return itertools.dropwhile(predicate, iterable)

@Pipe
def aggregate(iterable, function):
    return reduce(function, iterable)

@Pipe
def groupby(iterable, keyfunc):
    return itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)

@Pipe
def sort(iterable, **kwargs):
    return sorted(iterable, **kwargs)

@Pipe
def reverse(iterable):
    return reversed(iterable)

chain_with = Pipe(itertools.chain)
islice = Pipe(itertools.islice)

# Python 2 & 3 compatibility
if "izip" in dir(itertools):
    izip = Pipe(itertools.izip)
else:
    izip = Pipe(zip)

if __name__ == "__main__":
    import doctest
    doctest.testmod()