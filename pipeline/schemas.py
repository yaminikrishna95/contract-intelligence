from typing import Literal, Optional, List
from pydantic import BaseModel, Field, ConfigDict


AgreementType = Literal[
    "licensing",
    "services",
    "employment",
    "nda",
    "lease",
    "purchase",
    "other"
]


class Party(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(
        description="Full legal name of the party as written in the contract"
    )
    role: str = Field(
        description="Role of the party (e.g., 'Licensor', 'Licensee', 'Employer', 'Employee', 'Buyer', 'Seller')"
    )


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    agreement_type: AgreementType = Field(
        description="Type of agreement. Choose the BEST FIT from the available categories. Use 'other' only if no category fits."
    )
    effective_date: Optional[str] = Field(
        default=None,
        description="Effective date of the agreement in YYYY-MM-DD format. Use null if not specified."
    )
    parties: List[Party] = Field(
        description="All named parties in the contract with their roles. Typically 2 parties."
    )
    term_length: Optional[str] = Field(
        default=None,
        description="Length of the contract term (e.g., '3 years', '12 months', 'perpetual'). Use null if not specified."
    )
    governing_law: Optional[str] = Field(
        default=None,
        description="Jurisdiction whose law governs the contract (e.g., 'State of Delaware'). Use null if not specified."
    )
    payment_terms: Optional[str] = Field(
        default=None,
        description="Brief 1-2 sentence summary of payment terms. Do not copy the entire payment section."
    )
    termination_clauses: List[str] = Field(
        default_factory=list,
        description="List of distinct termination conditions, each as a short summary (e.g., '30 days written notice', 'Material breach with cure period')."
    )