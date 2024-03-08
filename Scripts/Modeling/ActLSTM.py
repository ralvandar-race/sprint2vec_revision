import os, sys
SEED = 0
os.environ['PYTHONHASHSEED'] = str(SEED)
import random
import json
import gzip
import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Model, Sequential, Input, models, initializers, optimizers
from tensorflow.keras.layers import Dense, Dropout, RepeatVector, Layer, LSTM, Embedding, TimeDistributed
import tensorflow.keras.backend as K
import tensorflow.keras.losses as losses
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, CSVLogger, TensorBoard
from tensorflow.keras.optimizers import Adam, RMSprop, SGD
import matplotlib.pyplot as plt

import keras_tuner as kt

import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter(action='ignore', category=FutureWarning)

def set_seeds(SEED):
    random.seed(SEED)
    tf.random.set_seed(SEED)
    np.random.seed(SEED)
    keras.utils.set_random_seed(SEED)
    tf.config.experimental.enable_op_determinism()
    os.environ['PYTHONHASHSEED'] = str(SEED)

def perplexity(y_true, y_pred):
    cross_entropy = K.sparse_categorical_crossentropy(y_true, y_pred)
    ppl = K.exp(cross_entropy)
    return ppl

def init_callbacks(repo, output_dim, rnn_type):
    if not os.path.exists('Act Models/{}/{}'.format(repo, output_dim)):
        os.makedirs('Act Models/{}/{}'.format(repo, output_dim))
    if not os.path.exists('Act Models/{}/{}/{}'.format(repo, output_dim, rnn_type)):
        os.makedirs('Act Models/{}/{}/{}'.format(repo, output_dim, rnn_type))
    if not os.path.exists('Act Models/{}/{}/{}/logs'.format(repo, output_dim, rnn_type)):
        os.makedirs('Act Models/{}/{}/{}/logs'.format(repo, output_dim, rnn_type))
    if not os.path.exists('Act Models/{}/{}/{}/checkpoints'.format(repo, output_dim, rnn_type)):
        os.makedirs('Act Models/{}/{}/{}/checkpoints'.format(repo, output_dim, rnn_type))

    early_stopping = EarlyStopping(
        monitor='val_perplexity',
        min_delta=0.01,
        patience=10,
        verbose=1,
        mode='auto',
        baseline=None,
        restore_best_weights=True
    )

    model_checkpoint = ModelCheckpoint(
        filepath='Act Models/{}/{}/{}'.format(repo, output_dim, rnn_type) + '/checkpoints/model.{epoch:02d}-{val_perplexity:.2f}.h5',
        monitor='val_perplexity',
        verbose=1,
        save_best_only=True,
        save_weights_only=True,
        mode='auto',
        save_freq='epoch',
        options=None
    )

    lr_scheduler = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.1,
        patience=5,
        verbose=1,
        mode='auto',
        min_delta=0.0001
    )
    # csv_logger = CSVLogger('Act Models/{}/{}/logs/lstm_.csv'.format(repo, output_dim), append=False, separator='\t')
    tensorboard = TensorBoard(log_dir='Act Models/{}/{}/{}/logs'.format(repo, output_dim, rnn_type), histogram_freq=1, write_graph=True)
    
    return [early_stopping, model_checkpoint, lr_scheduler, tensorboard]

def rnn2feature(vecs, mask):
    mask = np.expand_dims(mask, axis=-1)
    vecs = vecs * mask
    vecs = np.sum(vecs, axis=1)
    vecs = vecs / np.sum(mask, axis=1)
    return vecs

class MyLSTM(kt.HyperModel):
    def __init__(self, input_dim, length, output_dim):
        self.input_dim = input_dim
        self.length = length
        self.output_dim = output_dim

    def build(self, hp):
        set_seeds(SEED)

        shared_embedding = hp.Choice('shared_embedding', values=[True, False])
        num_layers = hp.Int('num_layers', min_value=1, max_value=2, step=1)

        en_dropouts = []
        de_dropouts = []
        for i in range(num_layers):
            en_dropouts.append(hp.Float(f'en_dropout_{i+1}', min_value=0.0, max_value=0.6, step=0.2))
            de_dropouts.append(hp.Float(f'de_dropout_{i+1}', min_value=0.0, max_value=0.6, step=0.2))

        activation_choice = hp.Choice('activation', values=['relu', 'tanh'])
        optimizer_choice = hp.Choice('optimizer', values=['adam', 'rmsprop'])
        learning_rate = hp.Choice('learning_rate', values=[0.1, 0.01, 0.001])

        # encoder
        encoder_inputs = Input(shape=(self.length,), name='encoder_inputs')
        if shared_embedding:
            shared_embedding = Embedding(input_dim=self.input_dim, output_dim=self.output_dim , mask_zero=True, name='shared_embedding')
            encoder_embedding = shared_embedding(encoder_inputs)
        else:
            encoder_embedding = Embedding(input_dim=self.input_dim, output_dim=self.output_dim , mask_zero=True, name='encoder_embedding')(encoder_inputs)
        encoder_states = []
        encoder = encoder_embedding
        for i in range(num_layers):
            encoder, state_h, state_c = LSTM(units=self.output_dim, return_sequences=True, return_state=True, dropout=en_dropouts[i], activation=activation_choice, name=f'encoder_lstm_{i+1}')(encoder)
            encoder_states.append([state_h, state_c])

        encoder_model = Model(encoder_inputs, [encoder] + encoder_states, name='encoder_model')

        # decoder
        decoder_inputs = Input(shape=(self.length,), name='decoder_inputs')
        if shared_embedding:
            decoder_embedding = shared_embedding(decoder_inputs)
        else:
            decoder_embedding = Embedding(input_dim=self.input_dim, output_dim=self.output_dim, mask_zero=True, name='decoder_embedding')(decoder_inputs)
        decoder = decoder_embedding
        for i in range(num_layers):
            decoder = LSTM(units=self.output_dim, return_sequences=True, dropout=de_dropouts[i], activation=activation_choice, name=f'decoder_lstm_{i+1}')(decoder, initial_state=encoder_states[i])

        decoder_outputs = Dense(self.input_dim, activation='softmax', name='decoder_dense')(decoder)

        model = Model([encoder_inputs, decoder_inputs], decoder_outputs, name='seq2seq_model')

        if optimizer_choice == 'adam':
            optimizer = Adam(learning_rate=learning_rate)
        elif optimizer_choice == 'rmsprop':
            optimizer = RMSprop(learning_rate=learning_rate)

        # Compile the model
        model.compile(
            optimizer=optimizer,
            loss = 'sparse_categorical_crossentropy',
            metrics=[perplexity]
        )

        return model

    def fit(self, hp, model, *args, **kwargs):
        set_seeds(SEED)
        return model.fit(
            *args,
            batch_size=hp.Choice("batch_size", [64, 128, 256]),
            **kwargs,
        )

def save_best_model(tuner, repo, output_dim, rnn_type):
    best_model = tuner.get_best_models(num_models=1)[0]
    best_model.save('Act Models/{}/{}/{}/best'.format(repo, output_dim, rnn_type))
    best_model.save_weights('Act Models/{}/{}/{}/best_weights'.format(repo, output_dim, rnn_type))

    best_trial = tuner.oracle.get_best_trials(num_trials=1)[0]
    with open('Act Models/{}/{}/{}/best_trial_id.txt'.format(repo, output_dim, rnn_type), 'w') as f:
        f.write(str(best_trial.trial_id))

    best_hps = best_trial.hyperparameters.values
    with open('Act Models/{}/{}/{}/best_hps.json'.format(repo, output_dim, rnn_type), 'w') as f:
        json.dump(best_hps, f, indent=4)
    
    return best_model

def load_best_model(repo, output_dim, rnn_type):
    return models.load_model('Act Models/{}/{}/{}/best'.format(repo, output_dim, rnn_type), custom_objects={'perplexity': perplexity})

def save_performance(repo, output_dim, rnn_type, train_loss, train_ppl, valid_loss, valid_ppl, test_loss, test_ppl):
    if not os.path.exists('Act Models/{}/{}/{}/best_performance.csv'.format(repo, output_dim, rnn_type)):
        with open('Act Models/{}/{}/{}/best_performance.csv'.format(repo, output_dim, rnn_type), 'w') as f:
            f.write('train_loss,train_ppl,valid_loss,valid_ppl,test_loss,test_ppl\n')
            f.write('{},{},{},{},{},{}\n'.format(train_loss, train_ppl, valid_loss, valid_ppl, test_loss, test_ppl))