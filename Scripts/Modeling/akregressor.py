import os, sys
import autokeras as ak
from keras_tuner.engine import hyperparameters as hp
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, CSVLogger, TensorBoard
import tensorflow.keras.backend as K
import tensorflow as tf

def ak_model():
    """
    AutoKeras regressor model with normalization, dense block and regression head
    """
    input_node = ak.Input()
    normalize_node = ak.Normalization()(input_node)
    dense_node = ak.DenseBlock()(normalize_node)
    output_node = ak.RegressionHead(metrics=['mae'])(dense_node)
    return input_node, output_node

def init_callbacks(repo, approach, approach_name, task):
    """
    Initialize callbacks for training regressor model
    """
    if not os.path.exists('Regressors/{}/{}/{}/{}/logs'.format(repo, approach, approach_name, task)):
        os.makedirs('Regressors/{}/{}/{}/{}/logs'.format(repo, approach, approach_name, task))
    if not os.path.exists('Regressors/{}/{}/{}/{}/checkpoints'.format(repo, approach, approach_name, task)):
        os.makedirs('Regressors/{}/{}/{}/{}/checkpoints'.format(repo, approach, approach_name, task))

    early_stopping = EarlyStopping(
        monitor='val_mae',
        min_delta=0.001,
        patience=20,
        verbose=1,
        mode='min',
        baseline=None,
        restore_best_weights=True
    ) # Stop training when a monitored quantity has stopped improving.

    model_checkpoint = ModelCheckpoint(
        filepath='Regressors/{}/{}/{}/{}'.format(repo, approach, approach_name, task) + '/checkpoints/model.{epoch:02d}-{val_mae:.4f}.h5',
        monitor='val_mae',
        verbose=1,
        save_best_only=True,
        save_weights_only=True,
        mode='min',
        save_freq='epoch',
        options=None
    ) # Save the model after every epoch.

    lr_scheduler = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.1,
        patience=5,
        verbose=1,
        mode='auto',
        min_delta=0.0001
    )
    tensorboard = TensorBoard(log_dir='Regressors/{}/{}/{}/{}/logs'.format(repo, approach, approach_name, task), histogram_freq=1, write_graph=True)
    
    return [early_stopping, model_checkpoint, lr_scheduler, tensorboard]
