from src.analyzer.media_analyzer import MediaAnalyzer, MovieAnalyzer, TVAnalyzer
from src.analyzer.mkv_subtitle_extractor import MkvSubtitleExtractor
from src.constants import MediaType
from src.errors import InvalidMediaTypeException
from src.env_configs import EnvConfigs
from src.log_exporter import LogExporter


class MediaAnalyzerFactory:
    def __init__(self, env_configs: EnvConfigs, log_exporter: LogExporter) -> None:
        self._env_configs = env_configs
        self._log_exporter = log_exporter

    def create(self, media_type: MediaType) -> MediaAnalyzer:
        mkv_subtitle_extractor = MkvSubtitleExtractor(
            env_configs=self._env_configs, log_exporter=self._log_exporter
        )

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
