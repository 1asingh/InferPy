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

"""The Normal (Gaussian) distribution class."""

import edward.models as base_models
import numpy as np
import inferpy.util

from inferpy.util import tf_run_wrapper
from inferpy.models.random_variable import *
from inferpy.replicate import *





class Normal(RandomVariable):

    """ Class implementing the Normal distribution with location `loc`, `scale` and `dim` parameters.

    The probability density of the normal distribution is,

    .. math::

      f(x|\mu,\sigma^2)=\\frac{1}{{\\sigma \\sqrt {2\\pi}}} e^{-\\frac{(x-\\mu)^2}{2 \\sigma ^2}}


    where

    - :math:`\mu`  is the mean or expectation of the distribution (i.e. `location`),
    - :math:`\sigma`  is the standard deviation (i.e. `scale`), and
    - :math:`\sigma^{2}` is the variance.



    The Normal distribution is a member of the `location-scale
    family <https://en.wikipedia.org/wiki/Location-scale_family>`_.

    This class allows the definition of a variable normal distributed of
    any dimension. Each of the dimensions are independent. For example:

    .. literalinclude:: ../../examples/normal_dist_definition.py



    """

    def __init__(self, loc, scale, dim=None, observed=True, name="inf_Normal"):

        """Construct Normal distributions

        The parameters `loc` and `scale` must be shaped in a way that supports
        broadcasting (e.g. `loc + scale` is a valid operation). If dim is specified,
        it should be consistent with the lengths of `loc` and `scale`


        Args:
            loc (float): scalar or vector indicating the mean of the distribution at each dimension.
            scale (float): scalar or vector indicating the stddev of the distribution at each dimension.
            dim (int): optional scalar indicating the number of dimensions

        Raises
            ValueError: if the parameters are not consistent
            AttributeError: if any of the properties is changed once the object is constructed

        """

        self.__check_params(loc, scale, dim)


        param_dim = 1
        if dim != None: param_dim = dim

        # shape = (batches, dimension)
        self_shape = (replicate.get_total_size(), np.max([np.size(loc), np.size(scale), param_dim]))

        loc_rep = self.__reshape_param(loc, self_shape)
        scale_rep = self.__reshape_param(scale, self_shape)

        # build the distribution

        super(Normal, self).__init__(base_models.Normal(loc=loc_rep, scale=scale_rep, name=name), observed=observed)

    # getter methods

    @property
    @tf_run_wrapper
    def loc(self):
        """Distribution parameter for the mean."""
        return self.dist.loc


    @property
    @tf_run_wrapper
    def scale(self):
        """Distribution parameter for standard deviation."""
        return self.dist.scale




    def __check_params(self, loc, scale, dim):
        """private method that checks the consistency of the input parameters"""

        # loc and scale cannot be multidimensional arrays (by now)
        if np.ndim(loc) > 1 or np.ndim(scale) > 1:
            raise ValueError("loc and scale cannot be multidimensional arrays")

        len_loc = np.size(loc)
        len_scale = np.size(scale)

        # loc and scale lengths must be equal or must be scalars
        if len_loc > 1 and len_scale > 1 and len_loc != len_scale:
            raise ValueError("loc and scale lengths must be equal or must be 1")

        # loc can be a scalar or a vector of length dim

        if dim != None and len_loc > 1 and dim != len_loc:
            raise ValueError("loc length is not consistent with value in dim")

        if dim != None and len_scale > 1 and dim != len_scale:
            raise ValueError("scale length is not consistent with value in dim")


    def __reshape_param(self,param, self_shape):

        N = self_shape[0]
        D = self_shape[1]


        # get a D*N unidimensional vector

        if np.shape(param) in [(), (1,)] or isinstance(param, RandomVariable):
            param_vect = np.repeat(param, D * N).tolist()
        else:
            param_vect = np.tile(param, N).tolist()

        # transform the numerical values into tensors

        for i in range(0, D * N):
            if np.isscalar(param_vect[i]):
                param_vect[i] = [[tf.constant(param_vect[i], dtype="float64")]]
            elif isinstance(param_vect[i], RandomVariable):
                param_vect[i] = param_vect[i].dist


        # reshape the list

        param_tf_mat = tf.reshape(tf.stack(param_vect), [N, D])

        return param_tf_mat
