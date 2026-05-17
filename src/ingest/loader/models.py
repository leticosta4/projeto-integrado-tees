from typing import TypedDict
from pydantic import BaseModel
from xml.etree.ElementTree import ElementTree, Element

class XMLLoaded(TypedDict):
    filename: str
    filehash: str
    data: ElementTree
