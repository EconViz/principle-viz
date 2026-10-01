from __future__ import annotations

import json

from principle_viz.cli.main import main


def test_cli_equilibrium_outputs_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "principle-viz",
            "equilibrium",
            "--demand-intercept",
            "10",
            "--demand-slope",
            "-1",
            "--supply-intercept",
            "2",
            "--supply-slope",
            "1",
        ],
    )
    main()
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert "q_star" in payload
    assert "p_star" in payload


def test_cli_tax_outputs_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "principle-viz",
            "tax",
            "--demand-intercept",
            "10",
            "--demand-slope",
            "-1",
            "--supply-intercept",
            "2",
            "--supply-slope",
            "1",
            "--tax-type",
            "per_unit",
            "--amount",
            "1",
            "--tax-on",
            "producer",
        ],
    )
    main()
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert "post_tax" in payload
    assert "delta_q" in payload


def test_cli_discrete_outputs_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "principle-viz",
            "discrete",
            "--demand-values",
            "11",
            "9",
            "7",
            "5",
            "--supply-values",
            "1",
            "3",
            "5",
            "8",
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["q_star"] == 3
    assert payload["price_low"] == 5
    assert payload["price_high"] == 7
    assert payload["price_rule"] == "midpoint"
