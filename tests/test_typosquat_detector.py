from __future__ import annotations

import pytest

from typosquat_detector import (
    POPULAR,
    Finding,
    TyposquatError,
    check,
    normalize,
    osa_distance,
)
from typosquat_detector.__main__ import main


def test_check_distance_transposition() -> None:
    assert check("reqeusts") == [Finding(rule="distance", target="requests", candidate="reqeusts")]


def test_check_same_name_returns_empty() -> None:
    assert check("requests") == []
    # PEP 503 normalisation makes 'Requests' the same package
    assert check("Requests") == []


def test_check_separator_rule_reported_once() -> None:
    result = check("pythondateutil")
    assert result == [
        Finding(rule="separator", target="python-dateutil", candidate="pythondateutil")
    ]
    # distance would also be 1, but separator wins
    assert len(result) == 1


def test_check_homoglyph_django_and_boto3() -> None:
    assert check("djang0") == [Finding(rule="homoglyph", target="django", candidate="djang0")]
    assert check("b0to3") == [Finding(rule="homoglyph", target="boto3", candidate="b0to3")]


def test_check_affix_rule() -> None:
    assert check("requests-python") == [
        Finding(rule="affix", target="requests", candidate="requests-python")
    ]


def test_check_short_name_excluded_from_distance() -> None:
    # 'six' has length 3, so distance rule is not applied
    assert check("sixx") == []


def test_check_npm_distance() -> None:
    assert check("lodahs", ecosystem="npm") == [
        Finding(rule="distance", target="lodash", candidate="lodahs")
    ]
    assert check("lodash", ecosystem="npm") == []


def test_invalid_ecosystem_raises() -> None:
    with pytest.raises(TyposquatError) as exc_info:
        check("x", ecosystem="maven")
    assert exc_info.value.code == "invalid_ecosystem"


def test_osa_distance_known_values() -> None:
    assert osa_distance("reqeusts", "requests") == 1
    assert osa_distance("abc", "ca") == 3
    assert osa_distance("", "abc") == 3


def test_input_too_large() -> None:
    with pytest.raises(TyposquatError) as exc_info:
        check("a" * 215)
    assert exc_info.value.code == "input_too_large"
    # 214 characters should be accepted (no input_too_large error)
    assert check("a" * 214) == []


def test_invalid_name_regex() -> None:
    with pytest.raises(TyposquatError) as exc_info:
        check("bad name!")
    assert exc_info.value.code == "invalid_name"


def test_custom_popular_list_and_scoped_npm() -> None:
    # rn->m homoglyph with custom list
    assert check("rnoment", ecosystem="npm", popular=["moment"]) == [
        Finding(rule="homoglyph", target="moment", candidate="rnoment")
    ]
    # scoped npm name
    assert check(
        "@scope/rnoment",
        ecosystem="npm",
        popular=["@scope/moment"],
    ) == [Finding(rule="homoglyph", target="@scope/moment", candidate="@scope/rnoment")]


def test_check_multiple_targets() -> None:
    result = check("fooba", ecosystem="pypi", popular=["foobar", "foobaz"])
    assert result == [
        Finding(rule="distance", target="foobar", candidate="fooba"),
        Finding(rule="distance", target="foobaz", candidate="fooba"),
    ]


def test_popular_constant_no_close_pairs() -> None:
    for ecosystem, names in POPULAR.items():
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                if len(a) >= 4 and len(b) >= 4:
                    assert osa_distance(a, b) > 1, f"{a} and {b} are too close in {ecosystem}"


def test_normalize_pypi() -> None:
    assert normalize("Requests") == "requests"
    assert normalize("Python-DateUtil") == "python-dateutil"
    assert normalize("foo__bar..baz") == "foo-bar-baz"


def test_normalize_npm() -> None:
    assert normalize("Lodash", "npm") == "lodash"
    assert normalize("lodash", "npm") == "lodash"


def test_normalize_invalid_ecosystem() -> None:
    with pytest.raises(TyposquatError) as exc_info:
        normalize("x", "invalid")
    assert exc_info.value.code == "invalid_ecosystem"


def test_main_findings() -> None:
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        ret = main(["reqeusts", "flask"])
    assert ret == 1
    assert buf.getvalue() == "reqeusts: distance -> requests\n"


def test_main_no_findings() -> None:
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        ret = main(["flask"])
    assert ret == 0
    assert buf.getvalue() == ""


def test_main_npm_ecosystem() -> None:
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        ret = main(["--ecosystem", "npm", "lodahs"])
    assert ret == 1
    assert "lodahs: distance -> lodash" in buf.getvalue()


def test_main_no_arguments_returns_2() -> None:
    ret = main([])
    assert ret == 2


def test_main_invalid_name_returns_2() -> None:
    ret = main(["bad name!"])
    assert ret == 2


def test_main_with_popular_file(tmp_path) -> None:
    popular_file = tmp_path / "popular.txt"
    popular_file.write_text("moment\n", encoding="utf-8")
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        ret = main(["--popular", str(popular_file), "rnoment"])
    assert ret == 1
    assert "rnoment: homoglyph -> moment" in buf.getvalue()


def test_main_popular_file_missing_returns_2(tmp_path) -> None:
    missing = tmp_path / "nope.txt"
    ret = main(["--popular", str(missing), "foo"])
    assert ret == 2


def test_invalid_name_trailing_newline_pypi() -> None:
    for name in ("requests\n", "reqeusts\n"):
        with pytest.raises(TyposquatError) as exc_info:
            check(name)
        assert exc_info.value.code == "invalid_name"


def test_invalid_name_trailing_newline_npm() -> None:
    for name in ("lodash\n", "lodahs\n"):
        with pytest.raises(TyposquatError) as exc_info:
            check(name, ecosystem="npm")
        assert exc_info.value.code == "invalid_name"


def test_check_case_insensitive_detection() -> None:
    assert check("Reqeusts") == [Finding(rule="distance", target="requests", candidate="Reqeusts")]
    assert check("Pythondateutil") == [
        Finding(rule="separator", target="python-dateutil", candidate="Pythondateutil")
    ]
    assert check("Lodahs", ecosystem="npm") == [
        Finding(rule="distance", target="lodash", candidate="Lodahs")
    ]


def test_main_popular_file_not_utf8_returns_2(tmp_path) -> None:
    popular_file = tmp_path / "popular.bin"
    popular_file.write_bytes(b"\xff\xfe\n")
    assert main(["--popular", str(popular_file), "reqeusts"]) == 2
