from pydantic_settings import BaseSettings, SettingsConfigDict

class Variables(BaseSettings):
    ASSETS_DIR: str    
    TEMP_SCALER_PATH: str
    STATIC_SCALER_PATH: str
    MODEL_PARAMS_PATH: str

    SEQ_INPUT_SIZE: int
    STATIC_INPUT_SIZE: int
    LSTM_HIDDEN: int
    DENSE_HIDDEN: int

    CLIENT_URL: str

    model_config = SettingsConfigDict(
        env_file=('.env')
    )

vars = Variables() #type: ignore
