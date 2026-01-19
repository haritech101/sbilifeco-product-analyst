class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    staging_host = "STAGING_HOST"
    qdrant_url = "QDRANT_URL"
    collection_name = "COLLECTION_NAME"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    http_port = "80"
    staging_host = "localhost"
    qdrant_url = "http://localhost:6333"
    collection_name = "default"
