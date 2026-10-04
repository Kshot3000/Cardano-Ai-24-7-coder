"""
Auto-fix template for Cardano repos — NOT YET IMPLEMENTED.

Honesty note: there is no AI-driven fix generation in this repo yet.
The previous version of ``apply_fix`` printed "Applying fix for ..."
and returned True without touching any file, so any caller would have
reported a fix that never happened. This template now refuses loudly
instead of faking success; implement real fix generation here (and
return True only after a change is actually written and verified)
before wiring it into the scanner.
"""


def apply_fix(repo_path, issue):
    """Apply a generated fix — not implemented.

    Raises NotImplementedError always, until real fix generation exists.
    Never returns True for work that was not done.
    """
    raise NotImplementedError(
        "auto-fix generation is not implemented yet; "
        f"no fix was applied to {repo_path!r} for issue {issue!r}"
    )
