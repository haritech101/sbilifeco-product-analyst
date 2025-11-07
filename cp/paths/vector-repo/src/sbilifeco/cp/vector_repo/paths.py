class VectorRepoPaths:
    BASE = "/api/v1/vectorised-data"  # POST
    BY_ID = BASE + "/{id}"  # GET, DELETE
    SEARCH_BY_CRITERIA = BASE + "/search/by-criteria"  # POST due to payload
    DELETE_BY_CRITERIA = BASE + "/delete/by-criteria"  # POST due to payload
    BY_VECTOR = BASE + "/search/by-vector"  # POST due to payload
