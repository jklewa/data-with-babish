import re


def normalize_raw_list(raw):
    return '\n'.join(
        line
        for line in (
            re.sub(r'^(\*\s+|[0-9]+\.\s+)', '', line.strip())
            for line in raw.splitlines()
        )
        if line
    )
