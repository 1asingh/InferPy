InferPy: A Python Library for Probabilistic Modelling
=====================================================

InferPy is a high-level API for probabilistic modelling written in
Python and capable of running on top of Edward, Tensorflow and Apache
Spark. InferPy's API is strongly inspired by Keras and it has a focus on
enabling flexible data processing, simple probablistic modelling,
scalable inference and robust model validation.

| Use InferPy is you need a probabilistic programming language that: -
  Has a simple and user friendly API (inspired by Keras). - Allows for
  easy and fast prototyping of simple probabilistic models or complex
  probabilistics constructs containing deep neural networks (by relying
  on Edward).
| - Run seamlessly on CPU and GPU (by relying on Tensorflow). - Process
  seamlessly small data sets or large distributed data sets (by relying
  on Apache Spark). .

--------------

Getting Started: 30 seconds to InferPy
--------------------------------------

The core data structures of InferPy is a a **probabilistic model**,
defined as a set of **random variables** with a conditional independence
structure. Like in Edward, a **random varible** is an object
parameterized by a set of tensors.

Let's look at a simple examle. We start defining the **prior** of the
parameters of a **mixture of Gaussians** model:

.. code:: python

    import numpy as np
    import inferpy as inf
    from inferpy.models import Normal, InverseGamma, Dirichlet

    # K defines the number of components. 
    K=10
    with inf.replicate(size = K)
        #Prior for the means of the Gaussians 
        mu = Normal(loc = 0, scale = 1)
        #Prior for the precision of the Gaussians 
        sigma = InverseGamma(concentration = 1, rate = 1)
        
    #Prior for the mixing proportions
    p = Dirichlet(np.ones(K))

InferPy supports the definition of **plateau notation** by using the
construct ``with inf.replicate(size = K)``, which replicates K times the
random variables enclosed within this anotator. Every replicated
variable is assumed to be **independent**.

This ``with inf.replicate(size = N)`` construct is also usefuel when
defining the model for the data:

.. code:: python

    # Number of observations
    N = 1000
    #data Model
    with inf.replicate(size = N)
        # Sample the component indicator of the mixture. This is a latent variable that can not be observed
        z_n = Multinomial(probs = p)
        # Sample the observed value from the Gaussian of the selected component.  
        x_n = Normal(loc = inf.gather(mu,z_n), scale = inf.gather(sigma,z_n), observed = true)

As commented above, the variable z\_n and x\_n are surrounded by a
**with** statement to inidicate that the defined random variables will
be reapeatedly used in each data sample. In this case, every replicated
variable is conditionally idependent given the variables mu and sigma
defined outside the **with** statement.

Once the random variables of the model are defined, the probablitic
model itself can be created and compiled. The probabilistic model
defines a joint probability distribuiton over all these random
variables.

.. code:: python

    from inferpy import ProbModel
    probmodel = ProbModel(vars = [p,mu,sigma,z_n,x_n]) 
    probmodel.compile(infMethod = 'KLqp')

During the model compilation we specify different inference methods that
will be used to learn the model.

.. code:: python

    from inferpy import ProbModel
    probmodel = ProbModel(vars = [p,mu,sigma,z_n,x_n]) 
    probmodel.compile(infMethod = 'MCMC')

The inference method can be further configure. But, as in Keras, a core
principle is to try make things reasonbly simple, while allowing the
user the full control if needed.

.. code:: python

    from keras.optimizers import SGD
    probmodel = ProbModel(vars = [p,mu,sigma,z_n,x_n]) 
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    infklqp = inf.inference.KLqp(optimizer = sgd, loss="ELBO")
    probmodel.compile(infMethod = infklqp)

Every random variable object is equipped with methods such as
*log\_prob()* and *sample()*. Similarly, a probabilistic model is also
equipped with the same methods. Then, we can sample data from the model
anbd compute the log-likelihood of a data set:

.. code:: python

    data = probmodel.sample(size = 100)
    log_like = probmodel.log_prob(data)

Of course, you can fit your model with a given data set:

.. code:: python

    probmodel.fit(data_training, epochs=10)

Update your probablistic model with new data using the Bayes' rule:

.. code:: python

    probmodel.update(new_data)

Query the posterior over a given random varible:

.. code:: python

    mu_post = probmodel.posterior(mu)

Evaluate your model according to a given metric:

.. code:: python

    log_like = probmodel.evaluate(test_data, metrics = ['log_likelihood'])

Or compute predicitons on new data

.. code:: python

    cluster_assignments = probmodel.predict(test_data, targetvar = z_n)

--------------

Guiding Principles
------------------

-  InferPy's probability distribuions are mainly inherited from
   TensorFlow Distribuitons package. InferPy's API is fully compatible
   with tf.distributions' API. The 'shape' argument was added as a
   simplifing option when defining multidimensional distributions.
-  InferPy directly relies on top of Edward's inference engine and
   includes all the inference algorithms included in this package. As
   Edward's inference engine relies on TensorFlow computing engine,
   InferPy also relies on it too.
-  InferPy seamsly process data contained in a numpy array, Tensorflow's
   tensor, Tensorflow's Dataset (tf.Data API) or Apache Spark's
   DataFrame.
-  InferPy also includes novel distributed statistical inference
   algorithms by combining Tensorflow and Apache Spark computing
   engines.

--------------

Getting Started
---------------

Guide to Building Probabilistic Models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

InferPy focuses on *hirearchical probabilistic models* which usually are
structured in two different layers:

-  A **prior model** defining a joint distribution :math:`p(\theta)`
   over the global parameters of the model, :math:`\theta`.
-  A **data or observation model** defining a joint conditional
   distribution :math:`p(x,h|\theta)` over the observed quantities
   :math:`x` and the the local hidden variables :math:`h` governing the
   observation :math:`x`. This data model should be specified in a
   single-sample basis. There are many models of interest without local
   hidden variables, in that case we simply specify the conditional
   :math:`p(x|\theta)`. More flexible ways of defining the data model
   can be found in ?.

This is how a mixture of Gaussians models is denfined in InferPy:

.. code:: python

    import numpy as np
    import inferpy as inf
    from inferpy.models import Normal, InverseGamma, Dirichlet

    # K defines the number of components. 
    K=10
    #Prior for the means of the Gaussians 
    mu = Normal(loc = 0, scale = 1, shape=[K,d])
    #Prior for the precision of the Gaussians 
    invgamma = InverseGamma(concentration = 1, rate = 1, shape=[K,d])
    #Prior for the mixing proportions
    theta = Dirichlet(np.ones(K))

    # Number of observations
    N = 1000
    #data Model
    with inf.replicate(size = N)
        # Sample the component indicator of the mixture. This is a latent variable that can not be observed
        z_n = Multinomial(probs = theta)
        # Sample the observed value from the Gaussian of the selected component.  
        x_n = Normal(loc = tf.gather(mu,z_n), scale = tf.gather(invgamma,z_n), observed = true)

    #Probabilistic Model
    probmodel = ProbModel(prior = [p,mu,sigma,z_n,x_n]) 
    probmodel.compile()

The ``with inf.replicate(size = N)`` sintaxis is used to replicate the
random variables contained within this construct. It follows from the
so-called *plateau notation* to define the data generation part of a
probabilistic model. Every replicated variable is **conditionally
idependent** given the previous random variables (if any) defined
outside the **with** statement.

Internally, ``with inf.replicate(size = N)`` construct modifies the
random variable shape by adding an extra dimension. For the above
example, z\_n's shape is [N,1], and x\_n's shape is [N,d].

Following Edward's approach, a random variable :math:`x` is an object
parametrized by a tensor :math:`\theta` (i.e. a TensorFlow's tensor or
numpy's ndarray). The number of random variables in one object is
determined by the dimensions of its parameters (like in Edward) or by
the 'shape' or 'dim' argument (inspired by PyMC3 and Keras):

.. code:: python

    # vector of 5 univariate standard normals
    x  = Normal(loc = 0, scale = 1, dim = 5) 

    # vector of 5 univariate standard normals
    x  = Normal(loc = np.zeros(5), scale = np.ones(5)) 

    # vector of 5 univariate standard normals
    x = Normal (loc = 0, scale = 1, shape = [5,1])

The ``with inf.replicate(size = N)`` sintaxis can also be used to define
multi-dimensional objects, the following code is also equivalent to the
above ones:

.. code:: python

    # vector of 5 univariate standard normals
    with inf.replicate(size = 5)
        x = Normal (loc = 0, scale = 1)

More detailed inforamtion about the semantics of
``with inf.replicate(size = N)`` can be found in ?. Examples of using
this construct to define more expressive and complex models can be found
in ?.

Multivariate distributions can be defined similarly. Following Edward's
approach, the multivariate dimension is the innermost (right-most)
dimension of the parameters.

.. code:: python

    # 2 x 3 matrix of K-dimensional multivariate normals
    x  = MultivariateNormal(loc = np.zeros([2,3,K]), scale = np.ones([2,3,K,K]), observed = true) 

    # 2 x 3 matrix of K-dimensional multivariate normals
    y = MultivariateNormal (loc = np.zeros(K), scale = np.ones([K,K]), shape = [2,3], observed = true)

The argument **observed = true** in the constructor of a random variable
is used to indicate whether a variable is observable or not.

A **probabilistic model** defines a joint distribution over observable
and non-observable variables, :math:`p(theta,mu,sigma,z_n, x_n)` for the
running example,

.. code:: python

    from inferpy import ProbModel
    probmodel = ProbModel(vars = [theta,mu,sigma,z_n,x_n]) 
    probmodel.compile()

The model must be **compiled** before it can be used.

Like any random variable object, a probabilistic model is equipped with
methods such as *log\_prob()* and *sample()*. Then, we can sample data
from the model anbd compute the log-likelihood of a data set:

.. code:: python

    data = probmodel.sample(size = 1000)
    log_like = probmodel.log_prob(data)

Folowing Edward's approach, a random variable :math:`x` is associated to
a tensor :math:`x^*` in the computational graph handled by TensorFlow,
where the computations takes place. This tensor :math:`x^*` contains the
samples of the random variable :math:`x`, i.e.
:math:`x^*\sim p(x|\theta)`. In this way, random variables can be
involved in expressive deterministic operations. For example, the
following piece of code corresponds to a zero inflated linear regression
model

.. code:: python


    #Prior
    w = Normal(0, 1, dim=d)
    w0 = Normal(0, 1)
    p = Beta(1,1)

    #Likelihood model
    with inf.replicate(size = 1000):
        x = Normal(0,1000, dim=d, observed = true)
        h = Binomial(p)
        y0 = Normal(w0 + inf.matmul(x,w, transpose_b = true), 1),
        y1 = Delta(0.0)
        y = Deterministic(h*y0 + (1-h)*y1, observed = true)

    probmodel = ProbModel(vars = [w,w0,p,x,h,y0,y1,y]) 
    probmodel.compile()
    data = probmodel.sample(size = 1000)
    probmodel.fit(data)

A special case, it is the inclusion of deep neural networks within our
probabilistic model to capture complex non-linear dependencies between
the random variables. This is extensively treated in the the Guide to
Bayesian Deep Learning.

Finally, a probablistic model have the following methods:

-  ``probmodel.summary()``: prints a summary representation of the
   model.
-  ``probmodel.get_config()``: returns a dictionary containing the
   configuration of the model. The model can be reinstantiated from its
   config via:

.. code:: python

    config = probmodel.get_config()
    probmodel = ProbModel.from_config(config)

-  ``model.to_json()``: returns a representation of the model as a JSON
   string. Note that the representation does not include the weights,
   only the architecture. You can reinstantiate the same model (with
   reinitialized weights) from the JSON string via: \`\`\`python from
   models import model\_from\_json

json\_string = model.to\_json() model = model\_from\_json(json\_string)
\`\`\`

--------------

Guide to Approximate Inference in Probabilistic Models
------------------------------------------------------

The API defines the set of algorithms and methods used to perform
inference in a probabilistic model :math:`p(x,z,\theta)` (where
:math:`x` are the observations, :math:`z` the local hidden variibles,
and :math:`\theta` the global parameters of the model). More precisely,
the inference problem reduces to compute the posterior probability over
the latent variables given a data sample
$p(z,:raw-latex:`\theta`\|x\_{train}), because by looking at these
posteriors we can uncover the hidden structure in the data. For the
running example, :math:`p(mu|x_{train})` tells us where the centroids of
the data are, while :math:`p(z_n|x_{train})` shows us to which centroid
every data point belongs to.

InferPy inherits Edward's approach an consider approximate inference
solutions,

.. math::  q(z,\theta) \approx p(z,\theta | x_{train})

,

in which the task is to approximate the posterior
:math:`p(z,\theta | x_{train})` using a family of distributions,
:math:`q(z,\theta; \labmda)`, indexed by a parameter vector
:math:`\lambda`.

A probabilistic model in InferPy should be compiled before we can access
these posteriors,

.. code:: python

     probmodel = ProbModel(vars = [theta,mu,sigma,z_n, x_n]) 
     probmodel.compile(infMethod = 'KLqp')   
     model.fit(x_train)
     posterior_mu = probmodel.posterior(mu)

The compilation process allows to choose the inference algorithm through
the 'infMethod' argument. In the above example we use 'Klqp'. Other
inference algorithms include: 'NUTS', 'MCMC', 'KLpq', etc. Look at ? for
a detailed description of the available inference algorithms.

Following InferPy guiding principles, users can further configure the
inference algorithm.

First, they can define they family 'Q' of approximating distributions,

.. code:: python

     probmodel = ProbModel(vars = [theta,mu,sigma,z_n,x_n]) 
     
     q_z_n = inf.inference.Q.Multinomial(bind = z_n, initializer='random_unifrom')
     q_mu = inf.inference.Q.PointMass(bind = mu, initializer='random_unifrom')
     q_sigma = inf.inference.Q.PointMass(bind = sigma, initializer='ones')
     
     probmodel.compile(infMethod = 'KLqp', Q = [q_mu, q_sigma, q_z_n])
     model.fit(x_train)
     posterior_mu = probmodel.posterior(mu)

By default, the posterior **q** belongs to the same distribution family
than **p** , but in the above example we show how we can change that
(e.g. we set the posterior over **mu** to obtain a point mass estimate
instead of the Gaussian approximation used by default). We can also
configure how these **q's** are initialized using any of the Keras's
initializers.

Inspired by Keras semantics, we can furhter configure the inference
algorithm,

.. code:: python

     probmodel = ProbModel(vars = [theta,mu,sigma,z_n,x_n]) 
     
     q_z_n = inf.inference.Q.Multinomial(bind = z_n, initializer='random_unifrom')
     q_mu = inf.inference.Q.PointMass(bind = mu, initializer='random_unifrom')
     q_sigma = inf.inference.Q.PointMass(bind = sigma, initializer='ones')
     
     sgd = keras.optimizers.SGD(lr=0.01, momentum=0.9, nesterov=True)
     infkl_qp = inf.inference.KLqp(Q = [q_mu, q_sigma, q_z_n], optimizer = sgd, loss="ELBO")
     probmodel.compile(infMethod = infkl_qp)

     model.fit(x_train)
     posterior_mu = probmodel.posterior(mu)

Have a look at Inference Zoo to explore other configuration options.

In the last part of this guide, we highlight that InferPy directly
builds on top of Edward's compositionality idea to design complex
infererence algorithms.

.. code:: python

     probmodel = ProbModel(vars = [theta,mu,sigma,z_n,x_n]) 
     
     q_z_n = inf.inference.Q.Multinomial(bind = z_n, initializer='random_unifrom')
     q_mu = inf.inference.Q.PointMass(bind = mu, initializer='random_unifrom')
     q_sigma = inf.inference.Q.PointMass(bind = sigma, initializer='ones')
     
     infkl_qp = inf.inference.KLqp(Q = [q_z_n], optimizer = 'sgd', innerIter = 10)
     infMAP = inf.inference.MAP(Q = [q_mu, q_sigma], optimizer = 'sgd')

     probmodel.compile(infMethod = [infkl_qp,infMAP])
     
     model.fit(x_train)
     posterior_mu = probmodel.posterior(mu)

With the above sintaxis, we perform a variational EM algorithm, where
the E step is repeated 10 times for every MAP step.

More flexibility is also available by defining how each mini-batch is
processed by the inference algorithm. The following piece of code is
equivalent to the above one,

.. code:: python

     probmodel = ProbModel(vars = [theta,mu,sigma,z_n,x_n]) 

     q_z_n = inf.inference.Q.Multinomial(bind = z_n, initializer='random_unifrom')
     q_mu = inf.inference.Q.PointMass(bind = mu, initializer='random_unifrom')
     q_sigma = inf.inference.Q.PointMass(bind = sigma, initializer='ones')
     
     infkl_qp = inf.inference.KLqp(Q = [q_z_n])
     infMAP = inf.inference.MAP(Q = [q_mu, q_sigma])

     emAlg = lambda (infMethod, dataBatch):
        for _ in range(10)
            infMethod[0].update(data = dataBatch)
        
        infMethod[1].update(data = dataBatch)
        return 
     
     probmodel.compile(infMethod = [infkl_qp,infMAP], ingAlg = emAlg)
     
     model.fit(x_train, EPOCHS = 10)
     posterior_mu = probmodel.posterior(mu)

Have a look again at Inference Zoo to explore other complex
compositional options.

--------------

Guide to Bayesian Deep Learning
-------------------------------

InferPy inherits Edward's approach for representing probabilistic models
as (stochastic) computational graphs. As describe above, a random
variable :math:`x` is associated to a tensor :math:`x^*` in the
computational graph handled by TensorFlow, where the computations takes
place. This tensor :math:`x^*` contains the samples of the random
variable :math:`x`, i.e. :math:`x^* \sim p(x|\theta)`. In this way,
random variables can be involved in complex deterministic operations
containing deep neural networks, math operations and another libraries
compatible with Tensorflow (such as Keras).

Bayesian deep learning or deep probabilistic programming enbraces the
idea of employing deep neural networks within a probabilistic model in
order to capture complex non-linear dependencies between variables.

InferPy's API gives support to this powerful and flexible modelling
framework. Let us start by showing how a variational autoencoder over
binary data can be defined by mixing Keras and InferPy code.

.. code:: python

    from keras.models import Sequential
    from keras.layers import Dense, Activation

    M = 1000
    dim_z = 10
    dim_x = 100

    #Define the decoder network
    input_z  = keras.layers.Input(input_dim = dim_z)
    layer = keras.layers.Dense(256, activation = 'relu')(input_z)
    output_x = keras.layers.Dense(dim_x)(layer)
    decoder_nn = keras.models.Model(inputs = input, outputs = output_x)

    #define the generative model
    with inf.replicate(size = N)
     z = Normal(0,1, dim = dim_z)
     x = Bernoulli(logits = decoder_nn(z.value()), observed = true)

    #define the encoder network
    input_x  = keras.layers.Input(input_dim = d_x)
    layer = keras.layers.Dense(256, activation = 'relu')(input_x)
    output_loc = keras.layers.Dense(dim_z)(layer)
    output_scale = keras.layers.Dense(dim_z, activation = 'softplus')(layer)
    encoder_loc = keras.models.Model(inputs = input, outputs = output_mu)
    encoder_scale = keras.models.Model(inputs = input, outputs = output_scale)

    #define the Q distribution
    q_z = Normal(loc = encoder_loc(x.value()), scale = encoder_scale(x.value()))

    #compile and fit the model with training data
    probmodel.compile(infMethod = 'KLqp', Q = {z : q_z})
    probmodel.fit(x_train)

    #extract the hidden representation from a set of observations
    hidden_encoding = probmodel.predict(x_pred, targetvar = z)

In this case, the parameters of the encoder and decoder neural networks
are automatically managed by Keras. These parameters are them treated as
model parameters and not exposed to the user. In consequence, we can not
be Bayesian about them by defining specific prior distributions. In this
example (?) , we show how we can avoid that by introducing extra
complexity in the code.

Other examples of probabilisitc models using deep neural networks are: -
Bayesian Neural Networks - Mixture Density Networks - ...

We can also define a Keras model whose input is an observation and its
output its the expected value of the posterior over the hidden
variables, :math:`E[p(z|x)]`, by using the method 'toKeras', as a way to
create more expressive models.

.. code:: python

    from keras.layers import Conv2D, MaxPooling2D, Flatten
    from keras.layers import Input, LSTM, Embedding, Dense
    from keras.models import Model, Sequential

    #We define a Keras' model whose input is data sample 'x' and the output is the encoded vector E[p(z|x)]
    variational_econder_keras = probmodel.toKeras(targetvar = z)

    vision_model = Sequential()
    vision_model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
    vision_model.add(Conv2D(64, (3, 3), activation='relu'))
    vision_model.add(MaxPooling2D((2, 2)))
    vision_model.add(Flatten())

    # Now let's get a tensor with the output of our vision model:
    encoded_image = vision_model(input_x)

    # Let's concatenate the vae vector and the convolutional image vector:
    merged = keras.layers.concatenate([variational_econder_keras, encoded_image])

    # And let's train a logistic regression over 100 categories on top:
    output = Dense(100, activation='softmax')(merged)

    # This is our final model:
    classifier = Model(inputs=[input_x], outputs=output)

    # The next stage would be training this model on actual data.

+------+
| ##   |
| Guid |
| e    |
| to   |
| Vali |
| dati |
| on   |
| of   |
| Prob |
| abil |
| isti |
| c    |
| Mode |
| ls   |
+------+
| Mode |
| l    |
| vali |
| dati |
| on   |
| try  |
| to   |
| asse |
| ss   |
| how  |
| faif |
| hful |
| ly   |
| the  |
| infe |
| rere |
| d    |
| prob |
| abil |
| isti |
| c    |
| mode |
| l    |
| repr |
| esen |
| ts   |
| and  |
| expl |
| ain  |
| the  |
| obse |
| rved |
| data |
| .    |
+------+
| The  |
| main |
| tool |
| for  |
| mode |
| l    |
| vali |
| dati |
| on   |
| cons |
| ists |
| on   |
| anal |
| yzin |
| g    |
| the  |
| post |
| erio |
| r    |
| pred |
| icti |
| ve   |
| dist |
| ribu |
| tion |
| ,    |
+------+
| .. m |
| ath: |
| :  p |
| (y_{ |
| test |
| }, x |
| _{te |
| st}| |
| y_{t |
| rain |
| }, x |
| _{tr |
| ain} |
| ) =  |
| \int |
|  p(y |
| _{te |
| st}, |
|  x_{ |
| test |
| }|z, |
| \the |
| ta)p |
| (z,\ |
| thet |
| a|y_ |
| {tra |
| in}, |
|  x_{ |
| trai |
| n})  |
| dzd\ |
| thet |
| a    |
|      |
| .    |
+------+
| This |
| post |
| erio |
| r    |
| pred |
| icti |
| ve   |
| dist |
| ribu |
| tion |
| can  |
| be   |
| used |
| to   |
| meas |
| ure  |
| how  |
| well |
| the  |
| mode |
| l    |
| fits |
| an   |
| inde |
| pend |
| ent  |
| data |
| set  |
| usin |
| g    |
| the  |
| test |
| marg |
| inal |
| log- |
| like |
| liho |
| od,  |
| :mat |
| h:`\ |
| ln p |
| (y_{ |
| test |
| }, x |
| _{te |
| st}| |
| y_{t |
| rain |
| }, x |
| _{tr |
| ain} |
| )`,  |
+------+
| ``py |
| thon |
|  log |
| _lik |
| e =  |
| prob |
| mode |
| l.ev |
| alua |
| te(t |
| est_ |
| data |
| , me |
| tric |
| s =  |
| ['lo |
| g_li |
| keli |
| hood |
| '])` |
| `    |
+------+
| In   |
| othe |
| r    |
| case |
| s,   |
| we   |
| may  |
| need |
| to   |
| eval |
| ute  |
| the  |
| pred |
| icti |
| ve   |
| capa |
| city |
| of   |
| the  |
| mode |
| l    |
| with |
| resp |
| ect  |
| to   |
| some |
| targ |
| et   |
| vari |
| able |
| :mat |
| h:`y |
| `,   |
+------+
| .. m |
| ath: |
| :  p |
| (y_{ |
| test |
| }|x_ |
| {tes |
| t},  |
| y_{t |
| rain |
| }, x |
| _{tr |
| ain} |
| ) =  |
| \int |
|  p(y |
| _{te |
| st}| |
| x_{t |
| est} |
| ,z,\ |
| thet |
| a)p( |
| z,\t |
| heta |
| |y_{ |
| trai |
| n},  |
| x_{t |
| rain |
| }) d |
| zd\t |
| heta |
|      |
|      |
| ,    |
+------+
| So   |
| the  |
| metr |
| ics  |
| can  |
| be   |
| comp |
| uted |
| with |
| resp |
| ect  |
| to   |
| this |
| targ |
| et   |
| vari |
| able |
| by   |
| usin |
| g    |
| the  |
| 'tar |
| getv |
| ar'  |
| argu |
| ment |
| ,    |
+------+
| ``py |
| thon |
|  log |
| _lik |
| e, a |
| ccur |
| acy, |
|  mse |
|  = p |
| robm |
| odel |
| .eva |
| luat |
| e(te |
| st_d |
| ata, |
|  tar |
| getv |
| ar = |
|  y,  |
| metr |
| ics  |
| = [' |
| log_ |
| like |
| liho |
| od', |
|  'ac |
| cura |
| cy', |
|  'ms |
| e']) |
| ``   |
| So,  |
| the  |
| log- |
| like |
| liho |
| od   |
| metr |
| ic   |
| as   |
| well |
| as   |
| the  |
| accu |
| racy |
| and  |
| the  |
| mean |
| squa |
| re   |
| erro |
| r    |
| metr |
| ic   |
| are  |
| comp |
| uted |
| by   |
| usin |
| g    |
| the  |
| pred |
| icti |
| ve   |
| post |
| erio |
| r    |
| :mat |
| h:`p |
| (y_{ |
| test |
| }|x_ |
| {tes |
| t},  |
| y_{t |
| rain |
| }, x |
| _{tr |
| ain} |
| )`.  |
+------+
| Cust |
| om   |
| eval |
| uati |
| on   |
| metr |
| ics  |
| can  |
| also |
| be   |
| defi |
| ned, |
+------+
| \`\` |
| \`py |
| thon |
| def  |
| mean |
| \_ab |
| solu |
| te\_ |
| erro |
| r(po |
| ster |
| ior, |
| obse |
| rvat |
| ions |
| ,    |
| weig |
| hts= |
| None |
| ):   |
| pred |
| icti |
| ons  |
| =    |
| tf.m |
| ap\_ |
| fn(l |
| ambd |
| a    |
| x :  |
| x.ge |
| tMea |
| n(), |
| post |
| erio |
| r)   |
|      |
|  ret |
| urn  |
| tf.m |
| etri |
| cs.m |
| ean\ |
| _abs |
| olut |
| e\_e |
| rror |
| (obs |
| erva |
| tion |
| s,   |
| pred |
| icti |
| ons, |
| weig |
| hts) |
+------+
| mse, |
| mae  |
| =    |
| prob |
| mode |
| l.ev |
| alua |
| te(t |
| est\ |
| _dat |
| a,   |
| targ |
| etva |
| r    |
| = y, |
| metr |
| ics  |
| =    |
| ['ms |
| e',  |
| mean |
| \_ab |
| solu |
| te\_ |
| erro |
| r])  |
| \`\` |
| \`   |
+------+

Guide to Data Handling
----------------------

.. code:: python

    import numpy as np
    import inferpy as inf
    from inferpy.models import Normal, InverseGamma, Dirichlet

    #We first define the probabilistic model 
    with inf.ProbModel() as mixture_model:
        # K defines the number of components. 
        K=10
        #Prior for the means of the Gaussians 
        mu = Normal(loc = 0, scale = 1, shape=[K,d])
        #Prior for the precision of the Gaussians 
        invgamma = InverseGamma(concentration = 1, rate = 1, shape=[K,d])
        #Prior for the mixing proportions
        theta = Dirichlet(np.ones(K))

        # Number of observations
        N = 1000
        #data Model
        with inf.replicate(size = N, batch_size = 100)
            # Sample the component indicator of the mixture. This is a latent variable that can not be observed
            z_n = Multinomial(probs = theta)
            # Sample the observed value from the Gaussian of the selected component.  
            x_n = Normal(loc = tf.gather(mu,z_n), scale = tf.gather(invgamma,z_n), observed = true)

    #compile the probabilistic model
    mixture_model.compile(infAlg = 'klqp')

    #fit the model with data
    mixture_model.fit(data)

--------------

Probabilistic Model Zoo
=======================

Bayesian Linear Regression
--------------------------

.. code:: python

    # Shape = [1,d]
    w = Normal(0, 1, dim=d)
    # Shape = [1,1]
    w0 = Normal(0, 1)

    with inf.replicate(size = N):
        # Shape = [N,d]
        x = Normal(0,1, dim=d, observed = true)
        # Shape = [1,1] + [N,d]@[d,1] = [1,1] + [N,1] = [N,1] (by broadcasting)
        y = Normal(w0 + tf.matmul(x,w, transpose_b = true ), 1, observed = true)

    model = ProbModel(vars = [w0,w,x,y]) 

    data = model.sample(size=N)

    log_prob = model.log_prob(sample)

    model.compile(infMethod = 'KLqp')

    model.fit(data)

    print(probmodel.posterior([w0,w]))

--------------

Zero Inflated Linear Regression
-------------------------------

.. code:: python

    # Shape = [1,d]
    w = Normal(0, 1, dim=d)
    # Shape = [1,1]
    w0 = Normal(0, 1)

    # Shape = [1,1]
    p = Beta(1,1)

    with inf.replicate(size = N):
        # Shape [N,d]
        x = Normal(0,1000, dim=d, observed = true)
        # Shape [N,1]
        h = Binomial(p)
        # Shape [1,1] + [N,d]@[d,1] = [1,1] + [N,1] = [N,1] (by broadcasting)
        y0 = Normal(w0 + inf.matmul(x,w, transpose_b = true ), 1),
        # Shape [N,1]
        y1 = Delta(0.0)
        # Shape [N,1]*[N,1] + [N,1]*[N,1] = [N,1]
        y = Deterministic(h*y0 + (1-h)*y1, observed = true)

    model = ProbModel(vars = [w0,w,p,x,h,y0,y1,y]) 

    data = model.sample(size=N)

    log_prob = model.log_prob(sample)

    model.compile(infMethod = 'KLqp')

    model.fit(data)

    print(probmodel.posterior([w0,w]))

--------------

Bayesian Logistic Regression
----------------------------

.. code:: python

    # Shape = [1,d]
    w = Normal(0, 1, dim=d)
    # Shape = [1,1]
    w0 = Normal(0, 1)

    with inf.replicate(size = N):
        # Shape = [N,d]
        x = Normal(0,1, dim=d, observed = true)
        # Shape = [1,1] + [N,d]@[d,1] = [1,1] + [N,1] = [N,1] (by broadcasting)
        y = Binomial(logits = w0 + tf.matmul(x,w, transpose_b = true), observed = true)

    model = ProbModel(vars = [w0,w,x,y]) 

    data = model.sample(size=N)

    log_prob = model.log_prob(sample)

    model.compile(infMethod = 'KLqp')

    model.fit(data)

    print(probmodel.posterior([w0,w]))

--------------

Bayesian Multinomial Logistic Regression
----------------------------------------

.. code:: python

    # Number of classes
    K=10

    with inf.replicate(size = K):
        # Shape = [K,d]
        w = Normal(0, 1, dim=d)
        # Shape = [K,1]
        w0 = Normal(0, 1])

    with inf.replicate(size = N):
        # Shape = [N,d]
        x = Normal(0,1, dim=d, observed = true)
        # Shape = [1,K] + [N,d]@[d,K] = [1,K] + [N,K] = [N,K] (by broadcasting)
        y = Multinmial(logits = tf.transpose(w0) + tf.matmul(x,w, transpose_b = true), observed = true)

    model = ProbModel(vars = [w0,w,x,y]) 

    data = model.sample(size=N)

    log_prob = model.log_prob(sample)

    model.compile(infMethod = 'KLqp')

    model.fit(data)

    print(probmodel.posterior([w0,w]))

--------------

Mixture of Gaussians
--------------------

.. figure:: https://github.com/amidst/InferPy/blob/master/docs/_static/imgs/MoG.png
   :alt: Mixture of Gaussians

   Mixture of Gaussians

Version A

.. code:: python

    d=3
    K=10
    N=1000
    #Prior
    with inf.replicate(size = K):
        #Shape [K,d]
        mu = Normal(loc = 0, scale =1, dim=d)
        #Shape [K,d]
        sigma = InverseGamma(concentration = 1, rate = 1, dim=d)

    # Shape [1,K]
    p = Dirichlet(np.ones(K))

    #Data Model
    with inf.replicate(size = N):
        # Shape [N,1]
        z_n = Multinomial(probs = p)
        # Shape [N,d]
        x_n = Normal(loc = tf.gather(mu,z_n), scale = tf.gather(sigma,z_n), observed = true)
        
    model = ProbModel(vars = [p,mu,sigma,z_n, x_n]) 

    data = model.sample(size=N)

    log_prob = model.log_prob(sample)

    model.compile(infMethod = 'KLqp')

    model.fit(data)

    print(probmodel.posterior([mu,sigma]))

Version B

.. code:: python

    d=3
    K=10
    N=1000
    #Prior
    mu = Normal(loc = 0, scale =1, shape = [K,d])
    sigma = InverseGamma(concentration = 1, rate = 1, shape = [K,d])

    # Shape [1,K]
    p = Dirichlet(np.ones(K))

    #Data Model
    z_n = Multinomial(probs = p, shape = [N,1])
    # Shape [N,d]
    x_n = Normal(loc = tf.gather(mu,z_n), scale = tf.gather(sigma,z_n), observed = true)
        
    probmodel = ProbModel(vars = [p,mu,sigma,z_n, x_n]) 

    data = probmodel.sample(size=N)

    log_prob = probmodel.log_prob(sample)

    probmodel.compile(infMethod = 'KLqp')

    probmodel.fit(data)

    print(probmodel.posterior([mu,sigma]))

--------------

Linear Factor Model (PCA)
-------------------------

.. figure:: https://github.com/amidst/InferPy/blob/master/docs/_static/imgs/LinearFactor.png
   :alt: Linear Factor Model

   Linear Factor Model

.. code:: python

    K = 5
    d = 10
    N=200

    with inf.replicate(size = K)
        # Shape [K,d]
        mu = Normal(0,1, dim = d)

    # Shape [1,d]
    mu0 = Normal(0,1, dim = d)

    sigma = 1.0

    with inf.replicate(size = N):
        # Shape [N,K]
        w_n = Normal(0,1, dim = K)
        # inf.matmul(w_n,mu) has shape [N,K] x [K,d] = [N,d] by broadcasting mu. 
        # Shape [1,d] + [N,d] = [N,d] by broadcasting mu0
        x = Normal(mu0 + inf.matmul(w,mu), sigma, observed = true)

    probmodel = ProbModel([mu,mu0,w_n,x]) 

    data = probmodel.sample(size=N)

    log_prob = probmodel.log_prob(sample)

    probmodel.compile(infMethod = 'KLqp')

    probmodel.fit(data)

    print(probmodel.posterior([mu,mu0]))

--------------

PCA with ARD Prior (PCA)
------------------------

.. code:: python

    K = 5
    d = 10
    N=200

    with inf.replicate(size = K)
        # Shape [K,d]
        alpha = InverseGamma(1,1, dim = d)
        # Shape [K,d]
        mu = Normal(0,1, dim = d)

    # Shape [1,d]
    mu0 = Normal(0,1, dim = d)

    # Shape [1,1]
    sigma = InverseGamma(1,1, dim = 1)

    with inf.replicate(size = N):
        # Shape [N,K]
        w_n = Normal(0,1, dim = K)
        # inf.matmul(w_n,mu) has shape [N,K] x [K,d] = [N,d] by broadcasting mu. 
        # Shape [1,d] + [N,d] = [N,d] by broadcasting mu0
        x = Normal(mu0 + inf.matmul(w,mu), sigma, observed = true)

    probmodel = ProbModel([alpha,mu,mu0,sigma,w_n,x]) 

    data = probmodel.sample(size=N)

    log_prob = probmodel.log_prob(sample)

    probmodel.compile(infMethod = 'KLqp')

    probmodel.fit(data)

    print(probmodel.posterior([alpha,mu,mu0,sigma]))

--------------

Mixed Membership Model
----------------------

.. figure:: https://github.com/amidst/InferPy/blob/master/docs/_static/imgs/LinearFactor.png
   :alt: Mixed Membership Model

   Mixed Membership Model

.. code:: python

    K = 5
    d = 10
    N=200
    M=50

    with inf.replicate(size = K)
        #Shape = [K,d]
        mu = Normal(0,1, dim = d)
        #Shape = [K,d]
        sigma = InverseGamma(1,1, dim = d)

    with inf.replicate(size = N):
        #Shape = [N,K]
        theta_n = Dirichlet(np.ones(K))
        with inf.replicate(size = M):
            # Shape [N*M,1]
            z_mn = Multinomial(theta_n)
            # Shape [N*M,d]
            x = Normal(tf.gather(mu,z_mn), tf.gather(sigma,z_mn), observed = true)

    probmodel = ProbModel([mu,sigma,theta_n,z_mn,x]) 

    data = probmodel.sample(size=N)

    log_prob = probmodel.log_prob(sample)

    probmodel.compile(infMethod = 'KLqp')

    probmodel.fit(data)

    print(probmodel.posterior([mu,sigma]))

--------------

Latent Dirichlet Allocation
---------------------------

.. code:: python

    K = 5 # Number of topics 
    d = 1000 # Size of vocabulary
    N=200 # Number of documents in the corpus
    M=50 # Number of words in each document

    with inf.replicate(size = K)
        #Shape = [K,d]
        dir = Dirichlet(np.ones(d)*0.1)

    with inf.replicate(size = N):
        #Shape = [N,K]
        theta_n = Dirichlet(np.ones(K))
        with inf.replicate(size = M):
            # Shape [N*M,1]
            z_mn = Multinomial(theta_n)
            # Shape [N*M,d]
            x = Multinomial(tf.gather(dir,z_mn), tf.gather(dir,z_mn), observed = true)

    probmodel = ProbModel([dir,theta_n,z_mn,x]) 

    data = probmodel.sample(size=N)

    log_prob = probmodel.log_prob(sample)

    probmodel.compile(infMethod = 'KLqp')

    probmodel.fit(data)

    print(probmodel.posterior(dir))

--------------

Matrix Factorization
--------------------

.. figure:: https://github.com/amidst/InferPy/blob/master/docs/_static/imgs/MatrixFactorization.png
   :alt: Matrix Factorization Model

   Matrix Factorization Model

Version A

.. code:: python

    N=200
    M=50
    K=5

    with inf.replicate(name = 'A', size = M)
        # Shape [M,K]
        gamma_m = Normal(0,1, dim = K)

    with inf.replicate(name = 'B', size = N):
        # Shape [N,K]
        w_n = Normal(0,1, dim = K)
        
    with inf.replicate(compound = ['A', 'B']):
        # x_mn has shape [N,K] x [K,M] = [N,M]
        x_nm = Normal(tf.matmul(w_n,gamma_m, transpose_b = true), 1, observed = true)


    probmodel = ProbModel([w_n,gamma_m,x_nm]) 

    data = probmodel.sample(size=N)

    log_prob = probmodel.log_prob(sample)

    probmodel.compile(infMethod = 'KLqp')

    probmodel.fit(data)

    print(probmodel.posterior([w_n,gamma_m]))

Version B

.. code:: python

    N=200
    M=50
    K=5

    # Shape [M,K]
    gamma_m = Normal(0,1, shape = [M,K])

    # Shape [N,K]
    w_n = Normal(0,1, shape = [N,K])
        
    # x_mn has shape [N,K] x [K,M] = [N,M]
    x_nm = Normal(tf.matmul(w_n,gamma_m, transpose_b = true), 1, observed = true)

    probmodel = ProbModel([w_n,gamma_m,x_nm]) 

    data = probmodel.sample(size=N)

    log_prob = probmodel.log_prob(sample)

    probmodel.compile(infMethod = 'KLqp')

    probmodel.fit(data)

    print(probmodel.posterior([w_n,gamma_m]))

--------------

Linear Mixed Effect Model
-------------------------

.. code:: python


    N = 1000 # number of observations
    n_s = 100 # number of students
    n_d = 10 # number of instructor
    n_dept = 10 # number of departments

    eta_s = Normal(0,1, dim = n_s)
    eta_d = Normal(0,1, dim = n_d)
    eta_dept = Normal(0,1, dim = n_dept)
    mu = Normal(0,1)
    mu_service = Normal(0,1)

    with inf.replicate( size = N):
        student = Multinomial(probs = np.rep(1,n_s)/n_s, observed = true)
        instructor = Multinomial(probs = np.rep(1,n_d)/n_d, observed = true)
        department = Multinomial(probs = np.rep(1,n_dept)/n_dept, observed = true)
        service = Binomial (probs = 0.5, observed = true)
        y = Normal (tf.gather(eta_s,student) 
                    + bs.gather(eta_d,instructor) 
                    + bs.gather(eta_dept,department) 
                    +  mu + mu_service*service, 1, observed = true)

    #vars = 'all' automatically add all previously created random variables
    probmodel = ProbModel(vars = 'all') 

    data = probmodel.sample(size=N)

    log_prob = probmodel.log_prob(sample)

    probmodel.compile(infMethod = 'KLqp')

    probmodel.fit(data)

    #When no argument is given to posterior, return all non-replicated random varibles
    print(probmodel.posterior())

--------------

Bayesian Neural Network Classifier
----------------------------------

.. code:: python

    d = 10   # number of features
    N = 1000 # number of observations

    def neural_network(x):
      h = tf.tanh(tf.matmul(x, W_0) + b_0)
      h = tf.tanh(tf.matmul(h, W_1) + b_1)
      h = tf.matmul(h, W_2) + b_2
      return tf.reshape(h, [-1])

    W_0 = Normal(0,1, shape = [d,10])
    W_1 = Normal(0,1, shape = [10,10])
    W_2 = Normal(0,1, shape = [10,1])

    b_0 = Normal(0,1, shape = [1,10])
    b_1 = Normal(0,1, shape = [1,10])
    b_2 = Normal(0,1, shape = [1,1])


    with inf.replicate(size = N):
        x = Normal(0,1, dim = d, observed = true)
        y = Bernoulli(logits=neural_network(x), observed = true)

    #vars = 'all' automatically add all previously created random variables
    probmodel = ProbModel(vars = 'all') 

    data = probmodel.sample(size=N)

    log_prob = probmodel.log_prob(sample)

    probmodel.compile(infMethod = 'KLqp')

    probmodel.fit(data)

    #When no argument is given to posterior, return all non-replicated random varibles
    print(probmodel.posterior())

--------------

Variational Autoencoder
-----------------------

.. code:: python

    from keras.models import Sequential
    from keras.layers import Dense, Activation

    M = 1000
    dim_z = 10
    dim_x = 100

    #Define the decoder network
    input_z  = keras.layers.Input(input_dim = dim_z)
    layer = keras.layers.Dense(256, activation = 'relu')(input_z)
    output_x = keras.layers.Dense(dim_x)(layer)
    decoder_nn = keras.models.Model(inputs = input, outputs = output_x)

    #define the generative model
    with inf.replicate(size = N)
     z = Normal(0,1, dim = dim_z)
     x = Bernoulli(logits = decoder_nn(z.value()), observed = true)

    #define the encoder network
    input_x  = keras.layers.Input(input_dim = d_x)
    layer = keras.layers.Dense(256, activation = 'relu')(input_x)
    output_loc = keras.layers.Dense(dim_z)(layer)
    output_scale = keras.layers.Dense(dim_z, activation = 'softplus')(layer)
    encoder_loc = keras.models.Model(inputs = input, outputs = output_mu)
    encoder_scale = keras.models.Model(inputs = input, outputs = output_scale)

    #define the Q distribution
    q_z = Normal(loc = encoder_loc(x.value()), scale = encoder_scale(x.value()))

    #compile and fit the model with training data
    probmodel.compile(infMethod = 'KLqp', Q = {z : q_z})
    probmodel.fit(x_train)

    #extract the hidden representation from a set of observations
    hidden_encoding = probmodel.predict(x_pred, targetvar = z)
