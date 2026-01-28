from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from typing import Optional
import os
import logging
from models import MessageRequest, HoneyPotResponse, EngagementMetrics, ExtractedIntelligence, CallbackPayload
from agent import agent_instance
from utils import send_final_result

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic Honey-Pot API")

# API Security
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "mysecretkey")

@app.post("/analyze", response_model=HoneyPotResponse)
async def analyze_message(
    request: MessageRequest, 
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(None)
):
    """
    Main endpoint to analyze message, detect scam, and engage agent.
    """
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # 1. Detect Scam
    is_scam, reason = agent_instance.analyze_scam(
        request.message.text, 
        request.conversationHistory
    )
    
    # Check if scam was already detected in history (heuristic: consistent scammer behavior)
    # For now, we rely on the current analysis or if the user passed previous flags (not in schema).
    # We'll trust the agent's analysis of the full history + current message.

    response_text = ""
    extracted_intel = ExtractedIntelligence()
    
    if is_scam:
        # 2. Extract Intelligence
        extracted_intel = agent_instance.extract_intelligence(
            request.message.text, 
            request.conversationHistory
        )
        
        # 3. Generate Response
        response_text = agent_instance.generate_response(
            request.message.text, 
            request.conversationHistory
        )
        
        # 4. Trigger Callback (Background Task)
        # We construct the payload for the callback
        # Calculate heuristics for "totalMessagesExchanged"
        total_messages = len(request.conversationHistory) + 2 # history + current + reply
        
        callback_payload = CallbackPayload(
            sessionId=request.sessionId,
            scamDetected=True,
            totalMessagesExchanged=total_messages,
            extractedIntelligence=extracted_intel,
            agentNotes=f"Scam detected: {reason}"
        )
        
        # Send callback in background to avoid blocking response
        background_tasks.add_task(send_final_result, callback_payload)

    return HoneyPotResponse(
        status="success",
        scamDetected=is_scam,
        engagementMetrics=EngagementMetrics(
            totalMessagesExchanged=len(request.conversationHistory) + 1
            # duration not easily calculable without session state, omitting or 0
        ),
        extractedIntelligence=extracted_intel,
        agentNotes=response_text if is_scam else "No scam detected."
    )
