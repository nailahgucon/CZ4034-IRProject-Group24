from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple


@dataclass
class Place:
    name: str
    style: List[str]
    category: str
    star: float

    def __post_init__(self):
        self.style = self.style.split("|")

    @property
    def link(self):
        return f"http://127.0.0.1:5000/place/{self.name.replace(' ', '+')}"
    
