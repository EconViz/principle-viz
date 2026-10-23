from __future__ import annotations

import dataclasses

import pytest
from mosaickit.themes import ROLES, SHARED_THEMES, get_tokens

from principle_viz import Config
from principle_viz.visuals import roles
from principle_viz.visuals.theme import ColorModel, PlotTheme

# principle-viz's manual colour model before it was built from the shared tokens.
MANUAL_BEFORE = ColorModel(
    name="manual",
    axis_color="#1a1a1a",
    label_color="#1a1a1a",
    demand_color="#8c8c8c",
    supply_color="#1a1a1a",
    baseline_color="#1a1a1a",
    shifted_color="#6e6e6e",
    tax_color="#595959",
    control_color="#595959",
    cs_color="#b8b8b8",
    ps_color="#8c8c8c",
    tax_revenue_color="#d9d9d9",
    dwl_color="#595959",
    arrow_color="#1a1a1a",
)


def test_every_colour_has_a_shared_role():
    colours = {
        f.name.removesuffix("_color")
        for f in dataclasses.fields(ColorModel)
        if f.name.endswith("_color")
    }
    assert set(roles.ELEMENT_ROLES) == colours
    assert set(roles.ELEMENT_ROLES.values()) <= set(ROLES)


def test_the_mapping():
    assert dict(roles.ELEMENT_ROLES) == {
        "axis": "ink",
        "label": "ink",
        "baseline": "ink",
        "arrow": "ink",
        "demand": "primary",
        "supply": "secondary",
        "shifted": "tertiary",
        "tax": "intervention",
        "control": "intervention",
        "cs": "fill.light",
        "ps": "fill.mid",
        "dwl": "fill.dark",
        "tax_revenue": "fill.faint",
    }


def test_manual_is_unchanged():
    assert roles.get_color_model("manual") == MANUAL_BEFORE
    assert PlotTheme.from_palette("manual") == PlotTheme(color_model=MANUAL_BEFORE)


@pytest.mark.parametrize("name", list(SHARED_THEMES))
def test_every_shared_theme_is_a_colour_model(name):
    tokens = get_tokens(name)
    model = roles.get_color_model(name)
    assert model.name == name
    assert model.demand_color == tokens.colors["primary"]
    assert model.supply_color == tokens.colors["secondary"]
    assert model.cs_color == tokens.colors["fill.light"]
    assert Config.from_dict({"base": name}).theme == PlotTheme.from_palette(name)


def test_scales_multiply_the_base_sizes():
    base = PlotTheme()
    theme = PlotTheme.from_palette("presentation")
    tokens = get_tokens("presentation")
    assert theme.demand_linewidth == pytest.approx(
        base.demand_linewidth * tokens.line_scale
    )
    assert theme.dashed_linewidth == pytest.approx(
        base.dashed_linewidth * tokens.line_scale
    )
    assert theme.equilibrium_marker_size == pytest.approx(
        base.equilibrium_marker_size * tokens.marker_scale**2
    )


def test_keyword_arguments_override_the_theme():
    theme = PlotTheme.from_palette("presentation", demand_linewidth=2.0)
    assert theme.demand_linewidth == 2.0
    assert theme.color_model.name == "presentation"


def test_tokens_build_a_theme_directly():
    tokens = dataclasses.replace(get_tokens("default"), name="custom")
    theme = roles.plot_theme(tokens)
    assert theme.color_model.name == "custom"
    assert theme.color_model.demand_color == tokens.colors["primary"]


def test_unknown_theme_is_an_error():
    with pytest.raises(ValueError, match="Available"):
        roles.get_color_model("dark")
