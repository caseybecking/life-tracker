from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime

# Base schemas
class NounBase(BaseModel):
    name: str = Field(..., description="Name of the noun (e.g., Banking, Person, Home)")
    description: Optional[str] = Field(None, description="Description of the noun")

class NounCreate(NounBase):
    pass

class Noun(NounBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AttributeBase(BaseModel):
    name: str = Field(..., description="Name of the attribute (e.g., Transaction, Casey, Garden)")
    description: Optional[str] = Field(None, description="Description of the attribute")

class AttributeCreate(AttributeBase):
    noun_id: int

class Attribute(AttributeBase):
    id: int
    noun_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ValueBase(BaseModel):
    name: str = Field(..., description="Name of the value (e.g., Category, Weight, Mowing)")
    data_type: str = Field(..., description="Data type: string, number, date, boolean")
    description: Optional[str] = Field(None, description="Description of the value")

class ValueCreate(ValueBase):
    attribute_id: int

class Value(ValueBase):
    id: int
    attribute_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DataBase(BaseModel):
    data_value: str = Field(..., description="The actual data value")
    notes: Optional[str] = Field(None, description="Additional notes")
    date_recorded: Optional[datetime] = Field(None, description="When this data was recorded")

class DataCreate(DataBase):
    value_id: int

class Data(DataBase):
    id: int
    value_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Financial specific schemas
class BankAccountBase(BaseModel):
    institution: str = Field(..., description="Bank institution name")
    account_name: str = Field(..., description="Account name (e.g., SF_Checking, Cuna)")
    account_type: str = Field(..., description="Account type (checking, savings, credit, etc.)")

class BankAccountCreate(BankAccountBase):
    pass

class BankAccount(BankAccountBase):
    id: int
    balance: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    account_id: int
    amount: float = Field(..., description="Transaction amount (positive for income, negative for expense)")
    category: str = Field(..., description="Transaction category (e.g., Income, Food, Gas)")
    description: str = Field(..., description="Transaction description")
    transaction_date: datetime = Field(..., description="Date of the transaction")

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Response schemas for hierarchical data
class NounWithAttributes(Noun):
    attributes: List[Attribute] = []

class AttributeWithValues(Attribute):
    values: List[Value] = []

class ValueWithData(Value):
    data_entries: List[Data] = []

# API Response schemas
class TrackDataResponse(BaseModel):
    noun: str
    attribute: str
    value: str
    data: str
    date_recorded: datetime
    notes: Optional[str] = None

class FinancialSummary(BaseModel):
    total_balance: float
    accounts: List[BankAccount]
    recent_transactions: List[Transaction] 