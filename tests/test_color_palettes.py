from __future__ import annotations

import pytest

from principle_viz.plot import (
    MarketFigure,
    PlotTheme,
    get_color_model,
    list_color_models,
)


def test_list_color_models_matches_econ_viz_builtin_names() -> None:
    names = set(list_color_models())
    assert names == {
        "manual",
        "default",
        "colorblind",
        "monochrome",
        "nord",
        "paper",
        "presentation",
    }


def test_get_color_model_resolves_known_palettes() -> None:
    default = get_color_model("default")
    colorblind = get_color_model("colorblind")
    nord = get_color_model("nord")
    monochrome = get_color_model("monochrome")

    assert default.name == "default"
    assert colorblind.name == "colorblind"
    assert nord.name == "nord"
    assert monochrome.name == "monochrome"


def test_plot_theme_from_palette() -> None:
    theme = PlotTheme.from_palette("nord")
    assert theme.color_model.name == "nord"
    assert theme.axis_color == "#2E3440"


def test_market_figure_accepts_palette_name() -> None:
    fig = MarketFigure(title="Palette", palette="colorblind")
    assert fig.theme.color_model.name == "colorblind"
    fig.close()


def test_unknown_palette_raises() -> None:
    with pytest.raises(ValueError):
        get_color_model("not-a-palette")


def test_default_palette_takes_the_shared_default_theme() -> None:
    from mosaickit.themes import get_tokens

    tokens = get_tokens("default").colors
    default = get_color_model("default")
    assert default.demand_color == tokens["primary"] == "#377EB8"
    assert default.supply_color == tokens["secondary"] == "#4DAF4A"
    assert default.cs_color == tokens["fill.light"]
    assert default.ps_color == tokens["fill.mid"]
    assert default.dwl_color == tokens["fill.dark"]
    assert default.tax_revenue_color == tokens["fill.faint"]


def test_default_theme_welfare_opacities_and_background() -> None:
    roles = PlotTheme().to_mosaickit().roles
    assert roles["principle.welfare.consumer"].fill.opacity == 0.15
    assert roles["principle.welfare.producer"].fill.opacity == 0.15
    assert roles["principle.welfare.loss"].fill.opacity == 0.45
    assert roles["principle.welfare.revenue"].fill.opacity == 0  # labelled, not filled
    assert roles["canvas"].fill.opacity == 1
    assert roles["principle.market.demand"].stroke.width == 3.5
    assert roles["principle.market.supply"].stroke.width == 3.5
