import os, sys
SEED = 0
os.environ['PYTHONHASHSEED'] = str(SEED)
import random
import _pickle as pkl
import json
import gzip
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Model, Sequential, Input, models, initializers, optimizers
from tensorflow.keras.layers import Dense, Dropout, RepeatVector, Layer, GRU, Embedding, TimeDistributed
import tensorflow.keras.backend as K
import tensorflow.keras.losses as losses
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, CSVLogger
from tensorflow.keras.optimizers import Adam, RMSprop, SGD
import keras_tuner as kt
import warnings

warnings.filterwarnings('ignore')
warnings.simplefilter(action='ignore', category=FutureWarning)

def set_seeds(SEED):
    """
    Set seeds for reproducibility.
    """
    random.seed(SEED)
    tf.random.set_seed(SEED)
    np.random.seed(SEED)
    keras.utils.set_random_seed(SEED)
    tf.config.experimental.enable_op_determinism()
    os.environ['PYTHONHASHSEED'] = str(SEED)

def perplexity(y_true, y_pred):
    """
    Perplexity metric.
    """
    cross_entropy = K.sparse_categorical_crossentropy(y_true, y_pred)
    ppl = K.exp(cross_entropy)
    return ppl

def rnn2feature(vecs, mask):
    """
    Convert RNN outputs to feature vectors
    """
    mask = np.expand_dims(mask, axis=-1)
    vecs = vecs * mask
    vecs = np.sum(vecs, axis=1)
    vecs = vecs / np.sum(mask, axis=1)
    return vecs

class MyGRU(kt.HyperModel):
    """
    Custom GRU model for hyperparameter
    """
    def __init__(self, input_dim, length, output_dim):
        self.input_dim = input_dim
        self.length = length
        self.output_dim = output_dim

    def build(self, hp):
        set_seeds(SEED)

        shared_embedding = hp.Choice('shared_embedding', values=[True, False]) # Whether to use shared embedding layer
        num_layers = hp.Int('num_layers', min_value=1, max_value=2, step=1) # Number of layers

        # Define the dropout rates for the encoder and decoder
        en_dropouts = []
        de_dropouts = []
        for i in range(num_layers):
            en_dropouts.append(hp.Float(f'en_dropout_{i+1}', min_value=0.0, max_value=0.6, step=0.2))
            de_dropouts.append(hp.Float(f'de_dropout_{i+1}', min_value=0.0, max_value=0.6, step=0.2))

        activation_choice = hp.Choice('activation', values=['relu', 'tanh']) # Activation function
        optimizer_choice = hp.Choice('optimizer', values=['adam', 'rmsprop']) # Optimizer
        learning_rate = hp.Choice('learning_rate', values=[0.1, 0.01, 0.001]) # Learning rate

        # Define the encoder sequence
        encoder_inputs = Input(shape=(self.length,), name='encoder_inputs')
        if shared_embedding:
            shared_embedding = Embedding(input_dim=self.input_dim, output_dim=self.output_dim , mask_zero=True, name='shared_embedding')
            encoder_embedding = shared_embedding(encoder_inputs)
        else:
            encoder_embedding = Embedding(input_dim=self.input_dim, output_dim=self.output_dim , mask_zero=True, name='encoder_embedding')(encoder_inputs)
        encoder_states = []
        encoder = encoder_embedding
        for i in range(num_layers):
            encoder, state_h = GRU(units=self.output_dim, return_sequences=True, return_state=True, activation=activation_choice, dropout=en_dropouts[i], name=f'encoder_gru_{i+1}')(encoder)
            encoder_states.append(state_h)

        # Define the encoder model
        encoder_model = Model(encoder_inputs, [encoder] + encoder_states, name='encoder_model')

        # Define the decoder sequence
        decoder_inputs = Input(shape=(self.length,), name='decoder_inputs')
        if shared_embedding:
            decoder_embedding = shared_embedding(decoder_inputs)
        else:
            decoder_embedding = Embedding(input_dim=self.input_dim, output_dim=self.output_dim, mask_zero=True, name='decoder_embedding')(decoder_inputs)
        decoder = decoder_embedding
        for i in range(num_layers):
            decoder = GRU(units=self.output_dim, return_sequences=True, activation=activation_choice, dropout=de_dropouts[i], name=f'decoder_gru_{i+1}')(decoder, initial_state=encoder_states[i])

        # Define the output layer
        decoder_outputs = Dense(self.input_dim, activation='softmax', name='decoder_dense')(decoder)

        # Define the full seq2seq model
        model = Model([encoder_inputs, decoder_inputs], decoder_outputs, name='seq2seq_model')
        
        # Define the optimizer
        if optimizer_choice == 'adam':
            optimizer = Adam(learning_rate=learning_rate)
        elif optimizer_choice == 'rmsprop':
            optimizer = RMSprop(learning_rate=learning_rate)

        # Compile the model
        model.compile(
            optimizer=optimizer,
            loss='sparse_categorical_crossentropy',
            metrics=[perplexity]
        )

        return model

    def fit(self, hp, model, *args, **kwargs):
        set_seeds(SEED)
        return model.fit(
            *args,
            batch_size=hp.Choice("batch_size", [64, 128, 256]), # Batch size
            **kwargs,
        )