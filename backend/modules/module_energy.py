import pickle
from pathlib import Path

import numpy as np
from sklearn.base import BaseEstimator

from .module_base import ModuleBase
from .train_energy_model import train


class EnergyModule(ModuleBase):
    def _load_model(self, horizon: int) -> BaseEstimator:
        if Path(f"models/energy/model_horizon={horizon}.pkl").exists():
            with open(f"models/energy/model_horizon={horizon}.pkl", "rb") as f:
                model = pickle.load(f)
        else:
            print(
                f"Energy model with horizon {horizon} does not exist. Training new model."
            )
            model = train(horizon)
        return model

    def execute(self, horizon: int):
        model = self._load_model(horizon)
        self._data = np.load(f"data/energy/data_preprocessed_horizon_{horizon}.npy")

        features = self._data[-1, :].reshape(1, -1)
        prediction = model.predict(features)[0]
        return prediction
