import random
import re

import matplotlib.pyplot as plt
import nltk
import numpy as np
import tensorflow as tf
from gensim.models import Doc2Vec
from utils.config import DATASET, EMBED_MODEL, INPUT
from utils.data_reader import ManySStuBs4J


def plot_graphs(history, metric):
    plt.plot(history.history[metric])
    plt.plot(history.history['val_'+metric], '')
    plt.xlabel("Epochs")
    plt.ylabel(metric)
    plt.legend([metric, 'val_'+metric])
    plt.show()


bug_type = 'MORE_SPECIFIC_IF'

p = r"([^\w_])"

sstubs = ManySStuBs4J(DATASET).bugs
model = Doc2Vec.load(str(EMBED_MODEL))

random.Random(3).shuffle(sstubs)
tf.random.set_seed(3)


xs = []
ys = []

for bug in sstubs:

    if bug.bug_type != bug_type:
        continue

    if (INPUT / bug.buggy_file_line_dir).exists():
        with open(INPUT / bug.buggy_file_line_dir / bug.file_name) as f:
            lines = f.read().splitlines()
            buggy_line = lines[bug.bug_line_num - 1]

        bug_vec = model.infer_vector(
            nltk.wordpunct_tokenize(
                ' '.join(re.split(pattern=p, string=buggy_line))),
            alpha=0.025, steps=300
        )

        xs.append(bug_vec)
        ys.append(1)

    if (INPUT / bug.fixed_file_line_dir).exists():
        with open(INPUT / bug.fixed_file_line_dir / bug.file_name) as f:
            lines = f.read().splitlines()
            fixed_line = lines[bug.fix_line_num - 1]

        fix_vec = model.infer_vector(
            nltk.wordpunct_tokenize(
                ' '.join(re.split(pattern=p, string=fixed_line))),
            alpha=0.025, steps=300
        )

        xs.append(fix_vec)
        ys.append(0)


# Split into training and validation data
nb_training = int(0.8*len(xs))
xs_training = np.array(xs[:nb_training])

ys_training = np.array(ys[:nb_training])
xs_validation = np.array(xs[nb_training:])

ys_validation = np.array(ys[nb_training:])
print(f"{len(xs_training)} training examples")
print(f"{len(xs_validation)} validation examples")

x_length = len(xs[0])

model = tf.keras.Sequential([
    tf.keras.layers.Dense(300, input_dim=x_length,
                          activation="relu", kernel_initializer='normal'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(100, activation="relu", kernel_initializer='normal'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(1, activation="sigmoid",
                          kernel_initializer='normal'),
])

# print(model.summary())

model.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
)
history = model.fit(xs_training, ys_training, batch_size=50, epochs=50,
                    verbose=1, validation_data=(xs_validation, ys_validation))

plot_graphs(history, 'accuracy')
plot_graphs(history, 'loss')
