from typing import (
    Tuple, 
    Type, 
    Optional, 
    List,
)
from pydantic import (
    BaseModel,
    field_validator,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)
from enum import Enum
import logging
import logging.handlers

class Api(BaseModel):
    SecretId: str
    SecretKey: str

class RecordType(Enum):
    IPV6 = "AAAA"
    IPV4 = "A"

class Dns(BaseModel):
    domain: str
    sub_domain: Optional[str]
    record_type: str
    record_line: str

    @field_validator('record_type')
    def validata_record_type(cls, v):
        try:
            return RecordType[v].value
        except KeyError:
            raise ValueError(f"Invalid record_type: {v}. Valid options are {[record_type.name for record_type in RecordType]}")

class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class HandlerClass(Enum):
    CONSOLE = logging.StreamHandler()
    FILE = logging.FileHandler('logfile.log')
    TimeROTA = logging.handlers.TimedRotatingFileHandler('logRoteFile.log', when='midnight', backupCount=2)
    
class Handler(BaseModel):
    handler: str
    
    # TODO: 添加对应log输出模式的详细配置
    @field_validator('handler')
    def validate_handler(cls, v):
        try:
            return HandlerClass[v].value
        except KeyError:
            raise ValueError(f"Invalid log handler: {v}. Valid options are {[handler.name for handler in HandlerClass]}")

class Log(BaseModel):
    level: str
    format: str
    handlers: List['Handler']
    
    @field_validator('level')
    def validate_log_level(cls, v):
        try:
            return LogLevel[v].value
        except KeyError:
            raise ValueError(f"Invalid log level: {v}. Valid options are: {[level.name for level in LogLevel]}")
        
    
class Settings(BaseSettings):
    api: Api
    dns: Dns
    log: Log
    model_config = SettingsConfigDict(toml_file='config.toml')

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # 继承基类改写返回类型为toml
        return (TomlConfigSettingsSource(settings_cls),)

settings = Settings()

logging.basicConfig(
    format=settings.log.format,
    level=settings.log.level,
    handlers=[_.handler for _ in settings.log.handlers]
)

logger = logging.getLogger(__name__)