"""principle-viz reads econ-viz.toml: the shared sections and its own [principle] table."""

from pathlib import Path

import pytest
from matplotlib import get_data_path
from mosaickit import ConfigurationError

from principle_viz import Config, default_theme
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure

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
