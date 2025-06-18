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
    inn: str = Field(
        default="9725041321",
        description="MIP INN",
        alias="CLOUDPAYMENTS_MIP_INN",
    )
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
    customer_receipt_url: str = Field(
        default="https://api.cloudpayments.ru/kkt/receipt",
        description="Cloudpayments customer receipt URL",
    )


class Email(BaseSettings):
    hr_email: str = Field(default="hr@mip.institute", description="HR email", alias="HR_EMAIL")
    info_email: str = Field(default="info@mip.institute", description="Info email", alias="INFO_EMAIL")


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


class SMTP(BaseSettings):
    server: str = Field(default="smtp.yandex.ru", description="SMTP server", alias="SMTP_SERVER")
    port: int = Field(default=587, description="SMTP port", alias="SMTP_PORT")
    user: str = Field(default="notify@mip.institute", description="SMTP user", alias="SMTP_USER")
    password: str = Field(
        default="password", description="SMTP server password", alias="SMTP_SERVER_PASSWORD"
    )


class AuthConfig:
    secret_key: str = "1yXk@2GfcFRMD!t$n66M1aB*93>EEgTl"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    admin_email: str = "developers@mip.institute"
    admin_password: str = "mipAdm1nP@ssw0rd"
    auth_username: str = "mip.admin"
    auth_password: str = "faksdfjw329f8d7u4%^*y4o2j4"


class Settings(BaseSettings):
    application: Application = Application()
    cloudpayments: CloudPayments = CloudPayments()
    email: Email = Email()
    frontend: Frontend = Frontend()
    logging: Logging = Logging()
    postgres: Postgres = Postgres()
    smtp: SMTP = SMTP()
    auth: AuthConfig = AuthConfig()


config = Settings()
