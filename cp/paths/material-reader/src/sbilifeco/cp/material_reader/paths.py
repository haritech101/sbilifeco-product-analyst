class MaterialReaderPaths:
    BASE = "/api/v1/materials"
    MATERIAL_BY_ID = BASE + "/{material_id}"
    NEXT_CHUNK = MATERIAL_BY_ID + "/next-chunk"
