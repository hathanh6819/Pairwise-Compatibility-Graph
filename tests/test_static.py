import ast
import os
import py_compile
import sys

CONTRACT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "contracts", "pairwise_compatibility_graph.py"
    )
)


def test_header_lines():
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        lines = [f.readline() for _ in range(3)]

    assert (
        lines[0].strip() == "# v0.2.16"
    ), f"Line 1 must be '# v0.2.16', got '{lines[0].strip()}'"
    assert (
        lines[1].strip()
        == '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }'
    ), f"Line 2 runner comment mismatch: '{lines[1].strip()}'"
    assert (
        lines[2].strip() == "from genlayer import *"
    ), f"Line 3 must be 'from genlayer import *', got '{lines[2].strip()}'"
    print("[PASS] Header verification")


def test_ascii_scan():
    with open(CONTRACT_PATH, "rb") as f:
        content = f.read()

    non_ascii_indices = [
        (i, byte) for i, byte in enumerate(content) if byte > 127
    ]
    assert (
        len(non_ascii_indices) == 0
    ), f"Found {len(non_ascii_indices)} non-ASCII bytes in contract source: {non_ascii_indices[:5]}"
    print("[PASS] Pure ASCII scan")


def test_ast_parse():
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        ast.parse(source)
    except SyntaxError as e:
        assert False, f"AST Parse failed with SyntaxError: {e}"

    py_compile.compile(CONTRACT_PATH, doraise=True)
    print("[PASS] AST compilation check")


if __name__ == "__main__":
    test_header_lines()
    test_ascii_scan()
    test_ast_parse()
    print("ALL STATIC TESTS PASSED SUCCESSFULLY.")
