import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

from .module_base import ModuleBase
from .train_energy_model import get_data_explanation, train


class EnergyModule(ModuleBase):
    def _load_model(self, horizon: int) -> BaseEstimator:
        model_candidates = list(Path(f"models/energy").glob(f"energy_*_{horizon}.pkl"))
        # TODO: load the model with the latest timestamp, for now there is only one model
        if model_candidates:
            model_candidate = model_candidates[0]
            with open(model_candidate, "rb") as f:
                model = pickle.load(f)
        else:
            print(
                f"Energy model with horizon {horizon} does not exist. Training new model."
            )
            train(horizon)
            model, model_candidate = self._load_model(horizon)

        return model, model_candidate

    def execute(self, horizon: int):
        model, model_filename = self._load_model(horizon)
        self._data = np.load(f"data/energy/data_preprocessed_horizon_{horizon}.npy")

        features = self._data[-horizon:, :]
        predictions = model.predict(features)

        str_for_explanation = self._generate_str_for_explanation(
            horizon, model, predictions, model_filename
        )

        return str_for_explanation

    def _last_date(self, model_filename: Path) -> str:
        return model_filename.stem.split("_")[1]

    def _generate_str_for_explanation(
        self, horizon, model, predictions, model_filename
    ):
        with open(f"models/energy/feature_names_horizon={horizon}.pkl", "rb") as f:
            feature_names = pickle.load(f)

        data = pd.read_csv(
            Path(__file__).parent.parent.parent / "data/energy/dataset.csv",
            parse_dates=["time"],
            index_col="time",
        )
        # for now getting midnight values
        latest_horizon_target_values = data.iloc[-horizon * 24 :: 24]["price actual"]

        return get_data_explanation(
            model,
            predictions,
            feature_names,
            horizon,
            last_date=self._last_date(model_filename),
            latest_horizon_target_values=latest_horizon_target_values,
        )
