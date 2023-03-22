from typing import Dict, List

autocomplete_field = "autocomplete__txtsug"

# updates frequently
def autocomplete(res) -> List[str]:
    '''
    autocompletes the query by offering suggestions
    res: response result dictionary
    '''
    suggested = res.get("spellcheck").get("suggestions")
    if suggested:
        suggtexts = []
        for suggestion in suggested:
            if type(suggestion) is dict:
                sugg_texts = suggestion.get("suggestion")
                for sugg_text in sugg_texts:
                    suggtexts.append(sugg_text
                        )
        return suggtexts
    else:
        return None
