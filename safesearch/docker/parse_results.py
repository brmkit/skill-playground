#!/usr/bin/env python3
"""Parse DuckDuckGo HTML search results from stdin.

Handles both html.duckduckgo.com and lite.duckduckgo.com formats.
"""
import sys
import urllib.parse
from html.parser import HTMLParser
from injection_patterns import INJECTION_PATTERNS


def flag_result(result):
    """Scan a result dict for injection patterns. Mutates in-place, returns it.

    Appends [⚠ FLAGGED: reason1, reason2] to any field that matches.
    The base64_blob pattern is skipped for the 'url' field to avoid false positives.
    """
    for field in ("title", "url", "snippet"):
        text = result.get(field, "")
        if not text:
            continue
        reasons = []
        for pattern, reason in INJECTION_PATTERNS:
            # Skip base64 check on URLs — too many false positives from path segments
            if reason == "base64_blob" and field == "url":
                continue
            if pattern.search(text):
                reasons.append(reason)
        if reasons:
            result[field] = f"{text} [⚠ FLAGGED: {', '.join(reasons)}]"
    return result


class DDGParser(HTMLParser):
    """Parser for html.duckduckgo.com/html/ format."""

    def __init__(self):
        super().__init__()
        self.results = []
        self.current = {}
        self.capture = None
        self.in_result = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        # Main result container
        if tag == "div" and "result" in cls and "results_links" in cls:
            self.in_result = True
            self.current = {"title": "", "url": "", "snippet": ""}
        if not self.in_result:
            return
        # Title link
        if tag == "a" and "result__a" in cls:
            self.capture = "title"
            href = attrs_dict.get("href", "")
            if "uddg=" in href:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                self.current["url"] = parsed.get("uddg", [href])[0]
            else:
                self.current["url"] = href
        # Snippet (can be <a> or <td> with class result__snippet)
        elif "result__snippet" in cls:
            self.capture = "snippet"

    def handle_endtag(self, tag):
        if self.capture == "title" and tag == "a":
            self.capture = None
        if self.capture == "snippet" and tag in ("a", "td", "span", "div"):
            self.capture = None
        if self.in_result and tag == "div":
            if self.current.get("title"):
                self.results.append(self.current)
                self.current = {}
                self.in_result = False

    def handle_data(self, data):
        if self.capture == "title":
            self.current["title"] += data.strip()
        elif self.capture == "snippet":
            self.current["snippet"] += data.strip() + " "


class DDGLiteParser(HTMLParser):
    """Parser for lite.duckduckgo.com/lite/ format.

    The lite format uses a table layout:
    - <a class="result-link"> for title+URL
    - <td class="result-snippet"> for snippet
    - <span class="link-text"> for display URL
    """

    def __init__(self):
        super().__init__()
        self.results = []
        self.current = {}
        self.capture = None
        self.in_link = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        if tag == "a" and "result-link" in cls:
            self.current = {"title": "", "url": "", "snippet": ""}
            href = attrs_dict.get("href", "")
            if "uddg=" in href:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                self.current["url"] = parsed.get("uddg", [href])[0]
            else:
                self.current["url"] = href
            self.capture = "title"
            self.in_link = True
        elif tag == "td" and "result-snippet" in cls:
            self.capture = "snippet"

    def handle_endtag(self, tag):
        if self.capture == "title" and tag == "a":
            self.capture = None
            self.in_link = False
        if self.capture == "snippet" and tag == "td":
            self.capture = None
            if self.current.get("title"):
                self.results.append(self.current)
                self.current = {}

    def handle_data(self, data):
        if self.capture == "title":
            self.current["title"] += data.strip()
        elif self.capture == "snippet":
            self.current["snippet"] += data.strip() + " "


def main():
    html_content = sys.stdin.read()

    # Try standard parser first
    parser = DDGParser()
    parser.feed(html_content)
    results = parser.results

    # If no results, try lite parser
    if not results:
        lite_parser = DDGLiteParser()
        lite_parser.feed(html_content)
        results = lite_parser.results

    if not results:
        print("No results found.")
        print("DuckDuckGo may have blocked the request or the query returned empty.")
        sys.exit(0)

    for i, r in enumerate(results[:15], 1):
        r = flag_result(r)
        title = r["title"]
        url = r["url"]
        snippet = r["snippet"].strip()
        print(f"## Result {i}: {title}")
        print(f"URL: {url}")
        if snippet:
            print(f"{snippet}")
        print()


if __name__ == "__main__":
    main()
