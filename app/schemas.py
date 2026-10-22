"""Pydantic schemas (API request/response contracts)."""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=5, max_length=32)
    group_name: str = Field(min_length=1, max_length=64)
    monthly_amount: int = Field(gt=0)

    @field_validator("name", "group_name", mode="before")
    @classmethod
    def strip(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        v = "".join(ch for ch in v if ch.isdigit() or ch == "+")
        if len(v) < 5:
            raise ValueError("phone must contain at least 5 digits")
        return v


class StudentUpdate(BaseModel):
    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = "".join(ch for ch in v if ch.isdigit() or ch == "+")
        if len(v) < 5:
            raise ValueError("phone must contain at least 5 digits")
        return v

    @model_validator(mode='before')
    def reject_null(cls, data: dict) -> dict:
        for k, v in data.items():
            if v is None:
                raise ValueError(f"{k} cannot be null")
        return data

    name: str | None = Field(default=None, min_length=1, max_length=120)
    phone: str | None = Field(default=None, min_length=5, max_length=32)
    group_name: str | None = Field(default=None, min_length=1, max_length=64)
    monthly_amount: int | None = Field(default=None, gt=0)


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    group_name: str
    monthly_amount: int


class PaymentCreate(BaseModel):
    student_id: int
    amount: int = Field(gt=0)
    paid_at: date


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    amount: int
    paid_at: date


class DebtorOut(BaseModel):
    student_id: int
    name: str
    phone: str
    group_name: str
    monthly_amount: int
    paid_in_month: int
    debt: int
