from __future__ import annotations

import json

import pytest

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


def test_cli_subsidy_outputs_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "principle-viz",
            "subsidy",
            "--demand-intercept",
            "12",
            "--demand-slope",
            "-1",
            "--supply-intercept",
            "2",
            "--supply-slope",
            "1",
            "--amount",
            "2",
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["post_subsidy"]["q_star"] == 6
    assert payload["post_subsidy"]["government_expenditure"] == 12


def test_cli_revenue_outputs_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "principle-viz",
            "revenue",
            "--demand-intercept",
            "12",
            "--demand-slope",
            "-1",
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["unit_elastic_quantity"] == 6
    assert payload["maximum_revenue"] == 36


def test_cli_trade_outputs_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "principle-viz",
            "trade",
            "--demand-intercept",
            "12",
            "--demand-slope",
            "-1",
            "--supply-intercept",
            "2",
            "--supply-slope",
            "1",
            "--world-price",
            "4",
            "--tariff",
            "2",
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["policy"]["imports"] == 2
    assert payload["policy"]["government_revenue"] == 4
    assert payload["deadweight_loss"] == 4


def test_cli_externality_outputs_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "principle-viz",
            "externality",
            "--demand-intercept",
            "12",
            "--demand-slope",
            "-1",
            "--supply-intercept",
            "2",
            "--supply-slope",
            "1",
            "--external-cost",
            "2",
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["social_equilibrium"]["q_star"] == 4
    assert payload["corrective_tax"] == 2


def test_cli_public_good_outputs_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "principle-viz",
            "public-good",
            "--benefit-intercepts",
            "8",
            "6",
            "--benefit-slopes",
            "-1",
            "-1",
            "--cost-intercept",
            "5",
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["efficient_quantity"] == pytest.approx(4.5)
    assert payload["free_rider_gap"] == pytest.approx(1.5)


def test_cli_minimum_wage_outputs_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "principle-viz",
            "minimum-wage",
            "--labor-demand-intercept",
            "12",
            "--labor-demand-slope",
            "-1",
            "--labor-supply-intercept",
            "2",
            "--labor-supply-slope",
            "1",
            "--minimum-wage",
            "9",
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["employment"] == 3
    assert payload["unemployment"] == 4


def test_cli_loanable_funds_outputs_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "principle-viz",
            "loanable-funds",
            "--savings-intercept",
            "2",
            "--savings-slope",
            "0.5",
            "--investment-intercept",
            "12",
            "--investment-slope",
            "-0.5",
            "--government-borrowing",
            "4",
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["shifted_equilibrium"]["p_star"] == 8
    assert payload["crowding_out"] == 2
