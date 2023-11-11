from datetime import datetime

import numpy as np
import pandas as pd
from bokeh.embed import file_html
from bokeh.resources import CDN
from dateutil.relativedelta import relativedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


def zip_string(arr1, arr2):
    return "\n" + "\n".join([f"{arr1[i]}: {arr2[i]}" for i in range(len(arr1))]) + "\n"


def generate_upcoming_months(start_date, n):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    upcoming_months = []

    for i in range(n):
        next_month = start_date + relativedelta(months=1)
        upcoming_months.append(next_month.strftime("%Y-%m-%d"))
        start_date = next_month

    return upcoming_months


def create_lag_features(data, label_column, feature_cols, horizon=3, lags=[1, 2, 3]):
    """
    Generate lagged features for time-series data training.

    Parameters:
    - data (pd.DataFrame): The input DataFrame containing time-series data.
    - label_column (str): The name of the column to be used as the target variable.
    - feature_cols (list): List of column names to create lagged features for.
    - horizon (int, optional): The time horizon for predicting the target variable in future periods. Default is 3.
    - lags (list, optional): List of time lags to create features for. Default is [1, 2, 3].

    Returns:
    pd.DataFrame: A new DataFrame with lagged features created for the specified columns.
    """
    data_lagged = data.copy()

    delayed_cols = []
    for feature in feature_cols:
        for i in lags:
            col_name = f"{feature}_t-{i-1}"
            delay = i + horizon
            data_lagged[col_name] = data[feature].shift(delay)
            delayed_cols.append(col_name)

    data_lagged["target"] = data_lagged[label_column].shift(horizon)
    delayed_cols.append("target")

    return data_lagged[delayed_cols].dropna()


def create_lag_features_forecast(data, feature_cols, lags=[0, 1, 2]):
    """
    Generate lagged features for time-series data forecasting.

    Parameters:
    - data (pd.DataFrame): The input DataFrame containing time-series data.riable.
    - feature_cols (list): List of column names to create lagged features for.
    - lags (list, optional): List of time lags to create features for. Default is [1, 2, 3].

    Returns:
    pd.DataFrame: A new DataFrame with lagged features created for the specified columns.
    """
    data_lagged = data.copy()

    delayed_cols = []
    for feature in feature_cols:
        for i in lags:
            col_name = f"{feature}_t-{i}"
            data_lagged[col_name] = data[feature].shift(i)
            delayed_cols.append(col_name)

    return data_lagged[delayed_cols].dropna()


def train(
    data,
    target_column: str,
    feature_cols: list,
    horizon=3,
    n_estimators=100,
    max_depth=None,
    random_state=42,
):
    data = data.drop("time", axis=1)

    # Create lag features
    lagged_data = create_lag_features(
        data,
        label_column=[target_column],
        feature_cols=[target_column] + feature_cols,
        horizon=3,
        lags=[1, 2, 3],
    )  #

    # Split the data into train and test sets
    train_data, test_data = lagged_data[:-horizon], lagged_data[-horizon:]

    # Prepare features and target variables
    y_train = train_data["target"]
    X_train = train_data.drop("target", axis=1)

    y_test = test_data["target"]
    X_test = test_data.drop("target", axis=1)

    # Create and train the Random Forest model
    model = RandomForestRegressor(
        n_estimators=n_estimators, max_depth=max_depth, random_state=random_state
    )
    model.fit(X_train, y_train)

    # Make predictions on the test set
    predictions = model.predict(X_test)

    # Evaluate the model
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print("Training completed!")
    print(f"Root Mean Squared Error on Test Set: {rmse}")

    return model


def formulate_explanation_string(
    model, forecast_features, last_date, horizon, last_label_data
):
    feat_names = model.feature_names_in_
    feat_importance = model.feature_importances_

    predictions = model.predict(forecast_features)
    pred_dates = generate_upcoming_months(last_date, horizon)

    data_explanation = ""
    data_explanation += (
        f"The model made the following predictions for the next {horizon} months:"
    )
    data_explanation += zip_string(pred_dates, predictions)
    data_explanation += "\n"

    data_explanation += f"The previous {horizon} months had the following values:"
    data_explanation += zip_string(
        np.array(last_label_data.iloc[:, 0]), np.array(last_label_data.iloc[:, 1])
    )
    data_explanation += "\n"

    data_explanation += (
        "The model used the following features with the respective importances:"
    )
    data_explanation += zip_string(feat_names, feat_importance)
    data_explanation += "\n"

    data_explanation += "Short-term business statistics (STS) provide index data on various economic activities. Percentage changes,\n"
    data_explanation += "The column Germany_steel_index represents the STS for Basic iron and steel and ferro-alloys\n"
    data_explanation += (
        "The column Germany_electricity_index represents the STS for Electricity\n"
    )
    data_explanation += "The t-x where x represents the delay in the features e-g t-1 represents the previous months data in the given column\n"

    return data_explanation


from datetime import datetime

import pandas as pd
from bokeh.embed import file_html
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Category10
from bokeh.plotting import figure, show
from bokeh.resources import CDN


def create_forecast_plot(past_df, predictions, past_target_col="Germany_steel_index"):
    # Sample Data
    past_data = {
        "time": np.array(past_df["time"]),
        "Germany_steel_index": np.array(past_df[past_target_col]),
    }
    last_date = str(past_df["time"].max())
    print(last_date)
    forecast_data = {
        "time": generate_upcoming_months(last_date, 3),
        "Germany_steel_index": predictions,
    }

    # past_df = pd.DataFrame(past_data)
    past_df = past_df.tail(11)
    past_df["time"] = pd.to_datetime(past_df["time"])
    forecast_df = pd.DataFrame(forecast_data)
    forecast_df["time"] = pd.to_datetime(forecast_df["time"])
    # Create Bokeh plot
    # Create Bokeh plot
    p = figure(
        title="Short-term Business Statistics - Steel Index",
        x_axis_label="time",
        y_axis_label="Index Value",
        x_axis_type="datetime",
        width=480,
        height=480,
    )
    p.title.text_font_size = "18pt"

    source_forecast = ColumnDataSource(forecast_df)
    forecast_dots = p.circle(
        x="time",
        y="Germany_steel_index",
        size=10,
        color=Category10[3][1],
        legend_label="Forecast Data",
        source=source_forecast,
    )
    forecast_line = p.line(
        x="time",
        y="Germany_steel_index",
        line_width=4,
        color=Category10[3][1],
        legend_label="Forecast Data",
        source=source_forecast,
    )
    p.line(
        pd.concat([past_df["time"].tail(1), forecast_df["time"].head(1)]),
        pd.concat(
            [
                past_df["Germany_steel_index"].tail(1),
                forecast_df["Germany_steel_index"].head(1),
            ]
        ),
        line_width=4,
        color=Category10[3][1],
    )

    # Plot past data as dots
    source_past = ColumnDataSource(past_df)
    past_dots = p.circle(
        x="time",
        y="Germany_steel_index",
        size=10,
        color=Category10[3][0],
        legend_label="Past Data",
        source=source_past,
    )
    past_line = p.line(
        x="time",
        y="Germany_steel_index",
        color=Category10[3][0],
        legend_label="Past Data",
        source=source_past,
        line_width=4,
    )

    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [("time", "@time{%F}"), ("Index Value", "@Germany_steel_index")]
    hover.formatters = {"@time": "datetime"}
    p.add_tools(hover)

    # Add labels and legend
    p.legend.location = "bottom_left"
    p.legend.click_policy = "hide"
    html = file_html(p, CDN)

    return html
