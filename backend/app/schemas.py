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
    co2_factor: float = 0


class MaterialUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    current_stock: float | None = None
    critical_threshold: float | None = None
    co2_factor: float | None = None


class MaterialOut(BaseModel):
    id: int
    name: str
    unit: str
    current_stock: float
    critical_threshold: float
    co2_factor: float
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
    supplier: str | None = None


class MovementOut(BaseModel):
    id: int
    material_id: int
    material_name: str
    movement_type: str
    quantity: float
    note: str | None
    supplier: str | None
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


class EnvironmentalItem(BaseModel):
    material_id: int
    material_name: str
    unit: str
    total_consumption: float
    co2_factor: float
    total_co2_kg: float


class EnvironmentalSummary(BaseModel):
    days: int
    total_co2_kg: float
    total_co2_ton: float
    items: list[EnvironmentalItem]


class SupplierMaterialBreakdown(BaseModel):
    material_name: str
    unit: str
    total_quantity: float


class SupplierSummaryItem(BaseModel):
    supplier: str
    deliveries: int
    last_delivery: datetime
    materials: list[SupplierMaterialBreakdown]
