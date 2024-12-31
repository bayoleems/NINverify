from pydantic import BaseModel, Field

class Payload(BaseModel):
    nin: str = Field(..., min_length=11, max_length=11, pattern=r'^\d{11}$', description="National Identification Number (11 digits)")
    day: str = Field(..., min_length=1, max_length=2, pattern=r'^\d{1,2}$', description="Day (1 or 2 digits)")
    month: str = Field(..., pattern=r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$', description="Month (3-letter abbreviation)")
    year: str = Field(..., min_length=4, max_length=4, pattern=r'^\d{4}$', description="Year (4 digits)")
