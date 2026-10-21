"""Fonts behave as in every diagram package built on MosaicKit: font, fonts and math_font."""

from pathlib import Path

import matplotlib
import pytest
from mosaickit import MathFont, TextFonts

from principle_viz import MarketFigure, PlotTheme

FONTS = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
MATH = FONTS / "DejaVuSerif.ttf"  # has an OpenType MATH table


def test_the_default_font_is_sans():
    theme = PlotTheme().to_mosaickit()
    assert theme.defaults.text.font == "sans"


@pytest.mark.parametrize("font", ["sans", "serif", "mono"])
def test_all_three_generic_fonts_reach_the_theme_defaults(font):
    assert PlotTheme(font=font).to_mosaickit().defaults.text.font == font


@pytest.mark.parametrize("font", ["DejaVu Serif", "Avenir", ""])
def test_installed_font_names_are_not_fonts(font):
    with pytest.raises(ValueError, match="font must be one of sans, serif, mono"):
        PlotTheme(font=font)


def test_a_role_can_have_its_own_generic_font():
    theme = PlotTheme(font_roles={"principle.market.demand": "serif"}).to_mosaickit()
    assert theme.roles["principle.market.demand"].text.font == "serif"
    assert theme.defaults.text.font == "sans"
    with pytest.raises(ValueError, match="font must be one of"):
        PlotTheme(font_roles={"axes": "Avenir"})


def test_font_files_and_the_math_font_reach_the_mosaickit_config():
    fonts = TextFonts(serif=MATH)
    theme = PlotTheme(fonts=fonts, math_font=MATH)
    config = theme.mosaickit_config()
    assert config.fonts is fonts
    assert config.math_font == MathFont(MATH)
    assert PlotTheme(math_font=MathFont(MATH)).math_font == MathFont(MATH)


def test_settings_that_are_not_given_leave_the_mosaickit_config_alone():
    from mosaickit.config import current_config

    assert PlotTheme().mosaickit_config() == current_config()


def test_bad_font_settings_are_named():
    with pytest.raises(ValueError, match="TextFonts"):
        PlotTheme(fonts=str(MATH))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="not a font file"):
        PlotTheme(math_font="/no/such/font.otf")
    with pytest.raises(ValueError, match="MathFont"):
        PlotTheme(math_font=3)  # type: ignore[arg-type]


def test_a_figure_draws_with_the_chosen_fonts(tmp_path):
    theme = PlotTheme(font="serif", fonts=TextFonts(serif=MATH), math_font=MATH)
    figure = MarketFigure(theme=theme, x_max=10, y_max=10)
    assert figure.canvas.config.fonts == theme.fonts
    assert figure.canvas.config.math_font == MathFont(MATH)
    target = tmp_path / "figure.png"
    figure.save(target)
    assert target.stat().st_size > 0
