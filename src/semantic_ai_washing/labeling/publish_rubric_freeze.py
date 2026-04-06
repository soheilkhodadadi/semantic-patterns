"""Compatibility shim for provisional rubric-freeze publishing."""

from ai_washing_member.labeling.publish_rubric_freeze import main, parse_args, run_publish

__all__ = ["run_publish", "parse_args", "main"]


if __name__ == "__main__":
    main()
