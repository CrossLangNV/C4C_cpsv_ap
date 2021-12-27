from pydantic import BaseModel


class ChunkModel(BaseModel):
    title: str
    tags: str
    excerpt: str
    text: str
    hostname: str
    source_hostname: str  # Make sure to de-hyphenate
    source: str
    language: str
    cas_content: str
