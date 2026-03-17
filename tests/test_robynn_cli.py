from __future__ import annotations

from robynn import _resolve_run_input, build_parser


def test_run_accepts_trailing_prompt_text():
    parser = build_parser()
    args = parser.parse_args(["run", "cmo", "Write", "a", "launch", "post"])

    assert args.agent == "cmo"
    assert _resolve_run_input(args) == "Write a launch post"


def test_login_alias_accepts_api_key_argument():
    parser = build_parser()
    args = parser.parse_args(["login", "rb_test_123"])

    assert args.command == "login"
    assert args.api_key == "rb_test_123"
