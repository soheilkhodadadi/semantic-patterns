"""Compatibility shim for the package-owned director module entrypoint."""

from semantic_director.__main__ import main

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
