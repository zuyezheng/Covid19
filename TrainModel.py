import numpy
import pandas
import os

from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint

# workaround for cuda LSTM layer issues
from tensorflow.compat.v1 import ConfigProto, InteractiveSession
config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)


def generate_observations(file, steps, min_curve_length, min_cases, curve_names=None):
    curves = pandas.read_csv(file)
    if curve_names is None:
        curve_names = curves['Name'].unique()

    xs = []
    ys = []
    for curve_name in curve_names:
        # get the values for the current curve and start at first non zero
        curve = curves[curves['Name'] == curve_name]['Cases'].to_list()

        # don't train on smaller curves or low number of total cases
        if len(curve) < min_curve_length or sum(curve) < min_cases:
            continue

        # generate an x, y pair for each point in the curve
        for i in range(len(curve)):
            # get the previous points in the curve as the xs, padded by 0s
            x = numpy.zeros((steps, 1))
            for j in range(-1, -1 - steps, -1):
                if i + j < 0:
                    break

                x[j] = curve[i + j]

            xs.append(x)
            # we're trying to forecast current point in the curve
            ys.append(numpy.array(curve[i]))

    print(f'Generated {len(xs)} observations.')
    return numpy.stack(xs), numpy.stack(ys)


def train(xs, ys, steps, hidden_size, epochs, name):
    input = Input(shape=(steps, 1))
    lstm = LSTM(hidden_size, return_sequences=True)(input)
    lstm = LSTM(hidden_size)(lstm)
    output = Dense(1)(lstm)
    model = Model(inputs=input, outputs=output)

    model.summary()
    model.compile(optimizer='adam', loss='mae', metrics=["accuracy"])

    model.fit(
        xs, ys, batch_size=4, epochs=epochs,
        callbacks=[
            ModelCheckpoint(
                monitor='loss',
                mode='min',
                save_best_only=True,
                filepath=os.path.join(f'models/{name}.hdf5'),
                verbose=1
            )
        ]
    )


STEPS = 14
xs, ys = generate_observations(
    'datasets/epidemic_curves.csv',
    STEPS,
    21,
    200
)
train(xs, ys, STEPS, 32, 500, '21days_200cases_14steps_32hidden')
