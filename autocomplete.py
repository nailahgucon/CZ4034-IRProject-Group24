from typing import Dict, List

autocomplete_field = "autocomplete__txtsug"

# updates frequently
def autocomplete(res: Dict[str]) -> List[str]:
    '''
    autocompletes the query by offering suggestions
    res: response result dictionary
    '''
    suggested = res.get("response").get("docs")
    if suggested:
        suggtexts = []
        for suggestion in suggested:
            suggtexts.append(
                suggestion.get(autocomplete_field))
        return suggtexts
    else:
        return None
