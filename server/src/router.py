from fastapi import APIRouter

from src.inference import process_input, predict
from src.dtos import InferenceRequest, InferenceResponse

router = APIRouter()

@router.post('/infer', response_model=InferenceResponse)
def inference_endpoint(payload: InferenceRequest) -> InferenceResponse:
    try:
        x_seq = payload.seq_input
        x_static = payload.static_input

        processed_seq, processed_static = process_input(x_seq, x_static)
        predicted_value = predict(processed_seq, processed_static)

        return InferenceResponse(
            net_cash_flow=predicted_value
        )

    except Exception as e:
        print(f'Exception occurred in inference endpoint: {e}')
        raise e
