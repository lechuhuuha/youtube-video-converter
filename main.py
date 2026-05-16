import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from app.app import main
from app.utils.logging import write_error_log


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        write_error_log(error)
        raise
