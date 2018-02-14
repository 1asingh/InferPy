import inferpy.util
from inferpy.util import tf_run_wrapper

from inferpy.prob_model import ProbModel
import tensorflow as tf





class RandomVariable(object):
    """Base class for random variables.
    """

    def __init__(self, dist):
        self._dist = dist

        if ProbModel.is_active():
            print("is active")
            ProbModel.get_active_model().distlist.append(self)


    @property
    def dist(self):
        """Underlying Edward object"""
        return self._dist

    @property
    def dim(self):
        """ Dimensionality of variable """
        return self.dist.shape.as_list()[1]

    @property
    def batches(self):
        """ Number of batches of the variable"""
        return self.dist.shape.as_list()[0]

    @property
    def shape(self):
        """ shape of the variable, i.e. (batches, dim)"""
        return self.dist.shape.as_list()

    @property
    def name(self):
        """ name of the variable"""
        return self.dist.name


    @property
    def observed(self):
        return self.observed

    @observed.setter
    def observed(self,observed):
        self.__observed=observed

    @tf_run_wrapper
    def sample(self, v):
        """ Method for obaining a sample of shape v"""
        return self.dist.sample(v)

    @tf_run_wrapper
    def prob(self, v):
        return self.dist.prob(tf.cast(v, tf.float64))

    @tf_run_wrapper
    def log_prob(self, v):
        return self.dist.log_prob(tf.cast(v, tf.float64))



    def __repr__(self):
        return "<inferpy RandomVariable '%s' shape=%s dtype=%s>" % (
            self.name, self.shape, self.dist.dtype.name)



