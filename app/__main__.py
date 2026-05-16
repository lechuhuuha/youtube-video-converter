from .app import main
from .errors import write_error_log


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        write_error_log(error)
        raise
