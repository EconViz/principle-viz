"""Color model definitions for plotting."""

from __future__ import annotations

from dataclasses import dataclass

COLORBLIND_CYCLE_RGB: tuple[tuple[int, int, int], ...] = (
    (55, 126, 184),
    (255, 127, 0),
    (77, 175, 74),
    (247, 129, 191),
    (166, 86, 40),
    (152, 78, 163),
    (153, 153, 153),
    (228, 26, 28),
    (222, 222, 0),
)



def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02X}{g:02X}{b:02X}"


COLORBLIND_CYCLE_HEX: tuple[str, ...] = tuple(_rgb_to_hex(rgb) for rgb in COLORBLIND_CYCLE_RGB)

(
    _CB_BLUE,
    _CB_ORANGE,
    _CB_GREEN,
    _CB_PINK,
    _CB_BROWN,
    _CB_PURPLE,
    _CB_GRAY,
    _CB_RED,
    _CB_YELLOW,
) = COLORBLIND_CYCLE_HEX


@dataclass(frozen=True)
class ColorModel:
    """Named color model for market diagrams."""

    name: str
    axis_color: str = "#222222"
    label_color: str = "#222222"
    demand_color: str = _CB_BLUE
    supply_color: str = _CB_RED
    baseline_color: str = "#111111"
    shifted_color: str = _CB_GREEN
    tax_color: str = _CB_ORANGE
    control_color: str = _CB_PURPLE
    cs_color: str = _CB_GREEN
    ps_color: str = _CB_BLUE
    tax_revenue_color: str = _CB_ORANGE
    dwl_color: str = _CB_RED
    arrow_color: str = "#111111"


_COLORBLIND_BASE = {
    "axis_color": "#222222",
    "label_color": "#222222",
    "demand_color": _CB_BLUE,
    "supply_color": _CB_RED,
    "baseline_color": "#111111",
    "shifted_color": _CB_GREEN,
    "tax_color": _CB_ORANGE,
    "control_color": _CB_PURPLE,
    "cs_color": _CB_GREEN,
    "ps_color": _CB_BLUE,
    "tax_revenue_color": _CB_ORANGE,
    "dwl_color": _CB_RED,
    "arrow_color": "#111111",
}

DEFAULT_COLOR_MODEL = ColorModel(name="default", **_COLORBLIND_BASE)
COLORBLIND_COLOR_MODEL = ColorModel(name="colorblind", **_COLORBLIND_BASE)
NORD_COLOR_MODEL = ColorModel(
    name="nord",
    axis_color="#2E3440",
    label_color="#2E3440",
    demand_color="#88C0D0",
    supply_color="#BF616A",
    shifted_color="#A3BE8C",
    tax_color="#EBCB8B",
    control_color="#B48EAD",
    cs_color="#A3BE8C",
    ps_color="#5E81AC",
    tax_revenue_color="#EBCB8B",
    dwl_color="#BF616A",
    arrow_color="#4C566A",
)
MONOCHROME_COLOR_MODEL = ColorModel(
    name="monochrome",
    axis_color="#111111",
    label_color="#111111",
    demand_color="#111111",
    supply_color="#4A4A4A",
    baseline_color="#000000",
    shifted_color="#6E6E6E",
    tax_color="#2E2E2E",
    control_color="#595959",
    cs_color="#E0E0E0",
    ps_color="#BDBDBD",
    tax_revenue_color="#969696",
    dwl_color="#636363",
    arrow_color="#111111",
)

BUILTIN_COLOR_MODELS: dict[str, ColorModel] = {
    "default": DEFAULT_COLOR_MODEL,
    "colorblind": COLORBLIND_COLOR_MODEL,
    "nord": NORD_COLOR_MODEL,
    "monochrome": MONOCHROME_COLOR_MODEL,
}


def list_color_models() -> tuple[str, ...]:
    """List supported built-in color model names."""
    return tuple(BUILTIN_COLOR_MODELS.keys())


def get_color_model(name: str) -> ColorModel:
    """Resolve a built-in color model by name."""
    key = name.strip().lower()
    if key in BUILTIN_COLOR_MODELS:
        return BUILTIN_COLOR_MODELS[key]
    available = ", ".join(list_color_models())
    raise ValueError(f"Unknown color model: {name}. Available: {available}")


__all__ = [
    "BUILTIN_COLOR_MODELS",
    "COLORBLIND_COLOR_MODEL",
    "COLORBLIND_CYCLE_HEX",
    "COLORBLIND_CYCLE_RGB",
    "DEFAULT_COLOR_MODEL",
    "MONOCHROME_COLOR_MODEL",
    "NORD_COLOR_MODEL",
    "ColorModel",
    "get_color_model",
    "list_color_models",
]
