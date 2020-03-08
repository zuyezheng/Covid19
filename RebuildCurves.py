import datetime
import pandas
import math


def build_curve(rows, date_format, name, compute_delta=True):
    curve = []
    start_date = None
    last_index = 0
    last_value = 0
    zeros = 0

    for _, row in rows.iterrows():
        if start_date is None:
            start_date = datetime.datetime.strptime(row['Date'], date_format).date()
            delta = 0
        else:
            delta = row['Cases']
            if compute_delta:
                delta -= last_value

        if delta <= 0:
            delta = 0
            zeros += 1

        index = (datetime.datetime.strptime(row['Date'], date_format).date() - start_date).days
        last_value = row['Cases']

        # skip in the data fill distribute the delta
        if index - last_index > 1:
            distribution = math.floor(delta / (index - last_index))

            for i in range(last_index, index - 1):
                curve.append(distribution)

                if distribution == 0:
                    zeros += 1

            curve.append(delta - (distribution * (index - last_index - 1)))
        else:
            curve.append(delta)

        last_index = index

    # strip any leading or trailing zeros
    start = 0
    for i in range(len(curve)):
        if curve[i] > 0:
            start = i
            break
    end = 0
    for i in range(len(curve) - 1, 0, -1):
        if curve[i] > 0:
            end = i
            break

    curve = curve[start:end + 1]
    return list(map(lambda v: [name, v[0], v[1]], enumerate(curve)))


def build_aggregate_curve(dataset, date_format, name):
    aggregate = dict()

    for _, row in dataset.iterrows():
        date = datetime.datetime.strptime(row['Date'], date_format).date()
        if date in aggregate:
            aggregate[date] += row['Cases']
        else:
            aggregate[date] = row['Cases']

    aggregate_rows = []
    for date in aggregate:
        aggregate_rows.append([date.strftime(date_format), aggregate[date]])

    aggregate_df = pandas.DataFrame(
        aggregate_rows,
        columns=['Date', 'Cases']
    )

    return build_curve(aggregate_df, date_format, name)


def process(path, date_format, name):
    dataset = pandas.read_csv(path)

    curves = build_aggregate_curve(dataset, date_format, name)

    for country in dataset['Country'].unique():
        country_rows = dataset[dataset['Country'] == country]

        if country_rows.shape[0] > 3:
            curve = build_curve(country_rows, date_format, name + '_' + country)

            if len(curve) > 0:
                curves += curve

    return curves


pandas.DataFrame(
    process('curves/H1N1_2009.csv', '%m/%d/%Y', 'h1n1_2009') +
    process('curves/SARS_2003.csv', '%Y-%m-%d', 'sars_2003') +
    process('curves/covid_2019.csv', '%m-%d-%Y', 'covid_2019') +
    build_curve(pandas.read_csv('curves/english_flu_1978.csv'), '%Y-%m-%d', 'english_flu_1978') +
    build_curve(pandas.read_csv('curves/zika_girardot_2015.csv'), '%Y-%m-%d', 'zika_girardot_2015', False) +
    build_curve(pandas.read_csv('curves/zika_sanandres_2015.csv'), '%Y-%m-%d', 'zika_sanandres_2015', False) +
    build_curve(pandas.read_csv('curves/zika_yap_2007.csv'), '%Y-%m-%d', 'zika_yap_2007', False) +
    build_curve(pandas.read_csv('curves/dengue_fais_2011.csv'), '%Y-%m-%d', 'dengue_fais_2011', False) +
    build_curve(pandas.read_csv('curves/dengue_yap_2011.csv'), '%Y-%m-%d', 'dengue_yap_2011', False) +
    build_aggregate_curve(pandas.read_csv('curves/ebola_sierraleone_2014.csv'), '%Y-%m-%d', 'ebola_sierraleone_2014'),
    columns=['Name', 'Index', 'Cases']
).to_csv('datasets/epidemic_curves.csv', index=False)
