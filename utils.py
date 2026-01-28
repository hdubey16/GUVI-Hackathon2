import requests
import logging
from models import CallbackPayload

logger = logging.getLogger(__name__)

CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

def send_final_result(payload: CallbackPayload) -> bool:
    """
    Sends the final extracted intelligence to the GUVI evaluation endpoint.
    """
    try:
        # Convert model to dict, ensuring nested models are also converted
        payload_dict = payload.model_dump()
        
        logger.info(f"Sending final result to {CALLBACK_URL}: {payload_dict}")
        
        response = requests.post(
            CALLBACK_URL,
            json=payload_dict,
            timeout=5
        )
        
        response.raise_for_status()
        logger.info(f"Callback successful: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to send callback: {e}")
        return False
