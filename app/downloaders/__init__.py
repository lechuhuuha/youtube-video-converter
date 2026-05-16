from .registry import DownloadProviderRegistry
from .ytdlp_provider import YtDlpProvider


def create_default_registry():
    registry = DownloadProviderRegistry()
    registry.register(YtDlpProvider())
    return registry
