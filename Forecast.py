import numpy
import pandas
import tensorflow

model = tensorflow.keras.models.load_model('models/21days_50cases_14steps_32hidden.hdf5')

model.summary()

def forecast(steps, n, actual):
    forecasted = actual.copy()

    for i in range(n):
        # build the input with as much information as possible
        input = numpy.zeros((1, steps, 1))
        for j in range(-1, -1 - min(len(forecasted), steps), -1):
            input[0][steps + j] = forecasted[j]

        next = model.predict(input)[0][0]
        forecasted.append(next)

    print(forecasted)

    return forecasted[len(actual):]


#def get_curve(name):



#curves = pandas.read_csv('datasets/epidemic_curves.csv')
#curves

print(forecast(14, 21, [20.0, 0.0, 0.0, 18.0, 0.0, 6.0, 1.0, 2.0, 8.0, 6.0, 25.0, 21.0, 31.0, 68.0, 57.0, 139.0]))