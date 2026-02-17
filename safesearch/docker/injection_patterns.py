#!/usr/bin/env python3
"""Prompt injection detection patterns for search results.

Each pattern is a tuple of (compiled_regex, reason_label).
Patterns are case-insensitive and scanned against search result titles, URLs, and snippets.
"""
import re


# Layer 1: Regex patterns to flag potential prompt injection in search results.

# just a sample - put your own injection patterns
INJECTION_PATTERNS = [
    (re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I),
     "instruction_override"),
    (re.compile(r"you\s+are\s+now\b|act\s+as\s+(a\s+)?new\s+AI", re.I),
     "role_reset"),
    (re.compile(r"system\s*prompt|<\s*system\s*>", re.I),
     "system_prompt_ref"),
    (re.compile(r"IMPORTANT\s*:.*override|CRITICAL\s*:.*ignore", re.I),
     "directive_override"),
    (re.compile(r"(?:^|\W)(Human|Assistant|Claude)\s*:", re.I),
     "fake_turn_marker"),
    (re.compile(r"<\s*/?\s*(?:instructions|prompt|task|context|system)\s*>", re.I),
     "structural_xml_tag"),
    (re.compile(r"[A-Za-z0-9+/=]{40,}", re.I),
     "base64_blob"),
    (re.compile(r"new\s+instructions\b", re.I),
     "new_instructions"),
    (re.compile(r"\bDAN\b(?=\s+(?:mode|prompt|jailbreak))|(?<!\w)jailbreak|unrestricted\s+mode", re.I),
     "jailbreak_phrase"),
    (re.compile(r"###\s*(?:SYSTEM|INSTRUCTION|PROMPT)", re.I),
     "prompt_boundary_marker"),
    (re.compile(r"do\s+not\s+reveal|forget\s+(all\s+)?previous", re.I),
     "suppression_attempt"),
    (re.compile(r"pretend\s+you\s+are|roleplay\s+as", re.I),
     "role_hijack"),
]
