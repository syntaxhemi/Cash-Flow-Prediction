# Cash Flow Prediction

Predicts cash flow for small to medium-sized enterprises.

## Setup Instructions

### Clone the Repository

```bash
git clone https://github.com/praevalis/Cash-Flow-Prediction.git
```

```bash
cd Cash-Flow-Prediction
```

### Client Setup (Terminal 1)

1. **Move into client directory**

```bash
cd client
```

2. **Install dependencies**

```bash
npm install
```

3. **Add environment variables**
   Create a `.env` file in the `client` directory and add the following variables,

```bash
VITE_API_URL='http://localhost:8000
```

4. **Run the application**

```bash
npm run dev
```

**You are all set!** The application is now running at `http://localhost:5173`.

### Server Setup (Terminal 2)

1. **Move into server directory**

```bash
cd server
```

2. **Install dependencies**

```bash
uv venv
uv sync
```

3. **Add environment variables**
   Create a `.env` file and add the following variables to it,

```bash
ASSETS_DIR='assets'
TEMP_SCALER_PATH='scalers/temporal_scaler.pkl'
STATIC_SCALER_PATH='scalers/static_scaler.pkl'
MODEL_PARAMS_PATH='params/baseline.pth'
SEQ_INPUT_SIZE=5
STATIC_INPUT_SIZE=10
LSTM_HIDDEN=128
DENSE_HIDDEN=64
CLIENT_URL='http://localhost:5173'
```

4. **Run the server**

```bash
uv run uvicorn src.main:api --reload
# --reload flag is only used during development
```

The server is now running at `http://localhost:8000`.
