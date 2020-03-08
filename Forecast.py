import numpy
import pandas
import tensorflow

model = tensorflow.keras.models.load_model('models/m-gt14_14_16_16.hdf5')

model.summary()

def forecast(steps, n):
    forecasted = [15.0, 15.0, 15.0, 15.0, 15.0, 35.0, 35.0, 35.0, 53.0, 53.0, 59.0, 60.0, 62.0, 70.0]

    for i in range(n):
        input = numpy.zeros((1, steps, 1))
        for j in range(-1, -1 - min(len(forecasted), steps), -1):
            input[0][steps + j] = forecasted[j]

        next = model.predict(input)[0][0]
        forecasted.append(next)

    return forecasted

print(forecast(14, 21))