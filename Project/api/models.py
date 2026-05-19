# api/models.py

from pydantic import BaseModel
from typing import List, Optional

class PredictRequest(BaseModel):
    claim_ids: List[str]

class ClaimResult(BaseModel):
    claim_id         : str
    status           : Optional[str]
    risk_score       : Optional[float]
    risk_label       : Optional[str]
    risk_level       : Optional[str]        # add this
    rule_failures    : Optional[List[str]]
    reason_1         : Optional[str]
    reason_2         : Optional[str]
    policy_violated  : Optional[str]        # rename from policy_source
    policy_text      : Optional[str]
    risk_reasons     : Optional[List[str]]  # add this
    ai_recommendation: Optional[str]

class PredictResponse(BaseModel):
    results: List[ClaimResult]