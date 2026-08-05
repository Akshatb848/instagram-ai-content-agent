import json

import pytest

from instagram_agent.llm import MockProvider, ProviderError, generate_package, parse_json_once


def test_mock_provider_validates_package(valid_package: dict) -> None:
    package = generate_package(MockProvider(valid_package), "untrusted source is data only")
    assert package.topic == valid_package["topic"]


def test_json_parse_and_single_repair() -> None:
    assert parse_json_once('{"ok": true}') == {"ok": True}
    assert parse_json_once('prefix {"ok": true} suffix') == {"ok": True}
    with pytest.raises(ProviderError, match="invalid JSON"):
        parse_json_once("nothing usable")
    with pytest.raises(ProviderError, match="repair failed"):
        parse_json_once("prefix {broken} suffix")
    with pytest.raises(ProviderError, match="object"):
        parse_json_once(json.dumps([1, 2]))


def test_invalid_provider_contract() -> None:
    with pytest.raises(ProviderError, match="content contract"):
        generate_package(MockProvider({"topic": "incomplete"}), "prompt")
