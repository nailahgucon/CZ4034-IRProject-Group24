from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from .place import Place


@dataclass
class Places:
    place_list: List[Place] = field(default_factory=list)

    def extend(self, place: List[Place]):
        '''
        Appends a single instance of place to
        list of places
        '''
        # if place.name in self.place_list:
        #     print("Cannot be added!")
        # else:
        self.place_list.extend(place)
    
    def append(self, place: Place):
        if place.name in self.get_names:
            print("Name already exists in database!")
        else:
            self.place_list.append(place)

    def links(self) -> List[str]:
        '''
        returns the url of a single place
        '''
        return [p.link for p in self.place_list]

    @property
    def get_names(self) -> List[str]:
        '''
        returns name of all places in the form:
        [name1: str, ...]
        '''
        return [p.name for p in self.place_list]
    
    @property
    def get_styles(self) -> List[str]:
        '''
        returns styles of the places in the form:
        [[style1, style2], ...]
        '''
        return [p.style for p in self.place_list]

