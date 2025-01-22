from pydantic import Field
from pydantic_settings import BaseSettings


class Application(BaseSettings):
    version: str = Field(default="0.1.0", description="Version")
    title: str = Field(default="MIP Backend Service", description="Title")
    description: str = Field(default="MIP Backend Service", description="Description")
    debug: bool = Field(default=False, description="Debug mode", alias="debug")
    timezone: str = Field(default="Europe/Moscow", description="Timezone")
    allowed_origins: list[str] = Field(
        default=["*"], description="CORS origins", alias="ALLOWED_ORIGINS"
    )
    api_prefix: str = Field(default="/api", description="API prefix")
    docs_url: str = Field(default="/api/docs", description="Docs url")


class CloudPayments(BaseSettings):
    public_id: str = Field(
        default="test_public_id",
        description="Cloudpayments public ID",
        alias="CLOUDPAYMENTS_PUBLIC_ID",
    )
    api_secret: str = Field(
        default="test_api_secret",
        description="Cloudpayments API secret",
        alias="CLOUDPAYMENTS_API_SECRET",
    )
    status_url: str = Field(
        default="https://api.cloudpayments.ru/payments/get",
        description="Cloudpayments status URL",
    )
    confirmation_url: str = Field(
        default="https://api.cloudpayments.ru/payments/confirm",
        description="Cloudpayments confirmation URL",
    )


class Frontend(BaseSettings):
    users_login_url: str = Field(
        default="https://lms.mip.institute/local/ilogin/rlogin.php",
        description="Users login url",
    )


class Logging(BaseSettings):
    level: str = Field(default="INFO", description="Log level")
    config: dict = Field(
        default={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "app.utils.logging.JsonFormatter",
                    "format": "%(asctime)s %(module)s %(lineno)d %(levelname)s %(message)s",  # noqa: E501
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": level,
                },
            },
        },
        description="Log config",
    )


class Postgres(BaseSettings):
    db: str = Field(default="mip_db", description="Postgres DB", alias="POSTGRES_DB")
    port: int = Field(default=5432, description="Postgres port", alias="POSTGRES_PORT")
    user: str = Field(
        default="mip_default",
        description="Postgres user",
        alias="POSTGRES_USER",
    )
    host: str = Field(
        default="postgres", description="Postgres host", alias="POSTGRES_HOST"
    )
    min_size: int = Field(
        default=10, description="Postgres min pool size", alias="POSTGRES_MIN_SIZE"
    )
    max_size: int = Field(
        default=10, description="Postgres max pool size", alias="POSTGRES_MAX_SIZE"
    )
    password: str = Field(
        default="DD54OwPVOYvcDw2lfkGvYerDg7AknuldLnd77XlLVZpWFhiU5jJjFPjjmUAM4jWg",
        description="Postgres password",
        alias="POSTGRES_PASSWORD",
    )
    db_echo: bool = Field(
        default=False, description="Postgres db echo", alias="DB_ECHO"
    )
    db_schema: str = Field(
        default="public", description="Postgres db schema", alias="POSTGRES_SCHEMA"
    )

    @property
    def dsn(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"  # noqa: E501


class Settings(BaseSettings):
    application: Application = Application()
    cloudpayments: CloudPayments = CloudPayments()
    frontend: Frontend = Frontend()
    logging: Logging = Logging()
    postgres: Postgres = Postgres()


config = Settings()
