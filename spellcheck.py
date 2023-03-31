from typing import Tuple

# only after query completion
def spellcheck(res) -> Tuple[bool, str, str]:
    '''
    if there was a typo in query
    res: dictionary response 
    '''
    correct_terms = []
    typo_terms = []
    collation_queries = []
    for correction in res:
        if type(correction) is dict:
            correct_terms.append(
                correction.get("misspellingsAndCorrections")[1])
            typo_terms.append(
                correction.get("misspellingsAndCorrections")[0])
            collation_queries.append(
                correction.get("collationQuery")
            )
    return correct_terms, typo_terms, collation_queries