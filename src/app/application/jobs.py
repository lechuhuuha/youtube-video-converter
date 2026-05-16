from pathlib import Path

from ..adapters import create_default_registry
from ..adapters.local_converter import MoviePyConverter
from ..domain.errors import describe_error
from ..domain.models import BatchResult, OutputFormat
from ..utils.logging import write_error_log


def run_download_batch(urls, output_dir, output_format: OutputFormat, report):
    registry = create_default_registry()
    result = BatchResult()

    for index, url in enumerate(urls, start=1):
        report(f"Downloading {index} of {len(urls)}:\n{url}")
        print(f"Downloading {index} of {len(urls)}: {url}")
        try:
            provider = registry.resolve(url)
            title = provider.download(url, output_dir, output_format)
        except Exception as error:
            result.failed.append((url, describe_error(error)))
            write_error_log(
                error, context=f"URL: {url}", append=len(result.failed) > 1
            )
        else:
            result.succeeded.append(title)

    return result


def run_conversion_batch(file_paths, report):
    converter = MoviePyConverter()
    result = BatchResult()

    for index, path in enumerate(file_paths, start=1):
        report(f"Converting {index} of {len(file_paths)}:\n{Path(path).name}")
        try:
            output = converter.convert(path)
            result.succeeded.append(output)
        except Exception as error:
            result.failed.append((Path(path).name, describe_error(error)))

    return result
