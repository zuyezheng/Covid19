import datetime
import pandas
import math
import os
import us

start_date = datetime.date(2020, 1, 22)

# need to compute daily changes since daily reports are cumulative
last_metrics = dict()

# rows by country and state with status
rows = []
# rows by country with just confirmed for epidemic curves
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


def normalize_country_and_state(country, state):
    if country == 'Mainland China':
        country = 'China'
    elif country == 'US':
        country = 'United States of America'
        lookup = us.states.lookup(state)
        if lookup is None:
            state = state
        else:
            state = lookup.name
    elif country == 'Iran (Islamic Republic of)':
        country = 'Iran'
    elif country == 'Republic of Korea':
        country = 'South Korea'

    return [country, state]


def set_or_add_statuses(key, new_status, statuses):
    if key not in statuses:
        statuses[key] = new_status
    else:
        for status in ['Confirmed', 'Deaths', 'Recovered']:
            statuses[key][status] += new_status[status]


cur_date = start_date
while True:
    daily_path = 'COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/' + cur_date.strftime('%m-%d-%Y.csv')
    if not os.path.exists(daily_path):
        break

    csv = pandas.read_csv(daily_path)

    # rollup by country for epidemic curves dataset since state level is a little sparse
    aggregate_by_country = dict()

    # need to rollup by state as well since initial daily reports contained city granularity which was later dropped
    aggregate_by_country_and_state = dict()

    # process and rollup the rows
    for _, row in csv.iterrows():
        if cur_date >= datetime.date(2020, 3, 22):
            province_state_key = 'Province_State'
            country_key = 'Country_Region'
        else:
            province_state_key = 'Province/State'
            country_key = 'Country/Region'

        state_maybe_with_city = value_or_default(row, province_state_key, '_').split(',')

        # parse out the city
        state = ''
        city = '_'
        if len(state_maybe_with_city) > 1:
            city = state_maybe_with_city[0].strip()
            state = state_maybe_with_city[1].strip()
        else:
            state = state_maybe_with_city[0]

        # normalize values across daily updates and for mapping
        [country, state] = normalize_country_and_state(row[country_key], state)

        # rollup to state
        row_metrics = dict()
        for status in ['Confirmed', 'Deaths', 'Recovered']:
            row_metrics[status] = value_or_default(row, status, 0)

        set_or_add_statuses((country, state), row_metrics, aggregate_by_country_and_state)

        if country in aggregate_by_country:
            aggregate_by_country[country] += row_metrics['Confirmed']
        else:
            aggregate_by_country[country] = row_metrics['Confirmed']

    # compute deltas and produce daily rows
    for country_state in aggregate_by_country_and_state:
        statuses = aggregate_by_country_and_state[country_state]
        for status in ['Confirmed', 'Deaths', 'Recovered']:
            delta_value = delta(country_state, status, statuses[status])

            if delta_value > 0:
                rows.append([
                    cur_date.strftime('%m-%d-%Y'),
                    country_state[0],
                    country_state[1],
                    status,
                    delta_value
                ])

        # populate last metrics by key vs full replace handle if a country_state is not reported for a day(s)
        last_metrics[country_state] = aggregate_by_country_and_state[country_state]

    for country in aggregate_by_country:
        cumulative_rows.append([
            cur_date.strftime('%m-%d-%Y'),
            country,
            aggregate_by_country[country]
        ])

    cur_date += datetime.timedelta(1)

pandas.DataFrame(
    rows,
    columns=['Date', 'Country', 'State', 'Status', 'Value']
).to_csv('datasets/covid19_details.csv', index=False)

pandas.DataFrame(
    cumulative_rows,
    columns=['Date', 'Country', 'Cases']
).to_csv('curves/covid_2019.csv', index=False)