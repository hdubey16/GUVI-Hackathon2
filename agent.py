import os
import json
import logging
import google.generativeai as genai
from typing import List, Tuple
from dotenv import load_dotenv
from models import Message, ExtractedIntelligence, EngagementMetrics

load_dotenv()

logger = logging.getLogger(__name__)

# Configure Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables.")

# Model configuration
GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
    "response_mime_type": "application/json",
}

TEXT_GENERATION_CONFIG = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 512,
    "response_mime_type": "text/plain",
}

class HoneyPotAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def analyze_scam(self, current_message: str, history: List[Message]) -> Tuple[bool, str]:
        """
        Analyzes the conversation to detect scam intent.
        Returns (is_scam, reason).
        """
        if not API_KEY:
            return False, "API Key missing"

        history_text = "\n".join([f"{msg.sender}: {msg.text}" for msg in history])
        prompt = f"""
        You are an expert scam detection system. Analyze the following message and conversation history.
        Determine if the sender (scammer) is exhibiting scam intent (phishing, fraud, fake offers, urgency, etc.).
        
        Conversation History:
        {history_text}
        
        Current Message:
        {current_message}
        
        Return a JSON object with the following fields:
        - "is_scam": boolean
        - "reason": string (brief explanation)
        """
        
        try:
            response = self.model.generate_content(
                prompt, 
                generation_config=GENERATION_CONFIG
            )
            data = json.loads(response.text)
            return data.get("is_scam", False), data.get("reason", "No reason provided")
        except Exception as e:
            logger.error(f"Error in scam detection: {e}")
            return False, f"Error: {e}"

    def extract_intelligence(self, current_message: str, history: List[Message]) -> ExtractedIntelligence:
        """
        Extracts intelligence from the conversation.
        """
        history_text = "\n".join([f"{msg.sender}: {msg.text}" for msg in history])
        prompt = f"""
        Analyze the following conversation and extract intelligence about the scammer.
        
        Conversation History:
        {history_text}
        
        Current Message:
        {current_message}
        
        Return a JSON object matching this structure:
        {{
            "bankAccounts": ["list of bank account numbers found"],
            "upiIds": ["list of UPI IDs found"],
            "phishingLinks": ["list of URLs found"],
            "phoneNumbers": ["list of phone numbers found"],
            "suspiciousKeywords": ["list of key words indicating scam"]
        }}
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=GENERATION_CONFIG
            )
            data = json.loads(response.text)
            return ExtractedIntelligence(**data)
        except Exception as e:
            logger.error(f"Error in extraction: {e}")
            return ExtractedIntelligence()

    def generate_response(self, current_message: str, history: List[Message]) -> str:
        """
        Generates a honey-pot response to keep the scammer engaged.
        """
        history_text = "\n".join([f"{msg.sender}: {msg.text}" for msg in history])
        prompt = f"""
        You are an AI Agent acting as a gullible but cautious victim. 
        Your goal is to waste the scammer's time (honey-potting) and get them to reveal more information.
        Do not reveal you are an AI. Behave like a real human (e.g., an elderly person or a non-tech-savvy user).
        Keep the conversation going. Ask clarifying questions.
        
        Conversation History:
        {history_text}
        
        Current Message from Scammer:
        {current_message}
        
        Generate a text response to the scammer.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=TEXT_GENERATION_CONFIG
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            return "I am confused, can you explain that again?"

agent_instance = HoneyPotAgent()
