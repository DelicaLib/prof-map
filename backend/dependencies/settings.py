from pydantic import BaseModel


class PostgresSettings(BaseModel):
    db_password: str
    db_host: str
    db_port: int
    db_user: str
    db_name: str


class BertSettings(BaseModel):
    model: str


class Settings(BaseModel):
    postgres: PostgresSettings
    bert: BertSettings
