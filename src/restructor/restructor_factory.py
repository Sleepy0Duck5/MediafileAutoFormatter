from src.restructor.restructor import Restructor, MovieRestructor, TVRestructor
from src.formatter.formatter import GeneralFormatter
from src.constants import MediaType
from src.errors import InvalidMediaTypeException
from src.env_configs import EnvConfigs


class RestructorFactory:
    def __init__(
        self,
        env_configs: EnvConfigs,
    ) -> None:
        self._env_configs = env_configs

    def create(self, media_type: MediaType) -> Restructor:
        if media_type == MediaType.MOVIE:
            return MovieRestructor(
                env_configs=self._env_configs,
                formatter=GeneralFormatter(env_configs=self._env_configs),
            )
        elif media_type == MediaType.TV:
            return TVRestructor(
                env_configs=self._env_configs,
                formatter=GeneralFormatter(env_configs=self._env_configs),
            )

        raise InvalidMediaTypeException
