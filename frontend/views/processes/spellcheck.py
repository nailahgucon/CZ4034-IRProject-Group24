from typing import Tuple

# only after query completion
def spellcheck(res) -> Tuple[bool, str, str]:
    '''
    if there was a typo in query
    res: dictionary response 
    '''
    # TODO error spellchecking on multiple words
    # TODO error spellchecking on long terms
    correct_terms = []
    typo_terms = []
    collation_queries = []
    for correction in res:
        if type(correction) is dict:
            cq = correction.get("collationQuery").split(":")
            correct_terms.append(
                correction.get("misspellingsAndCorrections")[1])
            typo_terms.append(
                correction.get("misspellingsAndCorrections")[0])
            collation_queries.extend(
                cq[1:]
            )
    return correct_terms, typo_terms, collation_queries
