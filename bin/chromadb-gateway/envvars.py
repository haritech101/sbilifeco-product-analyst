class EnvVars:
    test_type = "TEST_TYPE"
    http_port_vectoriser = "HTTP_PORT_VECTORISER"
    http_port_vector_repo = "HTTP_PORT_VECTOR_REPO"
    staging_host = "STAGING_HOST"
    db_path = "DB_PATH"
    collection_name = "COLLECTION_NAME"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    http_port_vectoriser = "80"
    http_port_vector_repo = "80"
    staging_host = "localhost"
    db_path = "./.chromadb"
    collection_name = "embeddings"
