class EnvVars:
    test_type = "TEST_TYPE"
    staging_host = "STAGING_HOST"
    qdrant_url = "QDRANT_URL"
    collection_name = "COLLECTION_NAME"
    vectoriser_http_port = "VECTORSER_HTTP_PORT"
    vector_repo_http_port = "VECTOR_REPO_HTTP_PORT"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    staging_host = "localhost"
    qdrant_url = "http://localhost:6333"
    collection_name = "default"
    vectoriser_http_port = "80"
    vector_repo_http_port = "81"
