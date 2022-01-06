import cassis
from pydantic import BaseModel

from connectors.utils import cas_from_cas_content


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

    def get_cas(self) -> cassis.Cas:
        return cas_from_cas_content(self.cas_content)


class ContactInfo(BaseModel):
    text: str
    cas_content: str
    language: str
