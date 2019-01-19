# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import tensorflow as tf
from tensorflow_probability import edward2 as ed
from tensorflow_probability.python.edward2 import generated_random_variables

from inferpy.util import tf_run_eval


rv_all = generated_random_variables.rv_all  # the list of available RandomVariables in edward2


class RandomVariable:
    """
    Class for random variables. It encapsulares the Random Variable from edward2, and additional properties.

    - It creates a variable generator. It must be a function without parameters, that creates a
      new Random Variable from edward2. It is used to define edward2 models as functions.
      Also, it is useful to define models using the intercept function.

    - The first time the var property is used, it creates a var using the variable generator.
    """

    def __init__(self, var, *args, **kwargs):
        self.var = var

    @property
    def name(self):
        """ name of the variable"""
        ed_name = self.var.distribution.name
        return ed_name[:-1]

    # If try to use attributes or functions not defined for RandomVariables, this function is executed.
    # First try to return the same attribute of function from the edward2 RandomVariable.
    # Secondly try to return the same attribute of function from the distribution object inside the edward2 RandomVariable.
    # Otherwise, raise an Exception.
    def __getattr__(self, name):
        if hasattr(self.var, name):
            return tf_run_eval(getattr(self.var, name))
        elif hasattr(self.var.distribution, name):
            return tf_run_eval(getattr(self.var.distribution, name))
        else:
            raise NotImplementedError('Property or method "{name}" not implemented in "{classname}"'.format(
                name=name,
                classname=type(self.var).__name__
            ))

    # In the following, define the operations by using the edward2 operator definition

    def __add__(self, other):
        return _operator(self.var, other, '__add__')

    def __radd__(self, other):
        return _operator(self.var, other, '__radd__')

    def __sub__(self, other):
        return _operator(self.var, other, '__sub__')

    def __rsub__(self, other):
        return _operator(self.var, other, '__rsub__')

    def __mul__(self, other):
        return _operator(self.var, other, '__mul__')

    def __rmul__(self, other):
        return _operator(self.var, other, '__rmul__')

    def __div__(self, other):
        return _operator(self.var, other, '__div__')

    def __rdiv__(self, other):
        return _operator(self.var, other, '__rdiv__')

    def __truediv__(self, other):
        return _operator(self.var, other, '__truediv__')

    def __rtruediv__(self, other):
        return _operator(self.var, other, '__rtruediv__')

    def __floordiv__(self, other):
        return _operator(self.var, other, '__floordiv__')

    def __rfloordiv__(self, other):
        return _operator(self.var, other, '__rfloordiv__')

    def __mod__(self, other):
        return _operator(self.var, other, '__mod__')

    def __rmod__(self, other):
        return _operator(self.var, other, '__rmod__')

    def __lt__(self, other):
        return _operator(self.var, other, '__lt__')

    def __le__(self, other):
        return _operator(self.var, other, '__le__')

    def __gt__(self, other):
        return _operator(self.var, other, '__gt__')

    def __ge__(self, other):
        return _operator(self.var, other, '__ge__')

    def __and__(self, other):
        return _operator(self.var, other, '__and__')

    def __rand__(self, other):
        return _operator(self.var, other, '__rand__')

    def __or__(self, other):
        return _operator(self.var, other, '__or__')

    def __ror__(self, other):
        return _operator(self.var, other, '__ror__')

    def __xor__(self, other):
        return _operator(self.var, other, '__xor__')

    def __rxor__(self, other):
        return _operator(self.var, other, '__rxor__')

    def __getitem__(self, *args):
        return self.var.__getitem__(*args)

    def __pow__(self, other):
        return _operator(self.var, other, '__pow__')

    def __rpow__(self, other):
        return _operator(self.var, other, '__rpow__')

    def __invert__(self):
        return self.var.__invert__()

    def __neg__(self):
        return self.var.__neg__()

    def __abs__(self):
        return self.var.__abs__()

    def __matmul__(self, other):
        return _operator(self.var, other, '__matmul__')

    def __rmatmul__(self, other):
        return _operator(self.var, other, '__rmatmul__')

    def __iter__(self):
        return self.var.__iter__()

    def __bool__(self):
        return self.var.__bool__()

    def __nonzero__(self):
        return self.var.__nonzero__()


# Each arg which is a RandomVariable is transformed into its edward2 RandomVariable instead
def _sanitize_args(list_args):
    """
    Recursively sanitize the list of arguments, as each element can be a list which needs to be sanitized too.
    Using a for loop, the code is the following.
    Nested lists are put into a tf.stack to be used as a single tensor.
    clean_args = []
    for arg in list_args:
        if isinstance(arg, list):
            tf.stack(clean_args.append(_sanitize_args(arg)))
        elif isinstance(arg, RandomVariable):
            clean_args.apend(arg.var)
        else:
            clean_args.apend(arg)
    return clean_args
    """
    # For efficiency, we use a compregension list.
    return [
                tf.stack(_sanitize_args(arg)) if isinstance(arg, list) else (
                    arg.var if isinstance(arg, RandomVariable) else
                    arg
                )
                for arg in list_args
            ]


# Each kwarg which is a RandomVariable is transformed into its edward2 RandomVariable instead
def _sanitize_kwargs(dict_kwargs):
    # Similarly than in _sanitize_args, we use a comprehension list for efficiency. This three-case-based
    # if-else is used to recursively sanitize internal lists
    return {
                k: (
                    tf.stack(_sanitize_args(v)) if isinstance(v, list) else (
                        v.var if isinstance(v, RandomVariable) else
                        v
                    )
                ) for k, v in dict_kwargs.items()
            }


def _make_random_variable(distribution_cls):
    """Factory function to make random variable given distribution class."""
    docs = RandomVariable.__doc__ + '\n Random Variable information:\n' + ('-' * 30) + '\n' + distribution_cls.__doc__
    name = distribution_cls.__name__

    def func(*args, **kwargs):
        # The arguments of RandomVariable can be tensors or edward2 Random Variables.
        # If arguments are Random Variables from inferpy, use its edward2 Random Variable instead.
        rv = RandomVariable(var=distribution_cls(*_sanitize_args(args), **_sanitize_kwargs(kwargs)))
        # Doc for help menu
        rv.__doc__ += docs
        rv.__name__ = name
        return rv
    # Doc for help menu
    func.__doc__ = docs
    func.__name__ = name
    return func


def _operator(var, other, operator_name):
    """
    Function to apply the operation called `operator_name` by using a RandomVariable
    object and other object (which can be a RandomVariable or not).
    """
    # get the operator_name function from the edward2 variable `var`
    # and call that function using the edward2 object if other is a RandomVariable,
    # otherwise just use `other` as argument
    return getattr(var, operator_name)(other.var if isinstance(other, RandomVariable) else other)


# Define all Random Variables existing in edward2
for rv in rv_all:
    globals()[rv] = _make_random_variable(getattr(ed, rv))
