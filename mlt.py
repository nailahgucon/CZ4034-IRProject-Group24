from typing import List

field_you_want = "Name"  # can be hotel_name/restaurant_name or other columns that you want

# only after query completion
def mlt(res) -> List[str]:
    '''
    offers more like this documents

    col_name: main field of query
    query_term: term you are querying
    field: other data entries with similar data in this field
    
    use:
        mlt_params ={'mlt.match.include': "false",
                     "mlt.mintf": "0",
                     "mlt.mindf": "0"}
        out = mlt(col_name, query_term, field, mlt_url, **mlt_params)
    '''
    mlt_list = []
    if "moreLikeThis" in res:
        for i in res["moreLikeThis"]:
            morelikethises = res["moreLikeThis"][i].get("docs")
            for morelikethis in morelikethises:
                mlt_list.extend(morelikethis.get(field_you_want))
    return mlt_list
