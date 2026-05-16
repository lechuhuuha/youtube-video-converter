from .base import DownloadProvider


class NoDownloadProviderError(ValueError):
    pass


class DownloadProviderRegistry:
    def __init__(self, providers=None):
        self._providers = []

        for provider in providers or ():
            self.register(provider)

    def register(self, provider: DownloadProvider):
        self._providers.append(provider)

    def resolve(self, url: str) -> DownloadProvider:
        for provider in self._providers:
            if provider.supports(url):
                return provider

        raise NoDownloadProviderError(f"No downloader supports this URL: {url}")

    def providers(self):
        return tuple(self._providers)
