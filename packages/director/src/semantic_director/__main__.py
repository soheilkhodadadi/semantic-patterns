"""Module execution entrypoint for the package-owned director CLI."""

from semantic_director.cli import main

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
