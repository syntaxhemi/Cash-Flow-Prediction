import torch
import pickle
import numpy as np
import pandas as pd

from src.env import vars
from src.model import model
from src.dtos import SequenceInput, StaticInput

temp_scaler = None
with open(f'{vars.ASSETS_DIR}/{vars.TEMP_SCALER_PATH}', 'rb') as tsp:
    temp_scaler = pickle.load(tsp)

static_scaler = None
with open(f'{vars.ASSETS_DIR}/{vars.STATIC_SCALER_PATH}', 'rb') as ssp:
    static_scaler = pickle.load(ssp)

def process_input(x_seq: SequenceInput, x_static: StaticInput) -> tuple[torch.Tensor, torch.Tensor]:
    seq_df = pd.DataFrame(x_seq.model_dump(), index=[0])
    static_df = pd.DataFrame(x_static.model_dump(), index=[0])

    seq_array = seq_df.to_numpy(dtype=np.float32)
    static_array = static_df.to_numpy(dtype=np.float32)

    seq_scaled = temp_scaler.transform(seq_array)  # type: ignore
    static_scaled = static_scaler.transform(static_array)  # type: ignore

    X_seq = np.expand_dims(seq_scaled, axis=0) 
    X_static = static_scaled  

    X_seq_tensor = torch.tensor(X_seq, dtype=torch.float32)
    X_static_tensor = torch.tensor(X_static, dtype=torch.float32)

    return X_seq_tensor, X_static_tensor

def predict(seq_tensor: torch.Tensor, static_tensor: torch.Tensor) -> float:
    prediction = None
    with torch.no_grad():
        prediction = model(seq_tensor, static_tensor)

    pred_val = prediction.cpu().numpy().flatten()[0]
    return float(pred_val)