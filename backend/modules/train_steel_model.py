
from datetime import datetime
from dateutil.relativedelta import relativedelta


import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

def zip_string(arr1, arr2):
    return "\n"+"\n".join([f"{arr1[i]}: {arr2[i]}" for i in range(len(arr1))])+"\n"

def generate_upcoming_months(start_date, n):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    upcoming_months = []

    for i in range(n):
        next_month = start_date + relativedelta(months=1)
        upcoming_months.append(next_month.strftime("%Y-%m-%d"))
        start_date = next_month

    return upcoming_months

def create_lag_features(data,label_column, feature_cols, horizon=3,lags=[1,2,3]):
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
            col_name = f'{feature}_t-{i-1}'
            delay = i+horizon
            data_lagged[col_name] = data[feature].shift(delay)
            delayed_cols.append(col_name)

    data_lagged["target"] = data_lagged[label_column].shift(horizon)
    delayed_cols.append("target")

    return data_lagged[delayed_cols].dropna()

def create_lag_features_forecast(data, feature_cols, lags=[0,1,2]):
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
            col_name = f'{feature}_t-{i}'
            data_lagged[col_name] = data[feature].shift(i)
            delayed_cols.append(col_name)

    return data_lagged[delayed_cols].dropna()


def train(data, target_column: str, feature_cols: list, horizon=3, n_estimators=100, max_depth=None, random_state=42):
    data = data.drop("time", axis=1)

    # Create lag features
    lagged_data = create_lag_features(data, label_column=[target_column],feature_cols=[target_column]+feature_cols, horizon=3,lags=[1,2,3])# 

    
    # Split the data into train and test sets
    train_data, test_data = lagged_data[:-horizon], lagged_data[-horizon:]

    # Prepare features and target variables    
    y_train = train_data["target"]
    X_train = train_data.drop("target", axis=1)

    y_test = test_data["target"]
    X_test = test_data.drop("target", axis=1)
    
    
    # Create and train the Random Forest model
    model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)
    model.fit(X_train, y_train)
    
    # Make predictions on the test set
    predictions = model.predict(X_test)
    
    # Evaluate the model
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print("Training completed!")
    print(f'Root Mean Squared Error on Test Set: {rmse}')
    
    return model



def formulate_explanation_string(model, forecast_features, last_date, horizon, last_label_data):
    feat_names = model.feature_names_in_
    feat_importance = model.feature_importances_    


    predictions = model.predict(forecast_features)
    pred_dates = generate_upcoming_months(last_date, horizon)

    data_explanation = ""
    data_explanation += f"The model made the following predictions for the next {horizon} months:"
    data_explanation += zip_string(pred_dates, predictions)
    data_explanation += "\n"

    data_explanation += f"The previous {horizon} months had the following values:"
    data_explanation += zip_string(np.array(last_label_data.iloc[:, 0]), np.array(last_label_data.iloc[:, 1]))
    data_explanation += "\n"

    data_explanation += "The model used the following features with the respective importances:"
    data_explanation +=zip_string(feat_names, feat_importance)
    data_explanation += "\n"

    data_explanation += "Short-term business statistics (STS) provide index data on various economic activities. Percentage changes,\n"
    data_explanation += "The column Germany_steel_index represents the STS for Basic iron and steel and ferro-alloys\n"
    data_explanation += "The column Germany_electricity_index represents the STS for Electricity\n"
    data_explanation += "The t-x where x represents the delay in the features e-g t-1 represents the previous months data in the given column\n"

    return data_explanation