from __future__ import annotations

import pytest

from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.trade import (
    QuotaRentRecipient,
    TradeDirection,
    TradeScenario,
    analyze_trade,
)


@pytest.fixture
def market() -> tuple[Line, Line]:
    return Line.from_inverse(12, -1), Line.from_inverse(2, 1)


def test_free_trade_imports_and_gains_from_trade(market: tuple[Line, Line]) -> None:
    result = analyze_trade(*market, TradeScenario(world_price=4))

    assert result.free_trade.direction == TradeDirection.IMPORT
    assert result.free_trade.quantity_demanded == pytest.approx(8)
    assert result.free_trade.quantity_supplied == pytest.approx(2)
    assert result.free_trade.imports == pytest.approx(6)
    assert result.free_trade.gains_from_trade == pytest.approx(9)
    assert result.deadweight_loss == pytest.approx(0)


def test_free_trade_exports_when_world_price_is_high(
    market: tuple[Line, Line],
) -> None:
    result = analyze_trade(*market, TradeScenario(world_price=9))

    assert result.policy.direction == TradeDirection.EXPORT
    assert result.policy.exports == pytest.approx(4)
    assert result.policy.gains_from_trade == pytest.approx(4)


def test_tariff_raises_domestic_price_and_creates_revenue_and_dwl(
    market: tuple[Line, Line],
) -> None:
    result = analyze_trade(*market, TradeScenario(world_price=4, tariff=2))

    assert result.policy.domestic_price == pytest.approx(6)
    assert result.policy.imports == pytest.approx(2)
    assert result.policy.government_revenue == pytest.approx(4)
    assert result.policy.is_policy_binding
    assert result.deadweight_loss == pytest.approx(4)


def test_domestic_quota_rent_matches_equivalent_tariff(
    market: tuple[Line, Line],
) -> None:
    result = analyze_trade(*market, TradeScenario(world_price=4, import_quota=2))

    assert result.policy.domestic_price == pytest.approx(6)
    assert result.policy.imports == pytest.approx(2)
    assert result.policy.quota_rent == pytest.approx(4)
    assert result.policy.national_quota_rent == pytest.approx(4)
    assert result.deadweight_loss == pytest.approx(4)


def test_foreign_quota_rent_is_an_additional_national_loss(
    market: tuple[Line, Line],
) -> None:
    result = analyze_trade(
        *market,
        TradeScenario(
            world_price=4,
            import_quota=2,
            quota_rent_recipient=QuotaRentRecipient.FOREIGN,
        ),
    )

    assert result.policy.national_quota_rent == 0
    assert result.deadweight_loss == pytest.approx(8)


def test_trade_figure_contains_world_price_and_trade_volume(
    market: tuple[Line, Line],
) -> None:
    result = analyze_trade(*market, TradeScenario(world_price=4, tariff=2))
    figure = MarketFigure(x_max=12, y_max=13)
    figure.add_curves(*market, q_max=11).add_trade(result)
    ids = {layer.id for layer in figure.scene.layers}

    assert "market.trade.world_price" in ids
    assert "market.trade.policy_price" in ids
    assert "market.trade.volume" in ids  # brace over Q_s..Q_d on the quantity axis
    assert "market.trade.policy_rent" in ids
