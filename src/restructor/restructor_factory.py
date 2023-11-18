from src.restructor.restructor import Restructor, MovieRestructor, TVRestructor
from src.restructor.subtitle_extractor import SubtitleExtractor
from src.analyzer.media_analyzer import TVAnalyzer
from src.formatter.formatter import MovieFormatter, TVFormatter
from src.formatter.subtitle_converter import GeneralSubtitleConverter
from src.restructor.subtitle_syncer import GeneralSubtitleSyncer
from src.constants import MediaType
from src.errors import InvalidMediaTypeException
from src.env_configs import EnvConfigs


class RestructorFactory:
    def __init__(
        self, env_configs: EnvConfigs, subtitle_extractor: SubtitleExtractor
    ) -> None:
        self._env_configs = env_configs
        self._subtitle_extractor = subtitle_extractor

    def create(self, media_type: MediaType) -> Restructor:
        if media_type == MediaType.MOVIE:
            return MovieRestructor(
                env_configs=self._env_configs,
                formatter=MovieFormatter(env_configs=self._env_configs),
                subtitle_extractor=self._subtitle_extractor,
                subtitle_converter=GeneralSubtitleConverter(
                    env_configs=self._env_configs
                ),
                subtitle_syncer=GeneralSubtitleSyncer(),
            )
        elif media_type == MediaType.TV:
            return TVRestructor(
                env_configs=self._env_configs,
                formatter=TVFormatter(env_configs=self._env_configs),
                subtitle_extractor=self._subtitle_extractor,
                subtitle_converter=GeneralSubtitleConverter(
                    env_configs=self._env_configs
                ),
                subtitle_analyzer=TVAnalyzer(env_configs=self._env_configs),
                subtitle_syncer=GeneralSubtitleSyncer(),
            )

        raise InvalidMediaTypeException
