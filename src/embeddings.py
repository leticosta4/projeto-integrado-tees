import math
import re
from typing import Protocol


class EmbeddingsModel(Protocol):
    def embed_query(self, text: str) -> list[float]:
        ...

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...


class LocalEmbeddings:
    def __init__(self, dimensions: int = 128) -> None:
        self.dimensions = dimensions

    def embed_query(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions

        for token in tokenize(text):
            index = stable_index(token, self.dimensions)
            vector[index] += 1.0

        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0:
            return vector

        return [value / magnitude for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    expanded: list[str] = []

    for token in tokens:
        expanded.append(token)
        expanded.extend(SYNONYMS.get(token, ()))

    return expanded


def stable_index(token: str, dimensions: int) -> int:
    value = 0

    for character in token:
        value = (value * 31 + ord(character)) % dimensions

    return value


SYNONYMS = {
    "ai": ("artificial", "intelligence"),
    "artificial": ("ai",),
    "intelligence": ("ai",),
    "health": ("healthcare",),
    "healthcare": ("health",),
    "learning": ("ai",),
}
