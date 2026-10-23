"""principle-viz reads econ-viz.toml: the shared sections and its own [principle] table."""

import dataclasses
import warnings
from pathlib import Path

import pytest
from matplotlib import get_data_path
from mosaickit import ConfigurationError, econ_toml

from principle_viz import Config, default_theme
from principle_viz.config import COLOR_MODELS, COLOR_ROLES, SCHEMA, STROKES
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.visuals.theme import BUILTIN_COLOR_MODELS, ColorModel, PlotTheme

DEJAVU = Path(get_data_path()) / "fonts" / "ttf"

TOML = """
base = "default"

[font]
text = "serif"

[fonts]
serif = ["fonts/DejaVuSerif.ttf"]

[color]
axis = "#101010"
label = "#202020"
ic = "#8c8c8c"              # utility-viz's own key, skipped here

[stroke.budget]
width = 2.6                 # utility-viz's own section, skipped here

[principle]
palette = "manual"
language = "zh-TW"

[principle.color]
demand = "#123456"
supply = "#654321"

[principle.stroke]
demand = 2.0

[principle.marker]
equilibrium = 5
"""


@pytest.fixture(autouse=True)
def _reset():
    yield
    Config.reset()


def _write(tmp_path: Path, text: str = TOML) -> Path:
    (tmp_path / "fonts").mkdir(exist_ok=True)
    (tmp_path / "fonts" / "DejaVuSerif.ttf").write_bytes(
        (DEJAVU / "DejaVuSerif.ttf").read_bytes()
    )
    path = tmp_path / "econ-viz.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_reads_shared_sections_and_the_principle_table(tmp_path):
    theme = Config.load(_write(tmp_path)).theme

    assert theme.font == "serif"
    assert theme.fonts is not None
    assert theme.fonts.serif == (tmp_path / "fonts" / "DejaVuSerif.ttf",)
    assert theme.language == "zh-TW"
    assert theme.color_model.axis_color == "#101010"
    assert theme.color_model.label_color == "#202020"
    assert theme.color_model.demand_color == "#123456"
    assert theme.color_model.supply_color == "#654321"
    assert theme.color_model.cs_color == "#b8b8b8"  # from the manual palette
    assert theme.demand_linewidth == 2.0
    assert theme.equilibrium_marker_size == 25.0


def test_use_makes_it_the_default_theme(tmp_path, monkeypatch):
    config = Config.load(_write(tmp_path)).use()
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    figure = MarketFigure(x_max=12, y_max=12, title="")
    try:
        figure.add_curves(demand, supply, q_max=10)
        figure.add_equilibrium(solve_equilibrium(demand, supply))
        assert figure.theme is config.theme
    finally:
        figure.close()
    assert default_theme() is config.theme
    assert (
        default_theme("nord").color_model.name == "nord"
    )  # an explicit palette still wins

    monkeypatch.chdir(tmp_path)
    assert Config.load().theme == config.theme


def test_without_a_config_the_default_is_unchanged():
    assert default_theme() == default_theme("default")
    assert Config.discover(Path("/nonexistent")) == Config()
    with pytest.raises(ConfigurationError, match="econ-viz.toml"):
        Config.load(Path("/nonexistent/econ-viz.toml"))


@pytest.mark.parametrize(
    "extra",
    [
        "[principle]\nshape = 1\n",
        "[principle.color]\nsky = '#fff'\n",
        "[principle.color]\ndemand = 3\n",
        "[principle.stroke]\ndemand = -1\n",
        "[principle.marker]\nbig = 3\n",
        "[principle]\npalette = 'rainbow'\n",
        "[principle]\nlanguage = 'fr'\n",
    ],
)
def test_bad_principle_settings_are_rejected(tmp_path, extra):
    with pytest.raises(ConfigurationError):
        Config.load(_write(tmp_path, extra))


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        (
            "[principle.color]\ndemnad = '#fff'\n",
            r"econ-viz.toml: \[principle.color\] unknown key 'demnad'; did you mean 'demand'\?",
        ),
        (
            "[principle.stroke]\ndemand = -1\n",
            r"econ-viz.toml: \[principle.stroke\] demand must be a positive number, got -1",
        ),
        (
            "colour = 1\n",
            r"econ-viz.toml: unknown top-level key 'colour'; did you mean 'color'\?",
        ),
        ("base = 'nrod'\n", r"econ-viz.toml: base 'nrod' .*did you mean 'nord'\?"),
        (
            "[principle]\npaletet = 'nord'\n",
            r"unknown key 'paletet'; did you mean 'palette'\?",
        ),
    ],
)
def test_errors_name_the_file_and_the_table(tmp_path, extra, message):
    with pytest.raises(ConfigurationError, match=message):
        Config.load(_write(tmp_path, extra))


def test_fields_set_nested_attributes():
    fields = SCHEMA.fields
    assert fields["color.demand"].attr == "color_model.demand_color"
    assert fields["stroke.dashed"].attr == "theme.dashed_linewidth"
    assert fields["language"].attr == "theme.language"
    assert SCHEMA.shared["axis"] == "color_model.axis_color"

    theme = Config.from_dict(
        {
            "principle": {
                "color": {"tax_revenue": "#abcdef", "arrow": "red"},
                "stroke": {name: 1.5 for name in STROKES},
            }
        }
    ).theme
    assert theme.color_model.name == "default"
    assert theme.color_model.tax_revenue_color == "#abcdef"
    assert theme.color_model.arrow_color == "red"
    for name in STROKES:
        assert getattr(theme, f"{name}_linewidth") == 1.5


def test_the_lists_match_the_theme_module():
    assert set(COLOR_MODELS) == set(BUILTIN_COLOR_MODELS)
    assert COLOR_ROLES == tuple(
        f.name.removesuffix("_color")
        for f in dataclasses.fields(ColorModel)
        if f.name.endswith("_color")
    )
    assert all(hasattr(PlotTheme(), f"{name}_linewidth") for name in STROKES)


@pytest.mark.parametrize("name", sorted(BUILTIN_COLOR_MODELS))
def test_base_picks_a_colour_model(name):
    assert Config.from_dict({"base": name}).theme == PlotTheme.from_palette(name)


def test_palette_wins_over_base_and_keeps_the_named_colours():
    theme = Config.from_dict(
        {
            "base": "nord",
            "color": {"axis": "#010101"},
            # the colours come first: palette must not drop them
            "principle": {"color": {"demand": "#020202"}, "palette": "Manual"},
        }
    ).theme
    manual = PlotTheme.from_palette("manual").color_model
    assert theme.color_model == dataclasses.replace(
        manual, axis_color="#010101", demand_color="#020202"
    )


def test_defaults_written_out_give_the_default_theme():
    theme = Config.from_dict(
        {
            "base": "default",
            "principle": {
                "language": "en",
                "stroke": {"demand": 3.5, "tax": 1},
                "marker": {"equilibrium": 6.5},
            },
        }
    ).theme
    assert theme == PlotTheme()
    assert Config.from_dict({}) == Config()


def test_utility_settings_are_ignored(tmp_path):
    legacy = (
        "[color]\nic = '#8c8c8c'\n\n[stroke.ic]\nwidth = 2.6\n\n"
        "[marker.eq]\nsize = 5\n\n[label.point]\nfontsize = 14\n\n"
        "[fill.budget]\nopacity = 0.08\n\n[legend]\nshow = true\n\n"
        "[utility.color]\nic = '#8c8c8c'\n\n[utility.stroke.ic]\nwidth = 2.6\n"
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        theme = Config.load(_write(tmp_path, legacy)).theme
    assert theme == PlotTheme()


def test_math_font_errors_name_the_font_table(tmp_path):
    with pytest.raises(ConfigurationError, match=r"\[font\] math"):
        Config.load(_write(tmp_path, "[font]\nmath = 'missing.otf'\n"))


def test_registered_under_the_principle_table():
    assert econ_toml.registered()["principle"] is SCHEMA
    assert "# [principle.stroke]" in SCHEMA.template()
