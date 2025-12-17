from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class TradeApproval(BaseModel):
    CFAAM_Ref: str
    Importer_Name: str
    Date_Submitted: str
    Currency_and_Amount: str
    Expiry_Date: str
    Returns_Frequency: str
    Condition_Text: str
    Next_Due_Date: Optional[str]
    Compliance_Alert_Date: Optional[str]
    Status: Optional[str]
    Reminder_Sent_Flag: Optional[bool]
    Initial_Alert_Date: Optional[str]

    @validator('Date_Submitted', 'Expiry_Date', 'Next_Due_Date', 'Compliance_Alert_Date', 'Initial_Alert_Date', pre=True, always=True)
    def validate_date(cls, v):
        if v:
            try:
                datetime.strptime(v, "%d %B %Y")
            except Exception:
                raise ValueError(f"Date '{v}' is not in 'DD MMMM YYYY' format.")
        return v
