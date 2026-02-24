"""Legacy compatibility shim.

TODO: remove after Iteration 1 deprecation window.
"""

from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from semantic_ai_washing.modeling.predict import *  # noqa: F401,F403

if __name__ == "__main__" and "main" in globals():
    main()
