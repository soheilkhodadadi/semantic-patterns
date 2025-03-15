from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, MODELS_DIR, FIGURES_DIR
from src import config  # noqa: F401

app = typer.Typer()


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    output_path: Path = PROCESSED_DATA_DIR / "dataset.csv",
    # ----------------------------------------------t.csv",
):  # ----------------------------------------------
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Processing dataset...")DE ----
    for i in tqdm(range(10), total=10):)
        if i == 5:range(10), total=10):
            logger.info("Something happened for iteration 5.")
    logger.success("Processing dataset complete.")eration 5.")
    # -----------------------------------------.")
    # -----------------------------------------

if __name__ == "__main__":
    app()__ == "__main__":
    app()








known-first-party = ["src"][tool.ruff.lint.isort]include = ["pyproject.toml", "src/**/*.py"]src = ["src"]line-length = 99[tool.ruff]