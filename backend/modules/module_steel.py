import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from module_base import ModuleBase
from train_steel_model import train, formulate_explanation_string, create_lag_features_forecast, create_forecast_plot


class SteelModule(ModuleBase):
    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name
        self.target_column = "Germany_steel_index"
        self.feature_cols = ["Germany_electricity_index"]

    def _load_model(self, model_filename: str, horizon: int) -> BaseEstimator:
        model_path = f"..//..//models/steel/{model_filename}.pkl"
        if Path(model_path).exists():
            with open(Path(model_path), "rb") as f:
                model = pickle.load(f)
        else:
            print(
                f"Model {model_filename} does not exist. Training new model."
            )
            model = train(self.data, self.target_column, self.feature_cols, horizon=horizon)
            with open(model_path, 'wb') as file:
                pickle.dump(model, file)
        return model
    
    def _load_data(self, ):
        input_folder = "../..//data"
        df = pd.read_csv(Path(f"{input_folder}/processed_steel_data.csv"))
        df_electricity = pd.read_csv(Path(f"{input_folder}/processed_eletricity_price_index.csv"))

        new_column_names = {col: f"{col}_steel_index" for col in df.columns if col != "time"}
        df = df.rename(columns=new_column_names)


        new_column_names = {col: f"{col}_electricity_index" for col in df_electricity.columns if col != "time"}
        df_electricity = df_electricity.rename(columns=new_column_names)

        df["time"] = df["time"].apply(lambda x: f"{x}-01")
        df_electricity["time"] = df_electricity["time"].apply(lambda x: f"{x}-01")


        df = pd.merge(df, df_electricity, on="time", how="left")
        df = df.replace(':', method='ffill')

        return df.tail(36), self.model_name

    def execute(self, horizon: int) -> str:
        self.data, self.data_name = self._load_data()

        last_date = self.data["time"].max()
        model_filename = f"{self.data_name}-{last_date}-{horizon}.pkl"

        model = self._load_model(model_filename, horizon)

            
        forecast_features = create_lag_features_forecast(self.data, [self.target_column]+self.feature_cols).tail(horizon)
        
        last_label_data = self.data[["time", self.target_column]].tail(horizon)
        model_result_text = formulate_explanation_string(model, forecast_features, last_date, horizon, last_label_data)        

        plot_str = create_forecast_plot(self.data, model.predict(forecast_features))
        print(plot_str)

        return model_result_text, plot_str
    

if __name__ == "__main__":
    module = SteelModule("steel")
    reason, plot = module.execute(horizon=3)
    print(reason)
    print(plot)