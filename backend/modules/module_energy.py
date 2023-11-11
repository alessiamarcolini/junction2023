import pickle
from pathlib import Path

import numpy as np
from sklearn.base import BaseEstimator

from .module_base import ModuleBase


class EnergyModule(ModuleBase):
    def __init__(self, model_name: str):
        self.model_name = model_name

        self._data = np.load("data/energy/data_preprocessed.npy")

    def _load_model(self, horizon: int) -> BaseEstimator:
        if Path(f"models/energy/model_horizon={horizon}.pkl").exists():
            with open(f"models/energy/model_horizon={horizon}.pkl", "rb") as f:
                model = pickle.load(f)
        else:
            raise ValueError(f"Model for horizon {horizon} does not exist")
        return model

    def execute(self, horizon: int):
        model = self._load_model(horizon)

        features = self._data[-1, :].reshape(1, -1)
        prediction = model.predict(features)[0]
        return prediction
