"""Input dataset loading."""

from pathlib import Path

import pandas as pd

from training.config import DataConfig


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f'Dataset not found: {path}')
    return pd.read_csv(path).drop(columns=['Unnamed: 0'], errors='ignore')


def load_datasets(config: DataConfig) -> dict[str, pd.DataFrame]:
    return {
        'account_receivable': _read_csv(config.account_receivable_path),
        'businesses': _read_csv(config.businesses_path),
        'credit_account_history': _read_csv(config.credit_account_history_path),
        'credit_card_history': _read_csv(config.credit_card_history_path),
        'credit_rating': _read_csv(config.credit_rating_path),
        'loan': _read_csv(config.loan_path),
    }
