from src.restructor.restructor import Restructor
from src.restructor.movie_restructor import MovieRestructor
from src.restructor.tv_restructor import TVRestructor
from src.restructor.subtitle_extractor import SubtitleExtractor
from src.restructor.audio_track_changer import AudioTrackChanger
from src.analyzer.media_analyzer import TVAnalyzer
from src.analyzer.mkv_subtitle_extractor import MkvSubtitleExtractor
from src.formatter.formatter import MovieFormatter, TVFormatter
from src.formatter.subtitle_converter import SubtitleConverter
from src.formatter.smi_to_srt_converter import SmiToSrtConverter
from src.formatter.smi_to_ass_converter import SmiToAssConverter
from src.constants import MediaType, Extensions
from src.errors import InvalidMediaTypeException, InvalidEnvConfig
from src.env_configs import EnvConfigs
from src.arguments import Arguments


class RestructorFactory:
    def __init__(
        self,
        env_configs: EnvConfigs,
        subtitle_extractor: SubtitleExtractor,
        arguments: Arguments,
    ) -> None:
        self._env_configs = env_configs
        self._subtitle_extractor = subtitle_extractor
        self._arguments = arguments

    def create(self, media_type: MediaType) -> Restructor:
        subtitle_converter = self._get_subtitle_converter(
            self._env_configs._CONVERT_SMI_EXTENSION
        )
        audio_track_changer = AudioTrackChanger(
            audio_track_langugage=self._arguments.mkv_audio_language,
        )

        if media_type == MediaType.MOVIE:
            return MovieRestructor(
                env_configs=self._env_configs,
                formatter=MovieFormatter(env_configs=self._env_configs),
                audio_track_changer=audio_track_changer,
                subtitle_extractor=self._subtitle_extractor,
                subtitle_converter=subtitle_converter,
            )
        elif media_type == MediaType.TV:
            return TVRestructor(
                env_configs=self._env_configs,
                formatter=TVFormatter(env_configs=self._env_configs),
                audio_track_changer=audio_track_changer,
                subtitle_extractor=self._subtitle_extractor,
                subtitle_converter=subtitle_converter,
                subtitle_analyzer=TVAnalyzer(
                    env_configs=self._env_configs,
                    mkv_subtitle_extractor=MkvSubtitleExtractor(
                        env_configs=self._env_configs
                    ),
                ),
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
            return SmiToAssConverter(env_configs=self._env_configs)

        raise InvalidEnvConfig(
            f"Invalid CONVERT_SMI_EXTENSION {smi_subtitle_convert_extension}"
        )
