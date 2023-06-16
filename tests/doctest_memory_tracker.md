# RAM memory tracker

`perftester` enables you to check the full memory used the session, which includes the memory taken by all the objects minus the memory that `perftester`'s memory log takes. 

Since this is a profiling tool, the `perftester` code is not used by the application. Hence, to make using the tool easier, it's objects are available as global variables — hence you do not have to import that in every module in which you're using the tools. So, to use this functionality, it's enough to import `perftester` in any of the modules of your application; after this import, you can use its memory-tracking tools in any module of your application.

Let's see how this works. The main function to use is `MEMPOINT()`, which creates a memory point (a point of the measurement of the session memory) and adds it to `MEMLOGS`, a list-like container collecting memory points. The first memory point is when `perftester` is imported:

```python-repl
>>> import perftester
>>> MEMLOGS
[MemLog(ID='perftester import', memory=...)]
>>> MEMPOINT()
>>> len(MEMLOGS)
2
>>> MEMPOINT("The second MEMPOINT")
>>> len(MEMLOGS)
3
>>> MEMLOGS
[MemLog(ID='perftester import', memory=...), MemLog(ID='None', memory=...), MemLog(ID='The second MEMPOINT', memory=...)]

```

(The measured memory usage is not included in the doctests, as they would fail.)

As you see, we have access to a global variable `MEMLOGS`, which is a list, and a global function `MEMPOINT()`. A memory point creates a point with an ID, which by default is `None`; these memory points are added to `MEMLOGS`. When you create two points with the same ID, say "my id", the second time it will be replaced with "my id-2", and so on. Note that while you can use any object as an ID, its string representation will be used instead:

```python-repl
>>> MEMPOINT()
>>> MEMLOGS[-1].ID
'None-2'

```

In addition to IDs, memory points contain their essence: the memory used by the current session, in bytes. Let's see what happens when we add a big list to the scope and then remove it:

```python-repl
>>> li = [i for i in range(10_000_000)]
>>> MEMPOINT("After adding a list with 10 mln elements")
>>> del li
>>> MEMPOINT("After removing this list")
>>> MEMLOGS[-2].memory / MEMLOGS[-1].memory > 100
True

```

This basically means that adding so big a list to the scope makes the session use over a hundred times more memory.

`MEMLOGS` is actually not a list but an object of a custom `MemLogsList` class:

```python-repl
>>> type(MEMLOGS)
<class 'perftester.perftester.MemLogsList'>

```

This class inherits from `collections.UserList`, but it works in quite a different way than a regular list. First of all, it's a singleton class, so `MEMLOGS` is its only instance. The only method to update it is to use the `MEMPOINT()` function. You cannot append anything to it, and item assignment does not work for it, either; neither do multiplication and adding.

Note that `MEMLOGS` elements are instances of the `MemLog` named tuple (`collections.namedtuple`). So, you can access its two items as if it were a regular tuple, or using their names, `ID` and `memory`:

```python-repl
>>> MEMPOINT("Just checking")
>>> m = MEMLOGS[-1]
>>> type(m)
<class 'perftester.perftester.MemLog'>
>>> m.ID
'Just checking'
>>> type(m.memory)
<class 'int'>

```

You can print `MEMLOGS` yourself, you can use the `perftester.pp()` function:

```python-repl
>>> perftester.pp(MEMLOGS)
[MemLog(ID='perftester import', memory=...),
 MemLog(ID='None', memory=...),
 MemLog(ID='The second MEMPOINT', memory=...),
 MemLog(ID='None-2', memory=...),
 MemLog(ID='After adding a list with 10 mln elements', memory=...),
 MemLog(ID='After removing this list', memory=...),
 MemLog(ID='Just checking', memory=...)]

```

or you can use a dedicated function `MEMPRINT()`, which converts memories to MB:

```python-repl
>>> MEMPRINT()
 0   ...    → perftester import
 1   ...    → None
 2   ...    → The second MEMPOINT
 3   ...    → None-2
 4   ...    → After adding a list with 10 mln elements
 5   ...    → After removing this list
 6   ...    → Just checking

```

## Using the `MEMTRACE` decorator

If you're interested in tracing the full-memory usage for a particular function, to see the full-memory usage of the session right before calling the function and right after it has returned, you can use the `MEMTRACE` decorator. Just like the other full-memory-tracing tools, you do not need to import it, either.

```python-repl
>>> @MEMTRACE
... def create_huge_list(n):
...     return [i for i in range(n)]
>>> li = create_huge_list(10_000_000)
>>> del li
>>> MEMPOINT()
>>> MEMLOGS[-3:]
[MemLog(ID='Before create_huge_list()', memory=...),
 MemLog(ID='After create_huge_list()', memory=...),
 MemLog(ID='None-3', memory=...)]
>>> MEMLOGS[-2].memory > 100 * MEMLOGS[-1].memory
True

```


## Additional `MEMLOGS` tools

You can use several additional methods and properties for the `MEMLOGS` object:

* `.memories`, a property that returns all the memories reported until the moment
* `IDs`, like above but for IDs
* `.filter()`, a method for filtering `MEMLOGS`

Let's see how this works:

```python-repl
>>> type(MEMLOGS.memories), len(MEMLOGS.memories)
(<class 'list'>, 10)
>>> MEMLOGS.IDs
['perftester import',
 'None',
 'The second MEMPOINT',
 'None-2',
 'After adding a list with 10 mln elements',
 'After removing this list',
 'Just checking',
 'Before create_huge_list()',
 'After create_huge_list()', 'None-3']

```

The `.filter()` methods accepts one required argument, that is, a predicate to be used for filtering, just like you'd use with the built-in `filter()` function. For the `.filter()` method, however, you need to create a predicate working with `MemLog` elements. Unlike the built-in `filter()` function, it does not create a generator but a list. This is because `MEMLOGS` is not expected to be a large object.

```python-repl
>>> def memory_over(memlog: perftester.MemLog) -> bool:
...     return memlog.memory > 3_750_000
>>> MEMLOGS.filter(memory_over)
[MemLog(ID='After adding a list with 10 mln elements', memory=...),
 MemLog(ID='After create_huge_list()', memory=...)]

```

We can of course use a `lambda` function instead:

```python-repl
>>> MEMLOGS.filter(lambda m: m.memory > 3_750_000)
[MemLog(ID='After adding a list with 10 mln elements', memory=...),
 MemLog(ID='After create_huge_list()', memory=...)]
>>> MEMLOGS.filter(lambda m: m.memory < 1_000_000)
[]
>>> MEMLOGS.filter(lambda m: "after" in m.ID or "before" in m.ID)

```

And here's the `.map()` method in action. Like the `.filter()` method, it returns a list:

```python-repl
>>> as_MB = MEMLOGS.map(lambda m: m.memory / 1024 / 1024)
>>> all(m < 500 for m in as_MB)
True

```
