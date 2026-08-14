from dataclasses import dataclass
from datetime import datetime, timedelta

from app.forecast import compute_daily_consumption, compute_trend, forecast_days_remaining


def make_daily_totals(values):
    today = datetime.utcnow().date()
    start = today - timedelta(days=len(values) - 1)
    return {(start + timedelta(days=i)).isoformat(): v for i, v in enumerate(values)}


@dataclass
class FakeMovement:
    movement_type: str
    quantity: float
    created_at: datetime


def test_compute_daily_consumption_sums_cikis_only():
    today = datetime.utcnow()
    movements = [
        FakeMovement("cikis", 10, today),
        FakeMovement("cikis", 5, today),
        FakeMovement("giris", 100, today),
    ]
    totals = compute_daily_consumption(movements, days=1)
    key = today.date().isoformat()
    assert totals[key] == 15


def test_compute_daily_consumption_ignores_out_of_range_movements():
    today = datetime.utcnow()
    old_movement = FakeMovement("cikis", 999, today - timedelta(days=200))
    totals = compute_daily_consumption([old_movement], days=90)
    assert sum(totals.values()) == 0


def test_forecast_no_consumption_returns_none():
    daily = make_daily_totals([0] * 10)
    avg, days_remaining, message = forecast_days_remaining(daily, current_stock=100)
    assert avg == 0
    assert days_remaining is None
    assert "tahmin yapilamiyor" in message.lower()


def test_forecast_constant_consumption_estimates_days_remaining():
    daily = make_daily_totals([10] * 20)
    avg, days_remaining, message = forecast_days_remaining(daily, current_stock=100)
    assert avg == 10
    assert days_remaining is not None
    assert 9 <= days_remaining <= 11


def test_trend_increasing():
    values = [5] * 7 + [15] * 7
    assert compute_trend(make_daily_totals(values)) == "artiyor"


def test_trend_decreasing():
    values = [15] * 7 + [5] * 7
    assert compute_trend(make_daily_totals(values)) == "azaliyor"


def test_trend_stable_when_flat():
    values = [10] * 14
    assert compute_trend(make_daily_totals(values)) == "sabit"


def test_trend_insufficient_history_is_stable():
    daily = make_daily_totals([10] * 5)
    assert compute_trend(daily) == "sabit"
