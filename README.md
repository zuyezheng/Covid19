# Covid 19

Preps and processes the WHO daily reports from the Johns Hopkins CSSE repo. It builds a dataset that I think is better suited for analytics by computing daily deltas and pivoting the statuses from seperate columns to facts in a single column.

It also normalizes some of the variations in the data including changes to the country names and granularity from city for some countries to later state only.

It outputs 2 datasets, one for covid daily changes at the state level and another of epidemic curves for covid and others (SARS, H1N1, zika, ebola, etc) at the country level for comparison.

The CSSE repo is submoduled so it can be repulled and datasets rebuilt with RebuildFromDaily.py and RebuildCurves.py. Also started messing with forecasting using an LSTM trained on the dataset of past epidemic curves.
