from src.restructor.restructor import Restructor, MovieRestructor, TVRestructor
from src.restructor.subtitle_extractor import SubtitleExtractor
from src.analyzer.media_analyzer import TVAnalyzer
from src.formatter.formatter import MovieFormatter, TVFormatter
from src.formatter.subtitle_converter import SubtitleConverter
from src.formatter.smi_to_srt_converter import SmiToSrtConverter
from src.restructor.subtitle_syncer import GeneralSubtitleSyncer
from src.constants import MediaType, Extensions
from src.errors import InvalidMediaTypeException, InvalidEnvConfig
from src.env_configs import EnvConfigs


class RestructorFactory:
    def __init__(
        self, env_configs: EnvConfigs, subtitle_extractor: SubtitleExtractor
    ) -> None:
        self._env_configs = env_configs
        self._subtitle_extractor = subtitle_extractor

    def create(self, media_type: MediaType) -> Restructor:
        subtitle_converter = self._get_subtitle_converter(
            self._env_configs._CONVERT_SMI_EXTENSION
        )

        if media_type == MediaType.MOVIE:
            return MovieRestructor(
                env_configs=self._env_configs,
                formatter=MovieFormatter(env_configs=self._env_configs),
                subtitle_extractor=self._subtitle_extractor,
                subtitle_converter=subtitle_converter,
                subtitle_syncer=GeneralSubtitleSyncer(),
            )
        elif media_type == MediaType.TV:
            return TVRestructor(
                env_configs=self._env_configs,
                formatter=TVFormatter(env_configs=self._env_configs),
                subtitle_extractor=self._subtitle_extractor,
                subtitle_converter=subtitle_converter,
                subtitle_analyzer=TVAnalyzer(env_configs=self._env_configs),
                subtitle_syncer=GeneralSubtitleSyncer(),
            )

        raise InvalidMediaTypeException

    def _get_subtitle_converter(
        self, smi_subtitle_convert_extension: str
    ) -> SubtitleConverter:
        if not smi_subtitle_convert_extension:
            raise InvalidEnvConfig("CONVERT_SMI_EXTENSION not found")

        if smi_subtitle_convert_extension == Extensions.SRT:
            return SmiToSrtConverter(env_configs=self._env_configs)
        elif smi_subtitle_convert_extension == Extensions.ASS:
            pass

        raise InvalidEnvConfig(
            f"Invalid CONVERT_SMI_EXTENSION {smi_subtitle_convert_extension}"
        )
