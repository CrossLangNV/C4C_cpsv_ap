from pydantic import BaseModel


class ChunkModel(BaseModel):
    title: str
    tags: str
    excerpt: str  # description of a webpage, see Package "trafilatura"
    text: str
    hostname: str
    source_hostname: str  # Make sure to de-hyphenate
    source: str
    language: str
    cas_content: str
