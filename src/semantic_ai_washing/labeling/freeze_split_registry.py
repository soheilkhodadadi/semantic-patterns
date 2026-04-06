"""Compatibility shim for grouped split-registry freezing."""

from ai_washing_member.labeling.freeze_split_registry import main, parse_args, run_freeze

__all__ = ["run_freeze", "parse_args", "main"]


if __name__ == "__main__":
    main()
