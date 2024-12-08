from pydantic import BaseModel


class PostgresSettings(BaseModel):
    db_password: str
    db_host: str
    db_port: int
    db_user: str
    db_name: str


class BertSettings(BaseModel):
    model: str
    skills_model_path: str


class RobertaSettings(BaseModel):
    model: str


class OpenAISettings(BaseModel):
    gpt_token: str


class Settings(BaseModel):
    postgres: PostgresSettings
    bert: BertSettings
    roberta: RobertaSettings
    openai: OpenAISettings
