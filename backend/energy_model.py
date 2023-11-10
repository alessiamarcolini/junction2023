# %%
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.preprocessing import OrdinalEncoder

data = pd.read_csv(
    Path(__file__).parent.parent / "data/energy_dataset.csv",
    parse_dates=["time"],
    index_col="time",
)

lag = True

# %%

# Rename columns by replacing all - or blank space with _
data.columns = data.columns.str.replace(" ", "_").str.replace("-", "_")

# Make the index DT
data.index = pd.to_datetime(data.index, utc=True)

# %%
# Drop columns with more than 95% missing values
data = data.loc[:, data.isnull().sum() / len(data) * 100 < 0.95]

# %%
# Correlation of columns to target variable
correlations = data.corr(method="pearson")
# %%
correlations["price_actual"].sort_values(ascending=False)

# %%
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

# Set conditional statements for filtering times of month to season value


def season_from_month(month):
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"


# Create column in dataframe that inputs the season based on the conditions created above
data["season"] = data.apply(lambda x: season_from_month(x.name.month), axis=1)


# %%
def lag_column(df, column, lag):
    for i in range(1, lag + 1):
        new_column_name = column + "_lag" + str(i)
        df[new_column_name] = df[column].shift(i * 24)
    return df


if lag:
    for column in data.columns:
        data = lag_column(data, column, 7)

# %%
target = "price_actual"

y, X = data[target], data.drop(columns=target)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

print("finished preprocessing")

features_names = X_train.columns
# %%
ordinal_encoder = OrdinalEncoder()
ordinal_encoder = ordinal_encoder.fit(X_train[["season"]])
X_train["season"] = ordinal_encoder.transform(X_train[["season"]])
X_val["season"] = ordinal_encoder.transform(X_val[["season"]])

if lag:
    for i in range(1, 8):
        ordinal_encoder = ordinal_encoder.fit(X_train[[f"season_lag{i}"]])
        X_train[f"season_lag{i}"] = ordinal_encoder.transform(
            X_train[[f"season_lag{i}"]]
        )
        X_val[f"season_lag{i}"] = ordinal_encoder.transform(X_val[[f"season_lag{i}"]])


simp = SimpleImputer(strategy="mean")
simp_fit = simp.fit(X_train)
X_train = simp.transform(X_train)
X_val = simp.transform(X_val)


# %%

# %%
model_rfr = RandomForestRegressor()


# %%
def check_metrics(model):
    print(model)
    print("===================================================================")
    print("Training MAE:", mean_absolute_error(y_train, model.predict(X_train)))
    print("-------------------------------------------------------------------")
    print("Validation MAE:", mean_absolute_error(y_val, model.predict(X_val)))
    print("-------------------------------------------------------------------")
    print("Validation R2 score:", model.score(X_val, y_val))
    print("===================================================================")


# %%
if lag:
    params = {
        "max_depth": range(5, 35, 5),
        "n_estimators": range(25, 200, 10),
        "max_samples": np.arange(0.2, 1, 0.1),
        "max_features": ["sqrt", "log2"],
        "min_samples_split": np.arange(2, 5, 1),
    }
else:
    params = {
        "n_estimators": [125],
        "min_samples_split": [4],
        "max_samples": [0.9],
        "max_features": ["sqrt"],
        "max_depth": [20],
    }

model_rs_rfr = RandomizedSearchCV(
    model_rfr, param_distributions=params, n_iter=20, n_jobs=-1
)

model_rs_rfr.fit(X_train, y_train)

check_metrics(model_rs_rfr)

print(model_rs_rfr.best_params_)

# %%
feature_importances = model_rs_rfr.best_estimator_.feature_importances_

# Sort the features based on their importance
sorted_idx = np.argsort(feature_importances)
sorted_idx = sorted_idx[-10:]
# %%
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.barh(range(len(feature_importances[sorted_idx])), feature_importances[sorted_idx])
plt.yticks(
    range(len(feature_importances[sorted_idx])), np.array(features_names)[sorted_idx]
)
plt.xlabel("Feature Importance")
plt.ylabel("Feature")
plt.title("Random Forest Regressor - Feature Importances (top 10)")
plt.savefig(f"feature_importances_lag={lag}.png", bbox_inches="tight")

# %%
