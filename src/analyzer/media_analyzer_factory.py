from src.analyzer.media_analyzer import MediaAnalyzer, MovieAnalyzer, TVAnalyzer
from src.constants import MediaType
from src.errors import InvalidMediaTypeException
from src.env_configs import EnvConfigs


class MediaAnalyzerFactory:
    def __init__(
        self,
        env_configs: EnvConfigs,
    ) -> None:
        self._env_configs = env_configs

    def create(self, media_type: MediaType) -> MediaAnalyzer:
        if media_type == MediaType.MOVIE:
            return MovieAnalyzer(env_configs=self._env_configs)
        elif media_type == MediaType.TV:
            return TVAnalyzer(env_configs=self._env_configs)

        raise InvalidMediaTypeException
