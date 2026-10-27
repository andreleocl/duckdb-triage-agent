"""Validate a triage proposal offline; never access GitHub or publish content."""

import argparse
import json
from pathlib import Path
import re
import sys

REPOSITORY = 'andreleocl/duckdb-triage-agent'
LABELS = ('needs reproducible example', 'needs more info')
MAX_COMMENT_CHARS = 1200


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON field: {key}')
        result[key] = value
    return result


def validate(proposal, repository, issue):
    if repository != REPOSITORY or type(issue) is not int or issue <= 0:
        raise ValueError('Target must be a positive issue number in the assignment repository')
    if not isinstance(proposal, dict) or set(proposal) != {'label', 'comment', 'rationale'}:
        raise ValueError('Expected exactly label, comment and rationale')
    label, comment, rationale = (proposal[k] for k in ('label', 'comment', 'rationale'))
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError('A nonempty audit rationale is required')
    if label is None:
        if comment is not None:
            raise ValueError('No action requires both label and comment to be null')
        return proposal
    if not isinstance(label, str) or label not in LABELS:
        raise ValueError('Label is not allowed')
    if not isinstance(comment, str) or not comment.strip() or len(comment) > MAX_COMMENT_CHARS:
        raise ValueError('A request requires one nonempty comment of at most 1200 characters')
    # Keep sample requests size-neutral; this is not a semantic relevance check.
    if re.search(r'\b(?:\d[\d,]*(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|twenty)'
                 r'(?:\s*(?:[-–—]|to)\s*(?:\d[\d,]*|twenty))?'
                 r'[\s–—-]+(?:rows?|records?)\b', comment, re.IGNORECASE):
        raise ValueError('Public comments must use size-neutral sample requests, without numeric row/record counts')
    # Conservative: public triage questions do not need mentions or GitHub references.
    if '@' in comment or re.search(r'github\.com|#\d+|duckdb/duckdb', comment, re.IGNORECASE):
        raise ValueError('Public comments must not contain mentions or GitHub issue references')
    return proposal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('proposal', type=Path)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--issue', type=int, required=True)
    args = parser.parse_args()
    try:
        proposal = json.loads(args.proposal.read_text(encoding='utf-8'), object_pairs_hook=unique_fields)
        validate(proposal, args.repository, args.issue)
    except (ValueError, OSError) as error:
        print(f'Rejected: {error}', file=sys.stderr)
        return 1
    print(json.dumps(proposal, ensure_ascii=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
