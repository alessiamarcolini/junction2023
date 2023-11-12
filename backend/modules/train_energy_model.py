# %%
import pickle
import warnings
from datetime import datetime
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, HoverTool
from bokeh.palettes import Category10
from bokeh.plotting import figure
from bokeh.resources import CDN
from dateutil.relativedelta import relativedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import (
    RandomizedSearchCV,
    TimeSeriesSplit,
    train_test_split,
)
from sklearn.preprocessing import OrdinalEncoder

warnings.filterwarnings(action="ignore")


def _season_from_month(month):
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"


def _lag_column(df, column, horizon: int, lags=list[int]):
    for lag in lags:
        delay = lag + horizon
        new_column_name = column + "_t-" + str(lag)
        df[new_column_name] = df[column].shift(delay * 24)
    return df


def _preprocess_data(
    data: pd.DataFrame,
    horizon: int | None = None,
    lags: list[int] | None = None,
    target: str = "price_actual",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    # Rename columns by replacing all - or blank space with _
    data.columns = data.columns.str.replace(" ", "_").str.replace("-", "_")

    data.sort_index(inplace=True)

    # Make the index DT
    data.index = pd.to_datetime(data.index, utc=True)

    # Drop columns with more than 95% missing values
    data = data.loc[:, data.isnull().sum() / len(data) * 100 < 0.95]

    data.drop(
        columns=[
            "price_day_ahead",
            "generation_marine",
            "generation_fossil_coal_derived_gas",
            "generation_fossil_oil_shale",
            "generation_fossil_peat",
            "generation_geothermal",
            "generation_geothermal",
            "total_load_forecast",
        ],
        inplace=True,
    )

    # Create column in dataframe that inputs the season based on the conditions created above
    data["season"] = data.apply(lambda x: _season_from_month(x.name.month), axis=1)

    if lags and horizon:
        for column in data.columns:
            data = _lag_column(data, column, horizon=horizon, lags=lags)
            if column != target and column != "season":
                data.drop(columns=column, inplace=True)

    y, X = data[target], data.drop(columns=target)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )

    features_names = X_train.columns
    ordinal_encoder = OrdinalEncoder()
    ordinal_encoder = ordinal_encoder.fit(X_train[["season"]])
    X_train["season"] = ordinal_encoder.transform(X_train[["season"]])
    X_val["season"] = ordinal_encoder.transform(X_val[["season"]])

    if lags:
        for lag in lags:
            ordinal_encoder = ordinal_encoder.fit(X_train[[f"season_t-{lag}"]])
            X_train[f"season_t-{lag}"] = ordinal_encoder.transform(
                X_train[[f"season_t-{lag}"]]
            )
            X_val[f"season_t-{lag}"] = ordinal_encoder.transform(
                X_val[[f"season_t-{lag}"]]
            )
            # X_train.drop(columns=[f"season"], inplace=True)
            # X_val.drop(columns=[f"season"], inplace=True)

    simp = SimpleImputer(strategy="mean")
    simp = simp.fit(X_train)
    X_train = simp.transform(X_train)
    X_val = simp.transform(X_val)
    return X_train, X_val, y_train, y_val, features_names


def _check_metrics(model, X_train, X_val, y_train, y_val):
    print(model)
    print("===================================================================")
    print("Training MAE:", mean_absolute_error(y_train, model.predict(X_train)))
    print("-------------------------------------------------------------------")
    print("Validation MAE:", mean_absolute_error(y_val, model.predict(X_val)))
    print("-------------------------------------------------------------------")
    print("Validation R2 score:", model.score(X_val, y_val))
    print("===================================================================")


def _train_model(
    X_train, y_train, X_val, y_val, mode: Literal["random_search", "best_params"]
):
    model_rfr = RandomForestRegressor()

    if mode == "random_search":
        params = {
            "max_depth": range(5, 35, 5),
            "n_estimators": range(25, 200, 10),
            "max_samples": np.arange(0.2, 1, 0.1),
            "max_features": ["sqrt", "log2"],
            "min_samples_split": np.arange(2, 5, 1),
        }
    elif mode == "best_params":
        params = {
            "n_estimators": [125],
            "min_samples_split": [4],
            "max_samples": [0.9],
            "max_features": ["sqrt"],
            "max_depth": [20],
        }

    tscv = TimeSeriesSplit(n_splits=2)

    model_rs_rfr = RandomizedSearchCV(
        model_rfr,
        param_distributions=params,
        n_iter=20,
        n_jobs=-1,
        random_state=42,
        cv=tscv,
    )

    model_rs_rfr.fit(X_train, y_train)

    print("Best params: ", model_rs_rfr.best_params_)

    _check_metrics(model_rs_rfr, X_train, X_val, y_train, y_val)

    return model_rs_rfr


def _plot_feature_importances(model, features_names, horizon: int | None = None):
    feature_importances = model.feature_importances_

    # Sort the features based on their importance
    sorted_idx = np.argsort(feature_importances)
    sorted_idx = sorted_idx[-10:]

    plt.figure(figsize=(10, 6))
    plt.barh(
        range(len(feature_importances[sorted_idx])), feature_importances[sorted_idx]
    )
    plt.yticks(
        range(len(feature_importances[sorted_idx])),
        np.array(features_names)[sorted_idx],
    )
    plt.xlabel("Feature Importance")
    plt.ylabel("Feature")
    plt.title("Random Forest Regressor - Feature Importances (top 10)")

    plt.savefig(f"feature_importances_horizon={horizon}.png", bbox_inches="tight")


def _save_model(model, features_names, last_date: str, horizon: int | None = None):
    Path("models/energy").mkdir(parents=True, exist_ok=True)
    with open(f"models/energy/energy_{last_date}_{horizon}.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(f"models/energy/feature_names_horizon={horizon}.pkl", "wb") as f:
        pickle.dump(features_names, f)


def predict(model, data, horizon: int | None = None, lags: list[int] | None = None):
    X_train, X_val, _, _, _ = _preprocess_data(
        data, horizon=horizon, lags=[l - 1 for l in lags]
    )
    data_concat = np.concatenate([X_train, X_val])
    features = data_concat[-1, :].reshape(1, -1)
    return model.predict(features)


def _save_data_for_predictions(data: pd.DataFrame, horizon: int, lags: list[int]):
    X_train, X_val, _, _, _ = _preprocess_data(
        data, horizon=horizon, lags=[l - 1 for l in lags]
    )
    data_concat = np.concatenate([X_train, X_val])
    np.save(f"data/energy/data_preprocessed_horizon_{horizon}.npy", data_concat)


def train(
    horizon: int,
    data_path: str = Path(__file__).parent.parent.parent / "data/energy/dataset.csv",
):
    data = pd.read_csv(
        data_path,
        parse_dates=["time"],
        index_col="time",
    )
    last_date = data.index[-1].strftime("%Y-%m-%d")
    lags = [1, 2, 3]
    X_train, X_val, y_train, y_val, features_names = _preprocess_data(
        data, horizon=horizon, lags=lags
    )

    model = _train_model(X_train, y_train, X_val, y_val, mode="random_search")

    # _plot_feature_importances(model.best_estimator_, features_names, horizon=horizon)

    _save_model(
        model.best_estimator_, features_names, last_date=last_date, horizon=horizon
    )
    _save_data_for_predictions(data, horizon=horizon, lags=lags)
    return model.best_estimator_


def _calculate_raw_feature_importances(model, features_names, top_k_features=3):
    feature_importances = model.feature_importances_

    sorted_idx = np.argsort(feature_importances)[::-1]
    top_feature_importances = feature_importances[sorted_idx]
    top_features_names = features_names[sorted_idx]

    only_top_per_category = {}
    counter = 0
    for feature_name, feature_importance in zip(
        top_features_names, top_feature_importances
    ):
        category = "_".join(feature_name.split("_")[:-1])
        if category not in only_top_per_category:
            only_top_per_category[category] = (feature_name, feature_importance)
            counter += 1
        if counter == top_k_features:
            break

    return only_top_per_category


def _zip_string(arr1, arr2):
    return (
        "\n".join([f"{arr1[i]}: {round(arr2[i],6)}" for i in range(len(arr1))]) + "\n"
    )


def _generate_upcoming_days(start_date, n):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    upcoming_days = []

    for i in range(n):
        next_day = start_date + relativedelta(days=1)
        upcoming_days.append(next_day.strftime("%Y-%m-%d"))
        start_date = next_day

    return upcoming_days


def _formulate_explanation_string(
    feature_importances: dict[str, tuple[str, float]],
    predictions: np.ndarray,
    horizon: int,
    last_date: str,
    latest_horizon_target_values: np.array,
) -> str:
    data_explanation = ""
    data_explanation += (
        f"The model made the following predictions for the next {horizon} days:\n"
    )
    predicted_days = _generate_upcoming_days(last_date, horizon)
    data_explanation += _zip_string(predicted_days, predictions)

    data_explanation += f"The previous {horizon} days had the following values:\n"

    latest_horizon_target_values = latest_horizon_target_values.reset_index()
    latest_horizon_target_values["time"] = pd.to_datetime(latest_horizon_target_values[
        "time"
    ], utc=True).dt.strftime("%Y-%m-%d")

    data_explanation += _zip_string(
        latest_horizon_target_values["time"],
        latest_horizon_target_values["price actual"],
    )

    data_explanation += (
        "The model used the following features with the respective importances:\n"
    )
    feat_names = [name for name, _ in feature_importances.values()]
    feat_importance = [importance for _, importance in feature_importances.values()]
    data_explanation += _zip_string(feat_names, feat_importance)

    # TODO: this will not report the correct features if the model is trained with a
    # different horizon and the importances change

    data_explanation += (
        "where, \n- the feature 'price_actual_t-X' "
        "means the actual price from X days before.\n"
        "- the feature 'generation_fossil_hard_coal' represents the coal generation in MW,\n"
        "- the feature 'generation_fossil_brown_coal/lignite' represents the coal/lignite generation in MW.\n"
    )

    plot_html_str = plot_trend(
        previous_data=latest_horizon_target_values,
        predicted_data=predictions,
        horizon=horizon,
        last_date=last_date,
    )

    return data_explanation, plot_html_str


def plot_trend(previous_data, predicted_data, horizon, last_date):
    predicted_days = _generate_upcoming_days(last_date, horizon)

    # Sample Data
    past_data = {
        "time": np.array(previous_data["time"]),
        "price": np.array(previous_data["price actual"]),
    }
    last_date = str(previous_data["time"].max())
    print(last_date)
    forecast_data = {
        "time": predicted_days,
        "price": predicted_data,
    }

    past_df = pd.DataFrame(past_data)
    past_df["time"] = pd.to_datetime(past_df["time"])
    forecast_df = pd.DataFrame(forecast_data)
    forecast_df["time"] = pd.to_datetime(forecast_df["time"])
    # Create Bokeh plot
    p = figure(
        title="Energy Price Forecast",
        x_axis_label="Date",
        y_axis_label="Energy price [EUR/MWh]",
        width=480,
        height=480,
    )
    p.xaxis.major_label_orientation = 45

    source_forecast = ColumnDataSource(forecast_df)
    forecast_dots = p.circle(
        x="time",
        y="price",
        size=10,
        color=Category10[3][1],
        legend_label="Forecast Data",
        source=source_forecast,
    )
    forecast_line = p.line(
        x="time",
        y="price",
        line_width=4,
        color=Category10[3][1],
        legend_label="Forecast Data",
        source=source_forecast,
    )
    p.line(
        pd.concat([past_df["time"].tail(1), forecast_df["time"].head(1)]),
        pd.concat([past_df["price"].tail(1), forecast_df["price"].head(1)]),
        line_width=4,
        color=Category10[3][1],
    )

    # Plot past data as dots
    source_past = ColumnDataSource(past_df)
    past_dots = p.circle(
        x="time",
        y="price",
        size=10,
        color=Category10[3][0],
        legend_label="Past Data",
        source=source_past,
    )
    past_line = p.line(
        x="time",
        y="price",
        color=Category10[3][0],
        legend_label="Past Data",
        source=source_past,
        line_width=4,
    )

    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [("time", "@time{%F}"), ("Price", "@price")]
    hover.formatters = {"@time": "datetime"}
    p.add_tools(hover)

    # Add labels and legend
    p.legend.location = "bottom_left"
    p.legend.click_policy = "hide"

    p.xaxis.formatter = DatetimeTickFormatter(
        days=["%d/%m/%Y"],
        months=["%d-%M-%Y"],
        years=["%d-%M-%Y"],
    )

    html_str = file_html(p, CDN)
    return html_str


def get_data_explanation(
    model,
    predictions: np.ndarray,
    features_names,
    horizon: int,
    last_date: str,
    latest_horizon_target_values: np.array,
    top_k_features=3,
):
    feature_importances = _calculate_raw_feature_importances(
        model, features_names, top_k_features=top_k_features
    )
    data_explanation = _formulate_explanation_string(
        feature_importances,
        predictions,
        horizon,
        last_date,
        latest_horizon_target_values,
    )

    return data_explanation


if __name__ == "__main__":
    horizon = 7
    model = train(horizon)
    # predicted_value = predict(model, data=data, horizon=horizon, lags=lags)
    # print(predicted_value)
