import argparse
import csv
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Set


def strip_namespace(tag: str) -> str:
    """Remove XML namespace from tag."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def safe_filename(name: str) -> str:
    """Make a page title safe for saving as a filename."""
    name = name.replace("/", "_").replace("\\", "_").strip()
    name = re.sub(r"\s+", " ", name)
    return name


def load_city_filter(csv_path: Optional[str]) -> Optional[Set[str]]:
    """
    Load allowed city titles from a CSV file.
    Expected to contain at least a 'city' column.
    """
    if not csv_path:
        return None

    allowed = set()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "city" not in reader.fieldnames:
            raise ValueError(f"'city' column not found in {csv_path}")
        for row in reader:
            city = (row.get("city") or "").strip()
            if city:
                allowed.add(city)
    return allowed


def clean_wikitext(text: str) -> str:
    """
    Lightweight wikitext cleanup while preserving == section == headings.
    This is intentionally simple and robust enough for downstream chunking.
    """
    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # Remove <ref>...</ref> and self-closing refs
    text = re.sub(r"<ref[^>/]*?>.*?</ref>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<ref[^/]*/\s*>", "", text, flags=re.IGNORECASE)

    # Remove some HTML tags but keep text content
    text = re.sub(r"</?(small|span|div|center|blockquote|gallery|code|nowiki|sup|sub)[^>]*>", "", text, flags=re.IGNORECASE)

    # Remove tables {| ... |}
    text = re.sub(r"\{\|.*?\|\}", "", text, flags=re.DOTALL)

    # Remove categories/files/images
    text = re.sub(r"\[\[(Category|File|Image):.*?\]\]", "", text, flags=re.IGNORECASE)

    # Convert external links: [url label] -> label
    text = re.sub(r"\[https?://[^\s\]]+\s+([^\]]+)\]", r"\1", text)
    text = re.sub(r"\[https?://[^\]]+\]", "", text)

    # Convert wikilinks: [[A|B]] -> B, [[A]] -> A
    text = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)

    # Remove bold/italic markup
    text = text.replace("'''", "").replace("''", "")

    # Remove templates {{...}} iteratively (best-effort, nested-safe enough for many cases)
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\{\{[^{}]*\}\}", "", text)

    # Remove leftover HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Keep headings intact, but clean extra spaces around them
    cleaned_lines = []
    for line in text.split("\n"):
        line = line.rstrip()

        # Preserve headings like == Understand ==
        if re.match(r"^\s*==[^=].*?==\s*$", line):
            heading = re.sub(r"\s+", " ", line.strip())
            cleaned_lines.append(heading)
            continue

        # Skip list/table markup and wiki artifacts lines that are mostly syntax
        if re.match(r"^\s*[\*\#\:\;]+\s*$", line):
            continue

        # Remove leading list markers but keep content
        line = re.sub(r"^\s*[\*\#\:\;]+\s*", "", line)

        # Collapse internal whitespace
        line = re.sub(r"\s+", " ", line).strip()

        if line:
            cleaned_lines.append(line)

    # Remove repeated blank lines by rebuilding with single newlines
    text = "\n".join(cleaned_lines)

    # Final cleanup
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text


def should_keep_page(title: str, ns_text: str, is_redirect: bool, allowed_cities: Optional[Set[str]]) -> bool:
    """Heuristic filter for city pages."""
    if ns_text != "0":
        return False
    if is_redirect:
        return False
    if not title:
        return False

    # Exclude obvious non-article namespaces that may still leak in malformed dumps
    if ":" in title:
        return False

    # If a city filter is provided, only keep those exact titles
    if allowed_cities is not None:
        return title in allowed_cities

    # Otherwise keep all namespace-0 non-redirect pages
    return True


def extract_pages(xml_path: str, out_dir: str, city_csv: Optional[str] = None) -> None:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    allowed_cities = load_city_filter(city_csv)

    kept = 0
    total = 0

    context = ET.iterparse(xml_path, events=("start", "end"))
    _, root = next(context)

    current = {
        "title": None,
        "ns": None,
        "redirect": False,
        "text": None,
    }

    for event, elem in context:
        tag = strip_namespace(elem.tag)

        if event == "start" and tag == "page":
            current = {
                "title": None,
                "ns": None,
                "redirect": False,
                "text": None,
            }

        elif event == "end":
            if tag == "title":
                current["title"] = elem.text or ""
            elif tag == "ns":
                current["ns"] = elem.text or ""
            elif tag == "redirect":
                current["redirect"] = True
            elif tag == "text":
                current["text"] = elem.text or ""
            elif tag == "page":
                total += 1

                title = (current["title"] or "").strip()
                ns_text = (current["ns"] or "").strip()
                is_redirect = current["redirect"]
                raw_text = current["text"] or ""

                if should_keep_page(title, ns_text, is_redirect, allowed_cities):
                    cleaned = clean_wikitext(raw_text)

                    # Only save non-empty cleaned pages
                    if cleaned:
                        filename = safe_filename(title) + ".txt"
                        file_path = out_path / filename
                        file_path.write_text(cleaned, encoding="utf-8")
                        kept += 1

                elem.clear()
                root.clear()

    print(f"Finished. Total pages seen: {total}")
    print(f"Saved cleaned pages: {kept}")
    print(f"Output directory: {out_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Extract cleaned Wikivoyage city pages from a MediaWiki XML dump.")
    parser.add_argument(
        "--xml",
        required=True,
        help="Path to wikivoyage-pages-articles.xml"
    )
    parser.add_argument(
        "--out",
        default="./european-city-data/data-sources/wikivoyage/cleaned",
        help="Output directory for cleaned city text files"
    )
    parser.add_argument(
        "--city-csv",
        default=None,
        help="Optional CSV with a 'city' column. If provided, only those city titles are kept."
    )

    args = parser.parse_args()

    extract_pages(
        xml_path=args.xml,
        out_dir=args.out,
        city_csv=args.city_csv,
    )


if __name__ == "__main__":
    main()