from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from typing import Optional, Dict
import os
import logging
from models import MessageRequest, AgentResponse, ExtractedIntelligence, CallbackPayload
from agent import agent_instance
from utils import send_final_result

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic Honey-Pot API")

# API Security
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "mysecretkey")

# Session tracking for conversation state
# In production, use Redis or database
session_state: Dict[str, Dict] = {}

# Minimum messages before sending callback
MIN_MESSAGES_FOR_CALLBACK = 5

@app.post("/analyze", response_model=AgentResponse)
async def analyze_message(
    request: MessageRequest, 
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(None)
):
    """
    Main endpoint to analyze message, detect scam, and engage agent.
    Always returns a reply to maintain conversation.
    Sends callback after sufficient engagement (5+ messages).
    """
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    session_id = request.sessionId
    message_text = request.message.text if request.message else ""
    
    # Initialize session state if new
    if session_id not in session_state:
        session_state[session_id] = {
            "scam_detected": False,
            "message_count": 0,
            "callback_sent": False,
            "extracted_intel": ExtractedIntelligence()
        }
    
    # Increment message count
    session_state[session_id]["message_count"] += 1
    current_count = session_state[session_id]["message_count"]
    
    logger.info(f"Session {session_id}: Message #{current_count}")
    
    # Handle empty/test messages
    if not message_text:
        logger.info(f"Empty message for session: {session_id}")
        return AgentResponse(
            status="success",
            reply="Hello, how can I help you?"
        )
    
    # 1. Detect Scam (always analyze)
    is_scam, reason = agent_instance.analyze_scam(
        message_text, 
        request.conversationHistory
    )
    
    # Update session state
    if is_scam and not session_state[session_id]["scam_detected"]:
        session_state[session_id]["scam_detected"] = True
        logger.info(f"Session {session_id}: Scam detected - {reason}")
    
    # 2. Generate Reply (ALWAYS - this is key for multi-turn conversation)
    if is_scam or session_state[session_id]["scam_detected"]:
        # Engage as gullible victim to extract intelligence
        reply_text = agent_instance.generate_response(
            message_text, 
            request.conversationHistory
        )
        
        # Extract intelligence in background
        extracted_intel = agent_instance.extract_intelligence(
            message_text, 
            request.conversationHistory
        )
        session_state[session_id]["extracted_intel"] = extracted_intel
    else:
        # Generate neutral response for non-scam messages
        reply_text = agent_instance.generate_neutral_response(
            message_text,
            request.conversationHistory
        )
    
    # 3. Send Callback ONLY after sufficient engagement
    if (session_state[session_id]["scam_detected"] and 
        current_count >= MIN_MESSAGES_FOR_CALLBACK and 
        not session_state[session_id]["callback_sent"]):
        
        logger.info(f"Session {session_id}: Sending final callback (after {current_count} messages)")
        
        callback_payload = CallbackPayload(
            sessionId=session_id,
            scamDetected=True,
            totalMessagesExchanged=current_count,
            extractedIntelligence=session_state[session_id]["extracted_intel"],
            agentNotes=f"Scam detected: {reason}. Engaged for {current_count} messages."
        )
        
        # Mark callback as sent
        session_state[session_id]["callback_sent"] = True
        
        # Send callback in background
        background_tasks.add_task(send_final_result, callback_payload)
    
    # 4. Return simple response format (as per problem statement)
    return AgentResponse(
        status="success",
        reply=reply_text
    )
