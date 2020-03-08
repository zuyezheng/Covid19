import numpy
import pandas
import os

from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint

STEPS = 21


def build_observations():
    curves = pandas.read_csv('curves/curves.csv')
    curve_names = curves['name'].unique()

    xs = []
    ys = []
    for curve_name in curve_names:
        # get the values for the current curve and start at first non zero
        curve = curves[curves['name'] == curve_name]['cases']

        non_zeros = curve.where(curve != 0)
        for i in range(non_zeros.first_valid_index(), non_zeros.last_valid_index() + 1):
            # get the previous points in the curve as the xs
            x = numpy.zeros((STEPS, 1))
            for j in range(-1, -1 - STEPS, -1):
                if i + j < curve.index.min():
                    break

                x[j] = curve[i + j]

            xs.append(x)
            # current point in the curve is what we're trying to forecast
            ys.append(numpy.array(curve[i]))

    return numpy.stack(xs), numpy.stack(ys)


input = Input(shape=(STEPS, 1))
lstm = LSTM(8)(input)
output = Dense(1)(lstm)
model = Model(inputs=input, outputs=output)

model.summary()
model.compile(optimizer='adam', loss='mae', metrics=["accuracy", "mae"])

xs, ys = build_observations()
print("Training with samples of shape:", xs.shape)
model.fit(
    xs, ys, batch_size=16, epochs=200,
    callbacks=[
        ModelCheckpoint(
            monitor='accuracy',
            filepath=os.path.join('models/m-{epoch:03d}-{accuracy:.2f}.hdf5'),
            verbose=1
        )
    ]
)