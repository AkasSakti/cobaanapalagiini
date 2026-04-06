from __future__ import annotations


def _apply_rule(
    details: dict[str, str],
    score: int,
    feature_name: str,
    passed: bool,
    points: int,
    success_reason: str,
    fail_reason: str,
) -> int:
    if passed:
        details[feature_name] = f"+{points} ({success_reason})"
        return score + points

    details[feature_name] = f"0 ({fail_reason})"
    return score


def _score_python(features: dict, score: int, details: dict[str, str]) -> int:
    score = _apply_rule(
        details,
        score,
        "comment_ratio",
        features["comment_ratio"] > 0.3,
        15,
        "high comment ratio",
        "comment ratio not high",
    )
    score = _apply_rule(
        details,
        score,
        "generic_comment_count",
        features["generic_comment_count"] > 3,
        15,
        "many generic comments",
        "few generic comments",
    )
    score = _apply_rule(
        details,
        score,
        "function_count",
        features["function_count"] > 5,
        10,
        "many functions",
        "function count not suspicious",
    )
    score = _apply_rule(
        details,
        score,
        "try_except_count",
        features["try_except_count"] > 2,
        10,
        "many try/except blocks",
        "few try/except blocks",
    )
    score = _apply_rule(
        details,
        score,
        "docstring_count",
        features["docstring_count"] > 2,
        10,
        "many docstrings",
        "few docstrings",
    )
    score = _apply_rule(
        details,
        score,
        "avg_line_length",
        features["avg_line_length"] > 80,
        5,
        "long average line length",
        "average line length normal",
    )
    score = _apply_rule(
        details,
        score,
        "has_debug",
        not features["has_debug"],
        10,
        "no debug statements",
        "contains debug statements",
    )
    score = _apply_rule(
        details,
        score,
        "blank_line_ratio",
        features["blank_line_ratio"] < 0.05,
        5,
        "very compact layout",
        "blank line spacing looks normal",
    )
    return score


def _score_php(features: dict, score: int, details: dict[str, str]) -> int:
    score = _apply_rule(
        details,
        score,
        "comment_ratio",
        features["comment_ratio"] > 0.18,
        10,
        "high comment ratio for PHP web code",
        "comment ratio looks normal",
    )
    score = _apply_rule(
        details,
        score,
        "generic_comment_count",
        features["generic_comment_count"] > 1,
        15,
        "many generic explanatory comments",
        "few generic explanatory comments",
    )
    score = _apply_rule(
        details,
        score,
        "ai_comment_phrase_count",
        features["ai_comment_phrase_count"] > 1,
        10,
        "comment phrasing looks AI-like",
        "comment phrasing not strongly AI-like",
    )
    score = _apply_rule(
        details,
        score,
        "placeholder_text_count",
        features["placeholder_text_count"] > 1,
        10,
        "contains placeholder/demo text",
        "little placeholder text",
    )
    score = _apply_rule(
        details,
        score,
        "generic_identifier_count",
        features["generic_identifier_count"] > 8,
        10,
        "many generic identifiers",
        "identifier naming has more specificity",
    )
    score = _apply_rule(
        details,
        score,
        "repeated_line_ratio",
        features["repeated_line_ratio"] > 0.12,
        10,
        "repeated line patterns are high",
        "line repetition is limited",
    )
    score = _apply_rule(
        details,
        score,
        "docblock_count",
        features["docblock_count"] > 2,
        5,
        "many docblocks for simple PHP file",
        "docblock usage not excessive",
    )
    score = _apply_rule(
        details,
        score,
        "concern_mix_count",
        features["concern_mix_count"] >= 4,
        15,
        "many concerns mixed in one file",
        "concerns are less mixed",
    )
    score = _apply_rule(
        details,
        score,
        "monolithic_page",
        features["monolithic_page"],
        15,
        "single-file full-stack PHP page",
        "structure not strongly monolithic",
    )
    return score


def _score_dart(features: dict, score: int, details: dict[str, str]) -> int:
    score = _apply_rule(
        details,
        score,
        "comment_ratio",
        features["comment_ratio"] > 0.2,
        10,
        "high comment ratio for Dart/Flutter UI code",
        "comment ratio looks normal",
    )
    score = _apply_rule(
        details,
        score,
        "generic_comment_count",
        features["generic_comment_count"] > 1,
        15,
        "many generic explanatory comments",
        "few generic explanatory comments",
    )
    score = _apply_rule(
        details,
        score,
        "ai_comment_phrase_count",
        features["ai_comment_phrase_count"] > 1,
        10,
        "comment phrasing looks AI-like",
        "comment phrasing not strongly AI-like",
    )
    score = _apply_rule(
        details,
        score,
        "placeholder_text_count",
        features["placeholder_text_count"] > 1,
        10,
        "contains placeholder/demo text",
        "little placeholder text",
    )
    score = _apply_rule(
        details,
        score,
        "generic_identifier_count",
        features["generic_identifier_count"] > 8,
        10,
        "many generic identifiers",
        "identifier naming has more specificity",
    )
    score = _apply_rule(
        details,
        score,
        "widget_tree_count",
        features["widget_tree_count"] >= 18,
        10,
        "widget tree is very large in one file",
        "widget tree size is moderate",
    )
    score = _apply_rule(
        details,
        score,
        "named_param_count",
        features["named_param_count"] >= 8,
        5,
        "many boilerplate named parameters",
        "named parameter usage not excessive",
    )
    score = _apply_rule(
        details,
        score,
        "setstate_count",
        features["setstate_count"] >= 3,
        5,
        "frequent setState usage",
        "setState usage is limited",
    )
    score = _apply_rule(
        details,
        score,
        "repeated_line_ratio",
        features["repeated_line_ratio"] > 0.1,
        10,
        "repeated UI line patterns are high",
        "line repetition is limited",
    )
    score = _apply_rule(
        details,
        score,
        "monolithic_widget_file",
        features["monolithic_widget_file"],
        15,
        "single large Flutter widget file",
        "widget structure not strongly monolithic",
    )
    return score


def compute_ai_score(features: dict) -> tuple[int, dict[str, str]]:
    """
    Compute AI likelihood score based on language-aware heuristics.
    Returns: (score, details)
    """
    score = 0
    details: dict[str, str] = {"language": features["language"]}

    if features["language"] == "php":
        score = _score_php(features, score, details)
    elif features["language"] == "dart":
        score = _score_dart(features, score, details)
    else:
        score = _score_python(features, score, details)

    return min(score, 100), details
