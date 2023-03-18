from typing import Dict, Tuple

# only after query completion
def spellcheck(res: Dict[str]) -> Tuple[bool, str, str]:
    '''
    if there was a typo in query
    res: dictionary response 
    '''
    spellcheck_list = results.get("spellcheck").get("collations")
    correct_terms = []
    typo_terms = []
    for correction in spellcheck_list:
        if type(correction) is dict:
            correct_terms.append(
                correction.get("misspellingsAndCorrections")[1])
            typo_terms.append(
                correction.get("misspellingsAndCorrections")[0])
    return correct_terms, typo_terms
