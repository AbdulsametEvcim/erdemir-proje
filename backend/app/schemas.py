from datetime import datetime

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str


class MaterialCreate(BaseModel):
    name: str
    unit: str = "ton"
    current_stock: float = 0
    critical_threshold: float = 0


class MaterialUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    current_stock: float | None = None
    critical_threshold: float | None = None


class MaterialOut(BaseModel):
    id: int
    name: str
    unit: str
    current_stock: float
    critical_threshold: float
    status: str
    trend: str

    class Config:
        from_attributes = True


class ConsumptionComparisonItem(BaseModel):
    material_id: int
    material_name: str
    unit: str
    total_consumption: float


class MovementCreate(BaseModel):
    material_id: int
    movement_type: str  # "giris" | "cikis"
    quantity: float
    note: str | None = None


class MovementOut(BaseModel):
    id: int
    material_id: int
    material_name: str
    movement_type: str
    quantity: float
    note: str | None
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class DailyConsumption(BaseModel):
    date: str
    quantity: float


class MaterialAnalysis(BaseModel):
    material_id: int
    material_name: str
    unit: str
    current_stock: float
    critical_threshold: float
    daily_consumption: list[DailyConsumption]
    avg_daily_consumption: float
    days_remaining: float | None
    forecast_message: str


class AlertOut(BaseModel):
    id: int
    name: str
    current_stock: float
    critical_threshold: float
    unit: str
