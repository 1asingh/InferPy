Requirements
================


System
-----------------

Currently, InferPy requires Python 2.7 to 3.6. For checking your default Python version, type:


.. code:: bash

    $ python --version

Travis tests are performed on versions 2.7, 3.5 and 3.6. Go to `https://www.python.org/ <https://www.python.org/>`_
for specific instructions for installing the Python interpreter in your system.


InferPy runs in any OS with the Python interpreter installed. In particular, tests have been carried out
for the systems listed bellow.

- Linux CentOS 7
- Linux Elementary 0.4
- Linux Mint 19
- Linux Ubuntu 14.04 16.04 18.04
- MacOS High Sierra (10.13) and Mojave (10.14)
- Windows 10 Enterprise


Package Dependencies
-------------------------

Edward
~~~~~~~~~~~~~~~

InferPy requires exactly the version 1.3.5 of `Edward <http://edwardlib.org>`_. You may check the installed
package version as follows.


.. code:: bash

    $ pip freeze | grep edward

Tensorflow
~~~~~~~~~~~~~~~

`Tensorflow <http://www.tensorflow.org/>`_: from version 1.5 up to 1.7 (both included). To check the installed tensorflow version, type:

.. code:: bash

    $ pip freeze | grep tensorflow

Numpy
~~~~~~~~~~~~~~~

`Numpy <http://www.numpy.org/>`_ 1.14 or higher is required. To check the version of this package, type:


.. code:: bash

    $ pip freeze | grep numpy


Pandas
~~~~~~~~~~~~~~~

`Pandas <https://pandas.pydata.org>`_ 0.15.0 or higher is required. The installed version of this package can be checked as follows:


.. code:: bash

    $ pip freeze | grep pandas