from typing import Dict, Tuple

mlt_field = "Name"  # can be hotel_name/restaurant_name or other columns that you want

# only after query completion
@app.route('/mlt', methods=['GET'])
def mlt(col_name:str, query_term:str, field:str, **kwargs) -> List[str]:
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
    user_query = f"{col_name}:{query_term}"
    kwargs.update({"q": user_query, 'mlt.fl': field})

    results = requests.get(server,
                           params=kwargs).json()
    mlt_list = []
    if "response" in results:
        morelikethises = results["response"].get("docs")
        for morelikethis in morelikethises:
            mlt_list.extend(morelikethis.get(mlt_field))
    return mlt_list
