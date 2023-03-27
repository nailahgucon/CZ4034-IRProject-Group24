from typing import Dict, List

autocomplete_field = "autocomplete__txtsug"

# updates frequently
def autocomplete(res) -> List[str]:
    '''
    autocompletes the query by offering suggestions
    res: response result dictionary
    '''
    docs = res["response"]["docs"]
    sugg = set()
    for doc in docs:
        if "autocomplete__txtsug" in doc:
            sugg.add(doc["autocomplete__txtsug"][0])
    return list(sugg)

