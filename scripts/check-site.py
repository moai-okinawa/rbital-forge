#!/usr/bin/env python3
"""Check the static portfolio without a browser or third-party packages.

This checks source structure and declared colors; it does not verify rendered
layout, actual keyboard behavior, or text placed over images/gradients.
"""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
SUMMARY_BLOCKS = {"address", "article", "aside", "blockquote", "details", "dialog",
                  "div", "dl", "fieldset", "figure", "footer", "form", "header",
                  "hr", "main", "nav", "ol", "p", "pre", "section", "table", "ul"}
URL_PATTERN = re.compile(r"url\(\s*['\"]?([^)'\"\s]+)['\"]?\s*\)", re.I)


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = []
        self.references = []
        self.aria_references = []
        self.images = []
        self.h1_count = 0
        self.stack = []
        self.errors = []
        self.body_text = []

    def error_at(self, message):
        self.errors.append(f"{self.path.name}:{self.getpos()[0]}: {message}")

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "h1":
            self.h1_count += 1
        if "summary" in self.stack and tag in SUMMARY_BLOCKS:
            self.error_at(f"block element <{tag}> inside <summary>")
        if tag in {"a", "link"} and "href" in attrs:
            self.references.append(attrs["href"])
        if tag in {"img", "script", "source"} and "src" in attrs:
            self.references.append(attrs["src"])
        if tag == "img":
            self.images.append(attrs)
            if "alt" not in attrs:
                self.error_at("image is missing alt text (use alt=\"\" for decoration)")
            for key in ("width", "height"):
                value = attrs.get(key, "") or ""
                if not value.isdigit() or int(value) <= 0:
                    self.error_at(f"image needs a positive integer {key}")
        for key in ("aria-controls", "aria-labelledby", "aria-describedby"):
            self.aria_references.extend((attrs.get(key) or "").split())
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self.stack:
            index = len(self.stack) - 1 - self.stack[::-1].index(tag)
            del self.stack[index:]

    def handle_data(self, data):
        # Closed details still contain readable content when expanded. This is
        # a source-content check, not a simulation of CSS visibility.
        if "body" in self.stack and not {"head", "script", "style"}.intersection(self.stack):
            self.body_text.append(data)


def read_page(path):
    page = Page(path)
    page.feed(path.read_text(encoding="utf-8"))
    page.close()
    return page


def check_references(page, errors):
    internal_count = 0
    cached_pages = {page.path: page}
    for reference in page.references:
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc:
            continue  # Remote availability is a separate HTTP check.
        internal_count += 1
        if not reference:
            errors.append(f"{page.path.name}: empty local reference")
            continue
        if parsed.path.startswith("/"):
            target = (DIST / unquote(parsed.path).lstrip("/")).resolve()
        elif parsed.path:
            target = (page.path.parent / unquote(parsed.path)).resolve()
        else:
            target = page.path
        if not target.is_relative_to(DIST):
            errors.append(f"local reference escapes dist/: {reference}")
            continue
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            errors.append(f"missing local resource: {reference}")
            continue
        if parsed.fragment and target.suffix.lower() in {".html", ".htm"}:
            if target not in cached_pages:
                cached_pages[target] = read_page(target)
            if unquote(parsed.fragment) not in cached_pages[target].ids:
                errors.append(f"missing anchor target: {reference}")
    for reference in page.aria_references:
        if reference not in page.ids:
            errors.append(f"missing ARIA target: {reference}")
    return internal_count


def check_svgs(errors):
    files = sorted(DIST.rglob("*.svg"))
    for path in files:
        name = path.relative_to(DIST)
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            errors.append(f"{name}: invalid SVG XML: {exc}")
            continue
        if root.tag.rsplit("}", 1)[-1] != "svg":
            errors.append(f"{name}: root element must be svg")
        ids = [node.attrib["id"] for node in root.iter() if "id" in node.attrib]
        for value, count in Counter(ids).items():
            if count > 1:
                errors.append(f"{name}: duplicate SVG id {value}")
        references = []
        for node in root.iter():
            local_tag = node.tag.rsplit("}", 1)[-1].lower()
            if local_tag in {"script", "foreignobject"}:
                errors.append(f"{name}: active SVG element <{local_tag}> is not allowed")
            for key, value in node.attrib.items():
                local_key = key.rsplit("}", 1)[-1].lower()
                if local_key.startswith("on"):
                    errors.append(f"{name}: SVG event handler {local_key} is not allowed")
                if local_key in {"href", "src"}:
                    references.append(value)
                references.extend(URL_PATTERN.findall(value))
            if local_tag == "style":
                css = "".join(node.itertext())
                references.extend(URL_PATTERN.findall(css))
                if "@import" in css.lower():
                    errors.append(f"{name}: SVG stylesheet imports are not allowed")
        for reference in references:
            if not reference.startswith("#"):
                errors.append(f"{name}: external SVG reference is not allowed: {reference}")
            elif reference[1:] not in ids:
                errors.append(f"{name}: missing internal SVG reference: {reference}")
    return len(files)


def luminance(color):
    value = color.lstrip("#")
    if len(value) == 3:
        value = "".join(channel * 2 for channel in value)
    if len(value) != 6:
        raise ValueError(f"expected a three- or six-digit hex color: {color}")
    channels = [int(value[offset:offset + 2], 16) / 255 for offset in (0, 2, 4)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
              for channel in channels]
    return sum(channel * weight for channel, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def check_contrast(errors):
    css = (DIST / "style.css").read_text(encoding="utf-8")
    root = re.search(r":root\s*\{([^}]+)\}", css)
    if not root:
        errors.append("style.css: missing root color tokens")
        return []
    tokens = dict(re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;", root.group(1)))
    pairs = (("ink", "canvas"), ("body", "canvas"),
             ("body", "canvas-soft"), ("canvas", "primary"))
    results = []
    for foreground, background in pairs:
        if foreground not in tokens or background not in tokens:
            errors.append(f"missing color token for contrast check: {foreground}/{background}")
            continue
        light, dark = sorted((luminance(tokens[foreground]), luminance(tokens[background])), reverse=True)
        ratio = (light + 0.05) / (dark + 0.05)
        results.append(f"{foreground}/{background} {ratio:.2f}:1")
        if ratio < 4.5:
            errors.append(f"text contrast below 4.5:1: {results[-1]}")
    return results


def public_values(value, path="company"):
    """Yield publication content, excluding internal routing/filter keys."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key not in {"id", "category"}:
                yield from public_values(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from public_values(item, f"{path}[{index}]")
    elif isinstance(value, str) or type(value) in {int, float}:
        yield path, str(value)


def normalize_content(value):
    # Layout line breaks, indentation, and inline HTML boundaries must not
    # change whether a Japanese or English content field is present.
    return re.sub(r"\s+", "", value)


def check_company_content(page, errors):
    data = json.loads((ROOT / "content" / "company.json").read_text(encoding="utf-8"))
    text = normalize_content("".join(page.body_text))
    fields = list(public_values(data))
    for path, value in fields:
        expected = normalize_content(value)
        if expected and expected not in text:
            preview = " ".join(value.split())[:100]
            errors.append(f"missing company content in HTML body: {path}: {preview}")
    businesses = data.get("businesses", [])
    achievements = data.get("achievements", [])
    return (f"{len(fields)} publication fields; {len(businesses)} businesses; "
            f"{sum(len(item.get('services', [])) for item in businesses)} services; "
            f"{len(achievements)} achievements; "
            f"{sum(len(item.get('outcomes', [])) for item in achievements)} outcomes")


def main():
    page = read_page(DIST / "index.html")
    errors = list(page.errors)
    for value, count in Counter(page.ids).items():
        if count > 1:
            errors.append(f"duplicate HTML id: {value}")
    if page.h1_count != 1:
        errors.append(f"expected one h1, found {page.h1_count}")
    references = check_references(page, errors)
    svgs = check_svgs(errors)
    contrast = check_contrast(errors)
    content = check_company_content(page, errors)
    if errors:
        print(f"FAIL: {len(errors)} issue(s)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"PASS: HTML structure, {references} local references, {len(page.images)} images, {svgs} SVGs")
    print("Contrast: " + "; ".join(contrast))
    print("Content: " + content)
    print("Source checks only; rendered layout and browser behavior are not verified.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
