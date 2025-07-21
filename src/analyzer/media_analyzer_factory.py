from src.analyzer.media_analyzer import MediaAnalyzer, MovieAnalyzer, TVAnalyzer
from src.analyzer.mkv_subtitle_extractor import MkvSubtitleExtractor
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
        mkv_subtitle_extractor = MkvSubtitleExtractor(env_configs=self._env_configs)

        if media_type == MediaType.MOVIE:
            return MovieAnalyzer(
                env_configs=self._env_configs,
                mkv_subtitle_extractor=mkv_subtitle_extractor,
            )
        elif media_type == MediaType.TV:
            return TVAnalyzer(
                env_configs=self._env_configs,
                mkv_subtitle_extractor=mkv_subtitle_extractor,
            )

        raise InvalidMediaTypeException
