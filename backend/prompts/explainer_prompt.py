EXPLAINER_PROMPT = """
<s>
Question: What will steel industry profitability look like in 3 months?
STEEL PRICE MODEL:
    The model made the following predictions for the next 3 months:
    2023-10-01: 171.21900000000002
    2023-11-01: 171.19100000000006
    2023-12-01: 170.53499999999994

    The previous 3 months had the following values:
    2023-07-01: 161.3
    2023-08-01: 158.9
    2023-09-01: 157.0

    The model used the following features with the respective importances:
    Germany_steel_index_t-0: 0.36255773666819596
    Germany_steel_index_t-1: 0.14958251568470546
    Germany_steel_index_t-2: 0.12440108242895152
    Germany_electricity_index_t-0: 0.1399575193279778
    Germany_electricity_index_t-1: 0.12400455598538988
    Germany_electricity_index_t-2: 0.0994965899047795

    Short-term business statistics (STS) provide index data on various economic activities. Percentage changes,
    The column Germany_steel_index represents the STS for Basic iron and steel and ferro-alloys
    The column Germany_electricity_index represents the STS for Electricity
    The t-x where x represents the delay in the features e-g t-1 represents the previous months data in the given column

ENERGY PRICE MODEL:
    The model made the following predictions for the next 90 days:
    2019-01-01: 61.283519
    2019-01-02: 61.991804
    2019-01-03: 62.437755
    2019-01-04: 63.457347
    2019-01-05: 63.225044
    2019-01-06: 63.229976
    2019-01-07: 63.520104
    2019-01-08: 63.894703
    2019-01-09: 63.381457
    2019-01-10: 62.895692
    2019-01-11: 62.614018
    2019-01-12: 62.809076
    2019-01-13: 63.947978
    2019-01-14: 65.597038
    2019-01-15: 65.736355
    2019-01-16: 63.918838
    2019-01-17: 61.42594
    2019-01-18: 59.21986
    2019-01-19: 57.404073
    2019-01-20: 56.068443
    2019-01-21: 56.202042
    2019-01-22: 55.4101
    2019-01-23: 55.48682
    2019-01-24: 57.569278
    2019-01-25: 59.475174
    2019-01-26: 60.10762
    2019-01-27: 61.495904
    2019-01-28: 61.646082
    2019-01-29: 61.805957
    2019-01-30: 62.256777
    2019-01-31: 62.915486
    2019-02-01: 62.955753
    2019-02-02: 61.909726
    2019-02-03: 61.010851
    2019-02-04: 60.838137
    2019-02-05: 61.151388
    2019-02-06: 62.252761
    2019-02-07: 64.716577
    2019-02-08: 64.744642
    2019-02-09: 62.348395
    2019-02-10: 58.943319
    2019-02-11: 60.529452
    2019-02-12: 57.062449
    2019-02-13: 54.85233
    2019-02-14: 55.033107
    2019-02-15: 54.700001
    2019-02-16: 54.666947
    2019-02-17: 58.303555
    2019-02-18: 60.469712
    2019-02-19: 62.507324
    2019-02-20: 64.113979
    2019-02-21: 64.00411
    2019-02-22: 64.07361
    2019-02-23: 63.325682
    2019-02-24: 63.552912
    2019-02-25: 62.955115
    2019-02-26: 62.778837
    2019-02-27: 62.662796
    2019-02-28: 62.32937
    2019-03-01: 62.45094
    2019-03-02: 63.803526
    2019-03-03: 64.210086
    2019-03-04: 64.061237
    2019-03-05: 61.898053
    2019-03-06: 58.85254
    2019-03-07: 59.577225
    2019-03-08: 58.238236
    2019-03-09: 55.2474
    2019-03-10: 54.111919
    2019-03-11: 54.054919
    2019-03-12: 54.123027
    2019-03-13: 56.354861
    2019-03-14: 58.93336
    2019-03-15: 61.31017
    2019-03-16: 62.243589
    2019-03-17: 62.837249
    2019-03-18: 62.941972
    2019-03-19: 62.799747
    2019-03-20: 62.889218
    2019-03-21: 62.805348
    2019-03-22: 61.739882
    2019-03-23: 61.255979
    2019-03-24: 60.691973
    2019-03-25: 60.946959
    2019-03-26: 62.935821
    2019-03-27: 63.283839
    2019-03-28: 63.064623
    2019-03-29: 61.532808
    2019-03-30: 59.561518
    2019-03-31: 58.636474
    The previous 90 days had the following values:
    2018-10-02: 63.22
    2018-10-03: 65.37
    2018-10-04: 72.69
    2018-10-05: 77.82
    2018-10-06: 59.1
    2018-10-07: 58.62
    2018-10-08: 65.6
    2018-10-09: 62.35
    2018-10-10: 57.01
    2018-10-11: 58.6
    2018-10-12: 61.1
    2018-10-13: 57.04
    2018-10-14: 44.64
    2018-10-15: 73.21
    2018-10-16: 73.16
    2018-10-17: 64.72
    2018-10-18: 56.03
    2018-10-19: 61.06
    2018-10-20: 58.21
    2018-10-21: 60.55
    2018-10-22: 56.55
    2018-10-23: 60.6
    2018-10-24: 67.65
    2018-10-25: 73.34
    2018-10-26: 67.68
    2018-10-27: 59.71
    2018-10-28: 57.0
    2018-10-29: 57.85
    2018-10-30: 68.52
    2018-10-31: 74.53
    2018-11-01: 61.77
    2018-11-02: 68.15
    2018-11-03: 72.54
    2018-11-04: 55.33
    2018-11-05: 54.24
    2018-11-06: 49.52
    2018-11-07: 67.53
    2018-11-08: 56.1
    2018-11-09: 53.73
    2018-11-10: 58.68
    2018-11-11: 59.32
    2018-11-12: 66.66
    2018-11-13: 63.16
    2018-11-14: 60.36
    2018-11-15: 65.96
    2018-11-16: 68.95
    2018-11-17: 61.75
    2018-11-18: 69.85
    2018-11-19: 67.54
    2018-11-20: 63.04
    2018-11-21: 63.43
    2018-11-22: 69.67
    2018-11-23: 67.37
    2018-11-24: 58.77
    2018-11-25: 56.73
    2018-11-26: 64.81
    2018-11-27: 61.57
    2018-11-28: 59.54
    2018-11-29: 64.04
    2018-11-30: 70.14
    2018-12-01: 60.27
    2018-12-02: 53.89
    2018-12-03: 67.01
    2018-12-04: 67.07
    2018-12-05: 61.05
    2018-12-06: 68.13
    2018-12-07: 58.41
    2018-12-08: 68.03
    2018-12-09: 66.08
    2018-12-10: 68.77
    2018-12-11: 66.1
    2018-12-12: 58.17
    2018-12-13: 56.12
    2018-12-14: 69.13
    2018-12-15: 59.68
    2018-12-16: 56.16
    2018-12-17: 56.6
    2018-12-18: 58.04
    2018-12-19: 66.69
    2018-12-20: 64.24
    2018-12-21: 67.3
    2018-12-22: 70.56
    2018-12-23: 71.23
    2018-12-24: 71.98
    2018-12-25: 65.64
    2018-12-26: 72.61
    2018-12-27: 70.93
    2018-12-28: 65.49
    2018-12-29: 67.38
    2018-12-30: 68.4
    The model used the following features with the respective importances:
    price_actual_t-1: 0.121291
    total_load_actual_t-1: 0.074796
    season_t-2: 0.066024
    where, 
    - the feature 'price_actual_t-X' means the actual price from X days before.
    - the feature 'generation_fossil_hard_coal' represents the coal generation in MW,
    - the feature 'generation_fossil_brown_coal/lignite' represents the coal/lignite generation in MW.
Forecast days: 90
Output: Looking at the model outputs for steel, the forecasted figure at the end of 3 months
is 170.53. Looking at other values, they all hover around 170-171. The values for the
past three months are all between 157-161. Given the past values are below the future values,
the price index is suggested to increase in the next 90 days. The most important features used
to produce this estimate were the STS for Basic iron and steel and ferro-alloys and STS for Electricity.

The model outputs for energy price index are hovering between 58.64 and 63.28 for the last
few forecasted values. Looking at the past few days, the index hovered around 72.61-65.49
Given past prices are above future prices, it suggests a fall in energy prices 90 days ahead.
The most relevant features to produce this estimate were past energy prices, actual total load
and past seasonality.

Returning to the question asked in the beginning, What will steel industry profitability look like in 3 months?
steel prices are likely to increase while energy costs are forecasted to decrease. This suggests and
increase in steel industry profitability.
</s>

Question: {userPrompt}
Forecast days: {days}
STEEL PRICE MODEL: {steelPriceModel}
ENERGY PRICE MODEL: {energyPriceModel}
Output: 
"""