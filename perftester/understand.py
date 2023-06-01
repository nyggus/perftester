import ast
import copy
import inspect
import json
import pathlib
import pickle
import rounder

import easycheck

from collections import namedtuple
from copy import deepcopy
from functools import wraps
from memory_profiler import memory_usage
from time import perf_counter
from typing import Callable, Iterable, Union


# Globals, used as dict fields in calls

CALLEDFROM = "called from"
CALLMODE = "calls"
INSTANCEMODE = "instances"
CALLS = "no of calls"
INSTANCES = "no of instances"
MEM = "memory peak"
TIME = "execution time"
TIME_ALL = "time spent inside (all)"
TIME_MEAN = "time spent inside (mean)"


# Exceptions

class IncorrectDictRepresentationError(Exception):
    pass


# Performance decorators

def time_performance(func: Callable) -> Callable:
    """Time performance decorator.
    
    It is used to analyze the performance of the decorated function in terms
    of execution time.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        _type, function = _get_type_and_name(func)
        if _type == "class method":
            aargs = list(args)
            aargs[0] = "self"
            aargs = tuple(aargs)
            arguments = _stringify_args_kwargs(aargs, kwargs)
        else:
            arguments = _stringify_args_kwargs(args, kwargs)
        
        global calls
        
        call_type = INSTANCEMODE if _type == "class" else CALLMODE
        call_count = INSTANCES if _type == "class" else CALLS
        
        if not calls.registered[_type].get(function, False):
            calls.registered[_type][function] = {}
            calls.registered[_type][function][call_type] = {}

        calls.registered[_type][function][call_count] = (
            calls.registered[_type][function].get(call_count, 0) + 1
        )
        
        start = perf_counter()
        ret = func(*args, **kwargs)
        end = perf_counter()

        ID = calls.registered[_type][function][call_count]
        calls.registered[_type][function][call_type][ID] = {
            CALLEDFROM: inspect.stack()[1][3],
        }
        calls.registered[_type][function][call_type][ID][TIME] = (
            rounder.signif_object(end - start, 5)
        )
        calls.registered[_type][function][call_type][ID]["call"] = f"{function}({arguments})"
        calls.registered[_type][function][TIME_ALL] = (
            calls
                .registered[_type][function]
                .get(TIME_ALL, 0)
            + (end - start)
        )
        calls.registered[_type][function][TIME_MEAN] = (
            calls.registered[_type][function][TIME_ALL] /
            (
                calls.registered[_type][function].get(CALLS, None)
                or calls.registered[_type][function][INSTANCES]
            )
        )
        return ret

    return inner


def memory_performance(func: Callable) -> Callable:
    """Memory performance decorator.
    
    It is used to analyze the performance of the decorated function in terms
    of memory usage.
    """

    def inner(*args, **kwargs):
        _type, function = _get_type_and_name(func)
        if _type == "class method":
            aargs = list(args)
            aargs[0] = "self"
            aargs = tuple(aargs)
            arguments = _stringify_args_kwargs(aargs, kwargs)
        else:
            arguments = _stringify_args_kwargs(args, kwargs)
        
        global calls
        
        call_type = INSTANCEMODE if _type == "class" else CALLMODE
        call_count = INSTANCES if _type == "class" else CALLS
        
        if not calls.registered[_type].get(function, False):
            calls.registered[_type][function] = {}
            calls.registered[_type][function][call_type] = {}

        calls.registered[_type][function][call_count] = (
            calls.registered[_type][function].get(call_count, 0) + 1
        )
        memory_results, ret = memory_usage((func, args, kwargs), retval=True)
        peak_memory = min(memory_results)
        
        ID = calls.registered[_type][function][call_count]
        calls.registered[_type][function][call_type][ID] = {
            CALLEDFROM: inspect.stack()[1][3],
        }
        calls.registered[_type][function][call_type][ID][MEM] = (
            peak_memory
        )
        calls.registered[_type][function][call_type][ID]["call"] = f"{function}({arguments})"
        calls.registered[_type][function][MEM] = max(
            # current max
            calls
                .registered[_type][function]
                .get(MEM, 0),
            # current memory_peak
            peak_memory
        )
        return ret

    return inner


# Class containing all the registered calls and class instances.

class Calls:
    __slots__ = ("registered", "analyze", "save", "read")
    
    def __init__(self):
        self.registered: dict = {"class": {}, "class method": {}, "function": {}}
    
    def show(self, digits=4, indent=4):
        rounded_calls = rounder.signif_object(self.registered,
                                              use_copy=True,
                                              digits=digits)
        print("Classes:\n", json.dumps(rounded_calls["class"], indent=indent))
        print("Class methods:\n", json.dumps(rounded_calls["class method"], indent=indent))
        print("Functions:\n", json.dumps(rounded_calls["function"], indent=indent))

    def __repr__(self):
        if not self.registered.keys():
            return "No registered calls"
        
        instances = self._get_count("class")
        method_calls = self._get_count("class method")
        func_calls = self._get_count("function")
        
        return (
            "Registered:\n"
            f"  * {instances} class instances\n"
            f"  * {method_calls} class methods\n"
            f"  * {func_calls} function calls\n"
        )
    
    def _get_count(self, which):
        calls = 0
        if self.registered[which]:
            for k in self.registered[which]:
                key = INSTANCES if which == "class" else CALLS
                calls += self.registered[which][k][key]
        return calls


class CallsAnalyzer:
    """Class to analyze Calls.registered.
    
    This is a simple analyzer. A more adanced one will be offered
    in a dedicated understand extension.
    """
    def _update_calls(self):
        global calls
        self.calls = calls.registered

    def summarize(self, digits=4) -> dict:
        self._update_calls()
        summary_calls = copy.deepcopy(self.calls)
        for key in ("class method", "function"):
            if summary_calls[key]:
                for k in summary_calls[key]:
                    _ = summary_calls[key][k].pop(CALLMODE)
        if summary_calls["class"]:
            for k in summary_calls["class"]:
                _ = summary_calls["class"][k].pop(INSTANCEMODE)
            
        summary_calls = rounder.signif_object(summary_calls, digits=digits)
        return summary_calls

    summarise = summarize
    

class CallsSaver:
    def _update(self):
        global calls
        self.calls = calls.registered

    def to_json(self, path: Union[str, pathlib.Path]):
        self._update()
        json_dict = json.dumps(self.calls)
        with open(path, "w") as json_file:
            json_file.write(json_dict)
    
    def to_text(self, path: Union[str, pathlib.Path]):
        self._update()
        with open(path, "w") as text_file:
            text_file.write(str(self.calls))

    def to_pickle(self, path: Union[str, pathlib.Path]):
        self._update()
        with open(path, "wb") as pickle_file:
            pickle.dump(self.calls, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)


class IncorrectCallsInstanceError(Exception): ...


CallsInstance = namedtuple("CallsInstance", "type registered")


class CallsReader:
    __slots__ = tuple()

    def _check_calls_object(self, obj, path):
        # check if obj is a valid Calls object
        easycheck.check_type(
            obj,
            expected_type=dict,
            handle_with=IncorrectDictRepresentationError,
            message=f"Object parsed from {path} is not a dict but"
                    f" a {type(obj).__name__}"
        )
        # check if the required keys are there
        return self._get_type_of_calls(obj)

    @staticmethod
    def _get_type_of_calls(obj):
        # check if this is a time or memory calls dict
        # if time: return "time"
        # if memory: return "memory"
        # else: raise IncorrectCallsInstanceError
        for _type in ["class", "class method", "function"]:
            if obj[_type].keys():
                first = list(obj[_type].keys())[0]
                if TIME_ALL in obj[_type][first].keys():
                    return "time"
                if MEM in obj[_type][first].keys():
                    return "memory"
        raise IncorrectCallsInstanceError(
            "The object is neither Time nor Memory Calls dictionary."
            )

    def from_json(self, path: Union[str, pathlib.Path]):
        with open(path) as jsonfile:
            registered = json.load(jsonfile)
        
        # use int IDs (used as keys) instead of str,
        # which is used by json.load
        for _type in ["class", "class method", "function"]:
            calls = "instances" if _type == "class" else "calls"
            for method in registered[_type]:
                registered[_type][method][calls] = {
                    int(instance): value
                    for instance, value in registered[_type][method][calls].items()
                }
        return CallsInstance(
            type=self._check_calls_object(registered, path),
            registered=registered
        )

    def from_text(self, path: Union[str, pathlib.Path]):
        with open(path) as f:
            try:
                obj_from_text = ast.literal_eval(f.read())
            except Exception as e:
                raise IncorrectDictRepresentationError from e
        self._check_calls_object(obj_from_text, path)
        return CallsInstance(
            type=self._check_calls_object(obj_from_text, path),
            registered=obj_from_text
        )

    def from_pickle(self, path: Union[str, pathlib.Path]):
        with open(path, "rb") as pickle_file:
            pkl = pickle.load(pickle_file)
        return CallsInstance(
            type=self._check_calls_object(pkl, path),
            registered=pkl
        )


# Helpers

def _is_class(obj):
    return repr(obj).startswith("<class")


def _is_this_function_a_method(func):
    return "." in func.__qualname__


def _get_type_and_name(obj):
    if _is_class(obj):
        return "class", f"{obj.__module__}.{obj.__name__}"
    if hasattr(obj, "__wrapped__"):
        name = obj.__wrapped__.__name__
    if _is_this_function_a_method(obj):
        name = obj.__qualname__
        return "class method", f"{obj.__module__}.{name}"
    return "function", f"{obj.__module__}.{obj.__name__}"


def type_and_len_of_iterable(it, max_len=1000):
    """Get length of an iterable.
    
    The iterable is copied first, and the function works
    on the deep copy. For generators expressions, the function
    returns "generator" as cannot get its length without emptying
    the original generator.
    
    If maximum_len is reached, instead of the actual length, the function
    returns "over {max_len}", to make the function cheap.
    """
    # Get length, based on copy
    it_copy = deepcopy(it)
    
    c = 0
    max_len_reached = False
    for i in it_copy:
        c += 1
        if i == max_len:
            max_len_reached = True
            break

    if max_len_reached:
        return f"{type(it).__name__} of over {max_len} items"
    if not c:
        return f"empty {type(it).__name__}"
    return f"{type(it).__name__} of {c} item{'s' if c > 1 else ''}"


def _add_quotes_to_str(obj):
    """Add quotes to strings.

    The function works recursively, so that it goes deep into the structure
    to reach any string. If obj is "self", the quotes are not added, so that
    in case of class methods self is printed without quotes.

    Warning: Note that in a dictionary, it will add quotes only to values,
    not to keys.

    >>> _add_quotes_to_str(222)
    222
    >>> _add_quotes_to_str("222")
    "'222'"
    >>> _add_quotes_to_str(("222", ))
    'tuple of 1 item'
    >>> _add_quotes_to_str(("222", 50, "String", 'Also string'))
    'tuple of 4 items'
    >>> _add_quotes_to_str(("222", 50, ["String", 'Also string']))
    'tuple of 3 items'
    >>> _add_quotes_to_str((["'whatever'", "'and whatever'"], 20))
    'tuple of 2 items'
    >>> _add_quotes_to_str({"a": "whatever", "b":"Something"})
    {'a': "'whatever'", 'b': "'Something'"}
    """
    if obj == "self":
        return f"self"
    if not obj:
        return obj

    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = _add_quotes_to_str(v)
        return obj
    if isinstance(obj, str):
        return f"'{obj}'"
    if isinstance(obj, range):
        n = len(obj)
        return f"range of {n} item{'s' if n > 1 else ''}"
    if isinstance(obj, Iterable):
        # For generator expression, we need to use itertools.tee,
        # but this cannot be done behind the scenes, as the original
        # object is empty and cannot be thus used.
        try:
            return type_and_len_of_iterable(obj)
        except TypeError:
            # cannot pickle the generator type,
            # hence we do not get its length
            return "generator"

    return obj


def _stringify_args_kwargs(args, kwargs, digits=4):
    """Make a string out of args and kwargs.

    The final string is formatted in a way that can be used in a print
    of a call to a function. So, for instance, white spaces are added after
    each argument; quotes are added to strings, etc.

    >>> _stringify_args_kwargs(("something", 20), {})
    "'something', 20"
    >>> _stringify_args_kwargs(tuple(), {"x": 300})
    'x=300'
    >>> _stringify_args_kwargs(tuple(), {"x": "mixed"})
    "x='mixed'"
    >>> _stringify_args_kwargs(("something", 20), {"x": 300})
    "'something', 20, x=300"
    >>> _stringify_args_kwargs(("something", 20), {"x": "something else"})
    "'something', 20, x='something else'"
    """
    arguments = ""
    if len(args) > 0 and len(kwargs) == 0:
        if len(args) == 1:
            a = _add_quotes_to_str(rounder.signif_object(args[0], digits))
            arguments = f"{a}"
        else:
            to_join = [str(_add_quotes_to_str(rounder.signif_object(a, digits))) for a in args]
            arguments = f"{', '.join(to_join)}"
    elif len(kwargs) > 0 and len(args) == 0:
        a = ", ".join(f"{k}={str(_add_quotes_to_str(rounder.signif_object(v, digits)))}" for k, v in kwargs.items())
        arguments = f'{a}'
    elif len(kwargs) > 0 and len(args) > 0:
        if len(args) == 1:
            arguments = f"{_add_quotes_to_str(rounder.signif_object(args[0], digits))}"
        else:
            to_join = [str(_add_quotes_to_str(rounder.signif_object(a, digits))) for a in args]
            arguments = f"{', '.join(to_join)}"
        if len(kwargs) == 1:
            key = next(iter(kwargs))
            arguments += f", {key}={_add_quotes_to_str(rounder.signif_object(kwargs[key], digits))}"
        else:
            arguments += f', {", ".join(f"{k}={_add_quotes_to_str(rounder.signif_object(v, digits))}" for k, v in kwargs.items())}'
    return arguments


# The final creation of the instance of Calls

calls = Calls()
calls.analyze = CallsAnalyzer()
calls.save = CallsSaver()
calls.read = CallsReader()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
