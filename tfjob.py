# -*- coding: utf-8 -*-
"""tfjob.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Di9ha2wcHThHzn4NN6Fa1pmoqviViwSO
"""

import tensorflow as tf 
from sklearn.datasets import load_breast_cancer

# a quick neural network

import numpy as np
from tensorflow import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.optimizers import SGD, Adam
from keras.utils import np_utils
import matplotlib.pyplot as plt
from keras.layers.core import Dropout
import logging
import sys
import argparse
np.random.seed(1671)

"""Note: The following parameters below are key in the training of the network"""

# network and training 
NB_EPOCH = 50
VERBOSE = 1
OPTIMIZER = Adam()
N_HIDDEN = 128

def input_fn():
  cancer = load_breast_cancer()
  X = cancer.data
  y = cancer.target
  y = np.expand_dims(y,axis=1)
  x = tf.cast(X, tf.float32)
  dataset = tf.data.Dataset.from_tensor_slices((x, y))
  dataset = dataset.repeat(100)
  dataset = dataset.batch(32)

  return dataset

def main(args):

  if len(args) < 2:
    print('You must specify model_dir for checkpoints such as'
          ' /tmp/tfkeras_example/.')
    return

  model_dir = args[1]
  print('Using %s to store checkpoints.' % model_dir)

  # Define a Keras Model.
  NB_CLASSES = 1 
  OPTIMIZER = Adam()
  N_HIDDEN = 128
  DROPOUT = 0.3

  model = Sequential()
  model.add(Dense(N_HIDDEN,input_shape=(30,)))
  model.add(Activation('relu'))
  model.add(Dropout(DROPOUT))
  model.add(Dense(N_HIDDEN))
  model.add(Activation('relu'))
  model.add(Dropout(DROPOUT))
  model.add(Dense(NB_CLASSES))
  model.add(Activation('sigmoid'))

  model.compile(loss='categorical_crossentropy',optimizer=OPTIMIZER,
              metrics=['accuracy'])
  
  model.summary()

  # Define DistributionStrategies and convert the Keras Model to an
  # Estimator that utilizes these DistributionStrateges.
  # Evaluator is a single worker, so using MirroredStrategy.
  

  config = tf.estimator.RunConfig(
          train_distribute=tf.distribute.MultiWorkerMirroredStrategy(),
          eval_distribute=tf.distribute.MirroredStrategy())
  keras_estimator = tf.keras.estimator.model_to_estimator(
      keras_model=model, config=config, model_dir=model_dir)

  # Train and evaluate the model. Evaluation will be skipped if there is not an
  # "evaluator" job in the cluster.

  tf.estimator.train_and_evaluate(
      keras_estimator,
      train_spec=tf.estimator.TrainSpec(input_fn=input_fn),
      eval_spec=tf.estimator.EvalSpec(input_fn=input_fn))


if __name__ == '__main__':
  logger = tf.get_logger()
  logger.setLevel(logging.INFO)
  tf.compat.v1.app.run(argv=sys.argv)

  parser = argparse.ArgumentParser()
  parser.add_argument('--saved_model_dir',
                      type=str,
                      required=True,
                      help='Tensorflow export directory.')
  
  parsed_args = parser.parse_args()
  main(parsed_args)

