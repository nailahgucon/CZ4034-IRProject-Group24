from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

import geopy.distance


@dataclass
class Place:
    name: str
    style: List[str]
    category: str
    star: float
    # Latitude, longitude
    coordinates: Tuple[float, float]

    def __post_init__(self):
        self.style = self.style.split("|")
    
    def calculate_dist(self, place: Place):
        distance = geopy.distance.geodesic(place.coordinates, self.coordinates).km
        return distance

    def match(self, place: Place, **kwargs) -> bool:
        category: str = kwargs["category"]
        dist: str = kwargs["dist"]
        dist_value: float = kwargs["dist_value"]
        distance = self.calculate_dist(place)
        match_ = False
        if category:
            match_ = self.category.lower()==category
            if not match_:
                return None
        if dist:
            if dist == 'near':
                match_ = (True if distance <= dist_value else False)
            elif dist == 'far':
                match_ = (True if distance >= dist_value else False)
            else:
                match_ = False
        if match_:
            return {self.name: distance}
        else:
            return None

    
