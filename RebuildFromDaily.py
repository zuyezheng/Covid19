import datetime
import pandas
import math
import os

start_date = datetime.date(2020, 1, 22)
last_metrics = dict()
rows = []
cumulative_rows = []


def value_or_default(row, column, default):
    value = row[column]

    if type(value) is not str and math.isnan(value):
        return default
    else:
        return value


def delta(key, status, new_value):
    if key not in last_metrics:
        return new_value

    if status not in last_metrics[key]:
        return new_value

    return new_value - last_metrics[key][status]


cur_date = start_date
while True:
    daily_path = 'COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/' + cur_date.strftime('%m-%d-%Y.csv')
    if not os.path.exists(daily_path):
        break

    csv = pandas.read_csv(daily_path)

    aggregate_by_country = dict()
    for _, row in csv.iterrows():

        state_maybe_with_city = value_or_default(row, 'Province/State', '_').split(',')

        state = ''
        city = '_'
        if len(state_maybe_with_city) > 1:
            city = state_maybe_with_city[0].strip()
            state = state_maybe_with_city[1].strip()
        else:
            state = state_maybe_with_city[0]

        country = row['Country/Region']
        if country == 'Mainland China':
            country = 'China'
        elif country == 'US':
            country = 'United States of America'

        key = country + '.' + value_or_default(row, 'Province/State', '_')

        row_metrics = dict()
        for status in ['Confirmed', 'Deaths', 'Recovered']:
            value = value_or_default(row, status, 0)
            delta_value = delta(key, status, value)

            if delta_value > 0:
                rows.append([
                    cur_date.strftime('%m-%d-%Y'),
                    country,
                    state,
                    city,
                    status,
                    delta_value
                ])

            row_metrics[status] = value

        last_metrics[key] = row_metrics

        if country in aggregate_by_country:
            aggregate_by_country[country] += row_metrics['Confirmed']
        else:
            aggregate_by_country[country] = row_metrics['Confirmed']

    for country in aggregate_by_country:
        cumulative_rows.append([
            cur_date.strftime('%m-%d-%Y'),
            country,
            aggregate_by_country[country]
        ])

    cur_date += datetime.timedelta(1)

pandas.DataFrame(
    rows,
    columns=['Date', 'Country', 'State', 'City', 'Status', 'Value']
).to_csv('datasets/covid19_details.csv', index=False)

pandas.DataFrame(
    cumulative_rows,
    columns=['Date', 'Country', 'Cases']
).to_csv('curves/covid_2019.csv', index=False)