import ast
import re
from collections import Counter
from typing import Iterable


GENERIC_COMMENT_KEYWORDS = (
    "initialize",
    "process",
    "function",
    "calculate",
    "loop through",
    "handle form submission",
    "validate input",
    "connect to the database",
    "fetch data",
    "display the result",
    "check if the form is submitted",
)

PLACEHOLDER_PATTERNS = (
    "lorem ipsum",
    "sample data",
    "dummy data",
    "your api key",
    "your database",
    "your password",
    "your username",
    "your email",
    "example.com",
    "enter your",
    "insert your",
    "replace with your",
)

GENERIC_IDENTIFIER_PATTERNS = (
    "data",
    "result",
    "temp",
    "value",
    "item",
    "items",
    "response",
    "payload",
    "userData",
    "resultData",
    "dataList",
    "info",
)


def infer_language(code: str, filename: str | None = None) -> str:
    if filename:
        lowered = filename.lower()
        if lowered.endswith(".py"):
            return "python"
        if lowered.endswith(".php"):
            return "php"
        if lowered.endswith(".dart"):
            return "dart"

    if "<?php" in code or re.search(r"\$_(POST|GET|REQUEST|SESSION|COOKIE|FILES|SERVER)\b", code):
        return "php"
    if re.search(r"\bimport\s+'package:flutter/|extends\s+(StatelessWidget|StatefulWidget)|\bWidget\s+build\s*\(", code):
        return "dart"
    return "python"


def _safe_ratio(numerator: int | float, denominator: int | float) -> float:
    return numerator / denominator if denominator else 0.0


def _average(values: Iterable[int]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def _extract_line_comments(lines: list[str], language: str) -> list[str]:
    comment_texts: list[str] = []
    in_block_comment = False
    block_buffer: list[str] = []

    for raw_line in lines:
        line = raw_line.strip()

        if in_block_comment:
            block_buffer.append(line)
            if "*/" in line:
                joined = " ".join(block_buffer)
                comment_texts.append(re.sub(r"^/\*+|\*/$", "", joined).strip())
                block_buffer = []
                in_block_comment = False
            continue

        if line.startswith('"""') or line.startswith("'''"):
            comment_texts.append(line.strip("\"' ").strip())
            continue

        if language == "python":
            if line.startswith("#"):
                comment_texts.append(line[1:].strip())
            continue

        if line.startswith("//") or line.startswith("#"):
            comment_texts.append(line[2:].strip() if line.startswith("//") else line[1:].strip())
            continue

        if line.startswith("/*") or line.startswith("/**"):
            in_block_comment = True
            block_buffer = [line]
            if "*/" in line:
                joined = " ".join(block_buffer)
                comment_texts.append(re.sub(r"^/\*+|\*/$", "", joined).strip())
                block_buffer = []
                in_block_comment = False

    return [text.lower() for text in comment_texts if text]


def _count_generic_comments(comment_texts: list[str]) -> tuple[int, int]:
    generic_count = 0
    ai_phrase_count = 0
    for text in comment_texts:
        if any(keyword in text for keyword in GENERIC_COMMENT_KEYWORDS):
            generic_count += 1
        if any(
            phrase in text
            for phrase in (
                "this function",
                "this code",
                "the following",
                "ensure that",
                "in order to",
                "handle the",
                "display the",
            )
        ):
            ai_phrase_count += 1
    return generic_count, ai_phrase_count


def _count_generic_identifiers(code: str) -> int:
    matches = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]{2,}\b", code)
    lowered = [match.lower() for match in matches]
    return sum(1 for token in lowered if token in {name.lower() for name in GENERIC_IDENTIFIER_PATTERNS})


def _repeated_line_ratio(lines: list[str]) -> float:
    normalized = [
        re.sub(r"\s+", " ", line.strip()).lower()
        for line in lines
        if line.strip() and len(line.strip()) > 8
    ]
    if not normalized:
        return 0.0

    counts = Counter(normalized)
    repeated = sum(count - 1 for count in counts.values() if count > 1)
    return _safe_ratio(repeated, len(normalized))


def _extract_python_features(code: str) -> dict:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "function_count": 0,
            "class_count": 0,
            "try_except_count": 0,
            "docstring_count": 0,
            "syntax_ok": False,
        }

    function_count = sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
    class_count = sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    try_except_count = sum(isinstance(node, ast.Try) for node in ast.walk(tree))
    docstring_count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)) and ast.get_docstring(node):
            docstring_count += 1

    return {
        "function_count": function_count,
        "class_count": class_count,
        "try_except_count": try_except_count,
        "docstring_count": docstring_count,
        "syntax_ok": True,
    }


def _extract_php_features(code: str, lines: list[str], total_lines: int) -> dict:
    function_count = len(re.findall(r"\bfunction\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(", code))
    class_count = len(re.findall(r"\bclass\s+[a-zA-Z_][a-zA-Z0-9_]*\b", code))
    docblock_count = len(re.findall(r"/\*\*[\s\S]*?\*/", code))
    php_block_count = code.count("<?php")
    form_signal_count = len(re.findall(r"\$_(POST|GET|REQUEST|FILES)\b|<form\b|method\s*=\s*[\"']post[\"']", code, re.IGNORECASE))
    db_query_count = len(re.findall(r"\b(mysqli_query|->query|->prepare|prepare\s*\(|PDO\s*\(|SELECT\s+.+\s+FROM)\b", code, re.IGNORECASE))
    superglobal_count = len(re.findall(r"\$_(POST|GET|REQUEST|SESSION|COOKIE|FILES|SERVER)\b", code))
    inline_css = bool(re.search(r"<style\b", code, re.IGNORECASE))
    inline_js = bool(re.search(r"<script\b", code, re.IGNORECASE))
    has_html = bool(re.search(r"<(?:html|body|div|form|table|section|main|head)\b", code, re.IGNORECASE))
    mixed_php_html = "<?php" in code and has_html
    concern_mix_count = sum(
        [
            mixed_php_html,
            form_signal_count > 0,
            db_query_count > 0,
            inline_css,
            inline_js,
            superglobal_count > 0,
        ]
    )
    monolithic_page = bool(
        total_lines >= 50
        and mixed_php_html
        and function_count <= 2
        and concern_mix_count >= 4
    )

    return {
        "function_count": function_count,
        "class_count": class_count,
        "docblock_count": docblock_count,
        "php_block_count": php_block_count,
        "form_signal_count": form_signal_count,
        "db_query_count": db_query_count,
        "superglobal_count": superglobal_count,
        "inline_css": inline_css,
        "inline_js": inline_js,
        "mixed_php_html": mixed_php_html,
        "concern_mix_count": concern_mix_count,
        "monolithic_page": monolithic_page,
    }


def _extract_dart_features(code: str, lines: list[str], total_lines: int) -> dict:
    function_count = len(re.findall(r"\b(?:[A-Z_a-z][\w<>?]*\s+)+([a-zA-Z_]\w*)\s*\([^;{}]*\)\s*\{", code))
    class_count = len(re.findall(r"\bclass\s+[A-Z_a-z]\w*\b", code))
    widget_class_count = len(re.findall(r"\bextends\s+(?:StatelessWidget|StatefulWidget|State<[^>]+>)", code))
    build_method_count = len(re.findall(r"\bWidget\s+build\s*\(\s*BuildContext\b", code))
    setstate_count = len(re.findall(r"\bsetState\s*\(", code))
    async_count = len(re.findall(r"\basync\b", code))
    future_builder_count = len(re.findall(r"\bFutureBuilder\s*<|\bStreamBuilder\s*<", code))
    controller_count = len(re.findall(r"\b(?:TextEditingController|AnimationController|ScrollController)\b", code))
    widget_tree_count = len(
        re.findall(
            r"\b(?:Scaffold|Container|Column|Row|ListView|GridView|Padding|Center|Text|Card|ListTile|SizedBox|ElevatedButton|TextField|AppBar)\s*\(",
            code,
        )
    )
    named_param_count = len(re.findall(r"\brequired\s+this\.\w+|this\.\w+\s*,", code))
    const_constructor_count = len(re.findall(r"\bconst\s+[A-Z]\w*\s*\(", code))
    flutter_import = bool(re.search(r"\bimport\s+'package:flutter/", code))
    monolithic_widget_file = bool(
        total_lines >= 120
        and widget_tree_count >= 18
        and class_count <= 3
        and build_method_count >= 1
    )

    return {
        "function_count": function_count,
        "class_count": class_count,
        "widget_class_count": widget_class_count,
        "build_method_count": build_method_count,
        "setstate_count": setstate_count,
        "async_count": async_count,
        "future_builder_count": future_builder_count,
        "controller_count": controller_count,
        "widget_tree_count": widget_tree_count,
        "named_param_count": named_param_count,
        "const_constructor_count": const_constructor_count,
        "flutter_import": flutter_import,
        "monolithic_widget_file": monolithic_widget_file,
    }


def extract_features(code: str, filename: str | None = None) -> dict:
    """
    Extract language-aware heuristic features for AI code detection.
    """
    language = infer_language(code, filename)
    lines = code.splitlines()
    total_lines = len(lines)
    non_empty_lines = [line for line in lines if line.strip()]

    if total_lines == 0:
        return {
            "language": language,
            "total_lines": 0,
            "comment_ratio": 0.0,
            "generic_comment_count": 0,
            "ai_comment_phrase_count": 0,
            "function_count": 0,
            "class_count": 0,
            "has_debug": False,
            "avg_line_length": 0.0,
            "blank_line_ratio": 0.0,
            "placeholder_text_count": 0,
            "generic_identifier_count": 0,
            "repeated_line_ratio": 0.0,
        }

    comment_texts = _extract_line_comments(lines, language)
    comment_lines = len(comment_texts)
    generic_comment_count, ai_comment_phrase_count = _count_generic_comments(comment_texts)
    placeholder_text_count = sum(code.lower().count(pattern) for pattern in PLACEHOLDER_PATTERNS)
    has_debug = bool(
        re.search(r"\b(print|var_dump|dump|dd|console\.log)\s*\(", code)
        or "debug" in code.lower()
    )

    features = {
        "language": language,
        "total_lines": total_lines,
        "comment_ratio": _safe_ratio(comment_lines, total_lines),
        "generic_comment_count": generic_comment_count,
        "ai_comment_phrase_count": ai_comment_phrase_count,
        "has_debug": has_debug,
        "avg_line_length": _average(len(line) for line in non_empty_lines),
        "blank_line_ratio": _safe_ratio(total_lines - len(non_empty_lines), total_lines),
        "placeholder_text_count": placeholder_text_count,
        "generic_identifier_count": _count_generic_identifiers(code),
        "repeated_line_ratio": _repeated_line_ratio(lines),
    }

    if language == "php":
        features.update(_extract_php_features(code, lines, total_lines))
    elif language == "dart":
        features.update(_extract_dart_features(code, lines, total_lines))
    else:
        features.update(_extract_python_features(code))

    return features
