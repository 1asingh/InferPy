import importlib
import pytest
import numpy as np
import random
import tensorflow as tf

from inferpy.contextmanager import randvar_registry
from inferpy.util import name


SEED = 607742924


@pytest.fixture(autouse=True)
def tf_reset_default_graph():
    """
    Reset the tf default graph
    """
    tf.reset_default_graph()
    yield


@pytest.fixture(autouse=True)
def reproducible():
    """
    Set tf, numpy and random seed to SEED
    """
    tf.random.set_random_seed(SEED)
    np.random.seed(SEED)
    random.seed(SEED)
    yield


@pytest.fixture(autouse=True)
def restart_default_randvar_registry():
    randvar_registry.restart_default()
    yield


@pytest.fixture(autouse=True)
def restart_random_names_counter():
    importlib.reload(name)
    yield
