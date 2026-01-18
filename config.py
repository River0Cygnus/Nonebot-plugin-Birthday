from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    Bday_plugin_enabled:bool = True
