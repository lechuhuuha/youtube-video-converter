import sys
import traceback

from .. import PROJECT_ROOT


ERROR_LOG_PATH = PROJECT_ROOT / "error.log"


def write_error_log(error, context=None, append=False):
    details = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    if context:
        details = f"{context}\n{details}"

    if append:
        with ERROR_LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(f"\n\n{details}")
    else:
        ERROR_LOG_PATH.write_text(details, encoding="utf-8")

    print(details, file=sys.stderr)
