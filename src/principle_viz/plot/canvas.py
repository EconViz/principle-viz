"""Canvas model for first-quadrant market diagrams."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from principle_viz.plot.theme import PlotTheme


class Canvas:
    """Single plotting canvas with econ-diagram defaults."""

    def __init__(
        self,
        x_max: float = 20.0,
        y_max: float = 20.0,
        x_label: str = "Q",
        y_label: str = "P",
        title: str | None = "Market Diagram",
        theme: PlotTheme | None = None,
        fig=None,
        ax=None,
    ) -> None:
        self.theme = theme or PlotTheme()
        self.x_max = float(x_max)
        self.y_max = float(y_max)
        self.x_label = x_label
        self.y_label = y_label
        self.title = title

        self._owns_figure = fig is None or ax is None
        if fig is None or ax is None:
            self.fig, self.ax = plt.subplots(figsize=(7.2, 5.2))
        else:
            self.fig, self.ax = fig, ax

        self._apply_base_style()

    def _apply_base_style(self) -> None:
        """Apply base styling similar to econ-viz canvas conventions."""
        t = self.theme

        self.ax.set_xlim(0.0, self.x_max)
        self.ax.set_ylim(0.0, self.y_max)

        self.ax.set_xlabel(self.x_label, color=t.label_color)
        self.ax.set_ylabel(self.y_label, color=t.label_color)
        if self.title:
            self.ax.set_title(self.title, color=t.label_color)

        if not t.show_ticks:
            self.ax.set_xticklabels([])
            self.ax.set_yticklabels([])
            self.ax.tick_params(length=0)

        self.ax.grid(t.show_grid)

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_color(t.axis_color)
        self.ax.spines["left"].set_color(t.axis_color)

        if t.show_origin_label:
            self.ax.text(
                -self.x_max * 0.03,
                -self.y_max * 0.03,
                "0",
                ha="right",
                va="top",
                color=t.label_color,
            )

        if t.show_axis_arrows:
            self.ax.plot(self.x_max, 0.0, ">", color=t.axis_color, markersize=7, clip_on=False)
            self.ax.plot(0.0, self.y_max, "^", color=t.axis_color, markersize=7, clip_on=False)

        self.fig.patch.set_alpha(0.0)
        self.ax.patch.set_alpha(0.0)

    def finalize(self, legend: bool = True) -> Canvas:
        """Finalize layout and optional legend."""
        if legend:
            self.ax.legend(loc="best", fancybox=False)
        self.fig.tight_layout()
        return self

    def save(self, path: str, dpi: int = 150, close: bool = False) -> None:
        """Save figure to file."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.fig.savefig(target, dpi=dpi, bbox_inches="tight")
        if close:
            self.close()

    def close(self) -> None:
        """Close owned figure."""
        if self._owns_figure:
            plt.close(self.fig)
