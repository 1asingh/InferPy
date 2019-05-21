from tensorflow_probability import edward2 as ed
import tensorflow as tf

from inferpy import util


def ELBO(pmodel, qmodel, sample_dict, plate_size=None, batch_weight=1):
    # create combined model; for that first compute the plate size (for now, just one plate can be used)
    if not plate_size:
        plate_size = util.iterables.get_plate_size(pmodel.vars, sample_dict)

    sess = util.get_session()

    # expand the qmodel (just in case the q model uses data from sample_dict, use interceptor too)
    with ed.interception(util.interceptor.set_values_condition(qmodel)):
    #with ed.interception(util.interceptor.set_values(**sample_dict)):
        qvars, _ = qmodel.expand_model(plate_size)

    qmodel._predict_enabled.load(True, session=sess)
    for k, v in sample_dict.items():
        qmodel._predict_dict_expanded[k].load(v, session=sess)

    # expand de pmodel, using the intercept.set_values function, to include the sample_dict and the expanded qvars
    with ed.interception(util.interceptor.set_values(**qvars)):
        #with ed.interception(util.interceptor.set_values_condition(pmodel)):
        pvars, _ = pmodel.expand_model(plate_size)

    pmodel._predict_enabled.load(True, session=sess)
    for k, v in sample_dict.items():
        pmodel._predict_dict_expanded[k].load(v, session=sess)

    # compute energy
    energy = tf.reduce_sum(
        [(batch_weight if p.is_datamodel else 1) * tf.reduce_sum(p.log_prob(p.value))
         for p in pvars.values()])

    # compute entropy
    entropy = - tf.reduce_sum(
        [(batch_weight if q.is_datamodel else 1) * tf.reduce_sum(q.log_prob(q.value))
         for q in qvars.values() if not q.is_datamodel])

    # compute ELBO
    ELBO = energy + entropy

    # This function will be minimized. Return minus ELBO
    return -ELBO
