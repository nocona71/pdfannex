import argparse
import base64
import json
import os
import re
import subprocess
import sys


TAG_PATTERN = re.compile(r"pdfannex-v([0-9]+\.[0-9]+\.[0-9]+)\Z")
VERSION_SUFFIX = re.compile(r"\s+# x-release-please-version\s*\Z")


def normalize_version(contents):
    return VERSION_SUFFIX.sub("", contents).strip()


def eligible_release_tags(releases, version_for_tag):
    eligible = []
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        published_at = release.get("published_at")
        tag = release.get("tag_name", "")
        match = TAG_PATTERN.fullmatch(tag)
        if not published_at or not match:
            continue
        if version_for_tag(tag) == match.group(1):
            eligible.append((published_at, tag))
    return [tag for _, tag in sorted(eligible, reverse=True)]


def gh_json(args):
    result = subprocess.run(
        ["gh", "api", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def fetch_releases(repository):
    output = gh_json(
        [
            "--paginate",
            f"repos/{repository}/releases?per_page=100",
            "--jq",
            ".[] | {tag_name, draft, prerelease, published_at}",
        ]
    )
    return [json.loads(line) for line in output.splitlines() if line.strip()]


def fetch_version(repository, tag):
    encoded = gh_json(
        [
            f"repos/{repository}/contents/VERSION?ref={tag}",
            "--jq",
            ".content",
        ]
    ).strip()
    contents = base64.b64decode(encoded).decode("utf-8")
    return normalize_version(contents)


def write_outputs(path, run_pipeline, release_tag=""):
    with open(path, "a", encoding="utf-8") as output:
        output.write(f"run_pipeline={'true' if run_pipeline else 'false'}\n")
        output.write(f"release_tag={release_tag}\n")


def write_tag_summary(path, tags):
    lines = ["## Eligible published CTAN releases", ""]
    if tags:
        lines.extend(f"- `{tag}`" for tag in tags)
        lines.extend(
            [
                "",
                "Run this workflow again from `main` and enter one of these exact tags.",
            ]
        )
    else:
        lines.append("No eligible published releases were found.")
    with open(path, "a", encoding="utf-8") as summary:
        summary.write("\n".join(lines) + "\n")


def fail(message):
    print(f"::error::{message}")
    raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--tag", default="")
    args = parser.parse_args()

    output_path = os.environ["GITHUB_OUTPUT"]
    summary_path = os.environ["GITHUB_STEP_SUMMARY"]

    if args.event != "workflow_dispatch":
        if not TAG_PATTERN.fullmatch(args.tag):
            fail(f"Unexpected release tag: {args.tag!r}")
        write_outputs(output_path, True, args.tag)
        return

    if args.ref != "refs/heads/main":
        fail("Manual CTAN workflows must be run from the main branch.")

    repository = os.environ["GITHUB_REPOSITORY"]
    releases = fetch_releases(repository)
    tags = eligible_release_tags(
        releases,
        lambda tag: fetch_version(repository, tag),
    )

    if not args.tag:
        write_tag_summary(summary_path, tags)
        write_outputs(output_path, False)
        return

    if args.tag not in tags:
        write_tag_summary(summary_path, tags)
        fail(
            f"Release tag {args.tag!r} is not eligible. "
            "Choose a published tag listed in this run's summary."
        )
    write_outputs(output_path, True, args.tag)


if __name__ == "__main__":
    main()
