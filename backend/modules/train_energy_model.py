# %%
import pickle
import warnings
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
        new_column_name = column + "_lag" + str(delay)
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
            delay = lag + horizon
            ordinal_encoder = ordinal_encoder.fit(X_train[[f"season_lag{delay}"]])
            X_train[f"season_lag{delay}"] = ordinal_encoder.transform(
                X_train[[f"season_lag{delay}"]]
            )
            X_val[f"season_lag{delay}"] = ordinal_encoder.transform(
                X_val[[f"season_lag{delay}"]]
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


def _save_model(model, features_names, horizon: int | None = None):
    Path("models/energy").mkdir(parents=True, exist_ok=True)
    with open(f"models/energy/model_horizon={horizon}.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(f"models/energy/features_names_horizon={horizon}.pkl", "wb") as f:
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
    lags = [1, 2, 3]
    X_train, X_val, y_train, y_val, features_names = _preprocess_data(
        data, horizon=horizon, lags=lags
    )

    model = _train_model(X_train, y_train, X_val, y_val, mode="random_search")

    # _plot_feature_importances(model.best_estimator_, features_names, horizon=horizon)

    _save_model(model.best_estimator_, features_names, horizon=horizon)
    _save_data_for_predictions(data, horizon=horizon, lags=lags)
    return model


if __name__ == "__main__":
    horizon = 7
    model = train(horizon)
    # predicted_value = predict(model, data=data, horizon=horizon, lags=lags)
    # print(predicted_value)