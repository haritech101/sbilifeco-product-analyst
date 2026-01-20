class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    staging_host = "STAGING_HOST"
    api_base_url = "API_BASE_URL"
    material_queries_path = "MATERIAL_QUERIES_PATH"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    http_port = "80"
    staging_host = "localhost"
    api_base_url = "http://localhost"
    material_queries_path = "/api/v1/material-queries"
