import argparse
import os
import re
import shutil
import time
from datetime import datetime
from pathlib import Path


DEFAULT_SOURCE = Path(r"C:\Users\oprio\Documents\git_obsidian\notes")
DEFAULT_POSTS = Path(r"C:\Users\oprio\Documents\_website\_posts")
PUBLISH_KEYS = ("publish", "published", "status")


def parse_simple_frontmatter(frontmatter_text):
    """Parse basic frontmatter without external dependencies."""
    result = {}
    for raw_line in frontmatter_text.strip().split("\n"):
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue

        key, value = [x.strip() for x in line.split(":", 1)]
        value = value.strip("'\"")
        lowered = value.lower()

        if lowered == "true":
            parsed_value = True
        elif lowered == "false":
            parsed_value = False
        elif lowered in ("null", "none", ""):
            parsed_value = None
        else:
            parsed_value = value

        result[key] = parsed_value

    return result


def extract_frontmatter(content):
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    return parse_simple_frontmatter(match.group(1))


def format_date_for_jekyll(date_string):
    if not isinstance(date_string, str):
        return datetime.now().strftime("%Y-%m-%d")

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(date_string, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return datetime.now().strftime("%Y-%m-%d")


def slugify(title):
    slug = re.sub(r"[^\w\s-]", "", str(title).lower())
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def is_published(frontmatter):
    for key in PUBLISH_KEYS:
        value = frontmatter.get(key)
        lowered = str(value).lower()
        if value is True or lowered == "true":
            return True
        if key == "status" and lowered == "published":
            return True
    return False


def build_destination_filename(source_path, frontmatter):
    title = frontmatter.get("title") or source_path.stem
    date = frontmatter.get("last_tended") or frontmatter.get("planted") or datetime.now().strftime("%Y-%m-%d")
    date_prefix = format_date_for_jekyll(date)
    return f"{date_prefix}-{slugify(title)}.md"


def process_file(file_path, posts_dir, verbose=False):
    try:
        content = file_path.read_text(encoding="utf-8")
        frontmatter = extract_frontmatter(content)
        if not frontmatter:
            if verbose:
                print(f"Skipping {file_path.name}: no frontmatter")
            return None

        if not is_published(frontmatter):
            if verbose:
                print(f"Skipping {file_path.name}: not marked as published")
            return None

        destination_name = build_destination_filename(file_path, frontmatter)
        destination_path = posts_dir / destination_name

        if destination_path.exists() and destination_path.read_text(encoding="utf-8") == content:
            if verbose:
                print(f"Unchanged {destination_name}")
            return None

        destination_path.write_text(content, encoding="utf-8")
        print(f"Published {file_path.name} -> {destination_name}")
        return destination_path
    except Exception as error:
        print(f"Error processing {file_path}: {error}")
        return None


def process_notes(source_dir, posts_dir, single_file=None, verbose=False):
    posts_dir.mkdir(parents=True, exist_ok=True)
    changed = []

    if single_file:
        candidate_files = [Path(single_file)]
    else:
        candidate_files = sorted(source_dir.rglob("*.md"))

    for note_path in candidate_files:
        if not note_path.exists():
            print(f"File not found: {note_path}")
            continue
        published_file = process_file(note_path, posts_dir, verbose=verbose)
        if published_file:
            changed.append(published_file)

    print(f"Processed {len(candidate_files)} note(s), published {len(changed)} change(s).")
    return changed


def run_watch_loop(source_dir, posts_dir, interval, verbose=False):
    print(f"Watching {source_dir} every {interval}s")
    seen_mtimes = {}
    while True:
        files = sorted(source_dir.rglob("*.md"))
        changed_inputs = []

        for file_path in files:
            stat = file_path.stat().st_mtime
            previous = seen_mtimes.get(file_path)
            if previous is None or stat > previous:
                changed_inputs.append(file_path)
            seen_mtimes[file_path] = stat

        if changed_inputs:
            for note_path in changed_inputs:
                process_file(note_path, posts_dir, verbose=verbose)

        time.sleep(interval)


def parse_args():
    parser = argparse.ArgumentParser(description="Publish Obsidian notes to Jekyll posts.")
    parser.add_argument("--source", default=os.getenv("OBSIDIAN_NOTES_DIR", str(DEFAULT_SOURCE)))
    parser.add_argument("--posts", default=os.getenv("JEKYLL_POSTS_DIR", str(DEFAULT_POSTS)))
    parser.add_argument("--file", help="Process only this markdown file path")
    parser.add_argument("--watch", action="store_true", help="Keep watching source directory for changes")
    parser.add_argument("--interval", type=int, default=8, help="Watch interval in seconds")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    source_dir = Path(args.source)
    posts_dir = Path(args.posts)

    if not source_dir.exists():
        raise SystemExit(f"Source directory does not exist: {source_dir}")

    if args.watch and not args.file:
        run_watch_loop(source_dir, posts_dir, interval=max(3, args.interval), verbose=args.verbose)
    else:
        process_notes(source_dir, posts_dir, single_file=args.file, verbose=args.verbose)