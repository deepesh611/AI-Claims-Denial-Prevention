# api/models.py

from pydantic import BaseModel
from typing import List, Optional

class PredictRequest(BaseModel):
    claim_ids: List[str]

class ClaimResult(BaseModel):
    claim_id      : str
    status        : str
    risk_score    : Optional[float]
    risk_label    : Optional[str]
    rule_failures : Optional[List[str]]
    reason_1      : Optional[str]
    reason_2      : Optional[str]
    policy_source : Optional[str]
    policy_text   : Optional[str]
    ai_recommendation: Optional[str]

class PredictResponse(BaseModel):
    results: List[ClaimResult]