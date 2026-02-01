from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Message(BaseModel):
    sender: Optional[str] = "scammer"  # "scammer" or "user" (agent)
    text: Optional[str] = ""
    timestamp: Optional[datetime] = None

class MessageRequest(BaseModel):
    sessionId: Optional[str] = "test-session"
    message: Optional[Message] = None
    conversationHistory: List[Message] = []
    metadata: Optional[Dict[str, Any]] = None

class EngagementMetrics(BaseModel):
    engagementDurationSeconds: int = 0
    totalMessagesExchanged: int = 0

class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []

class HoneyPotResponse(BaseModel):
    status: str
    scamDetected: bool
    engagementMetrics: EngagementMetrics
    extractedIntelligence: ExtractedIntelligence
    agentNotes: Optional[str] = None

class CallbackPayload(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: Optional[str] = None
