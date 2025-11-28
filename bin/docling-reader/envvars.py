class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    staging_host = "STAGING_HOST"
    doclingserve_proto = "DOCLINGSERVE_PROTO"
    doclingserve_host = "DOCLINGSERVE_HOST"
    doclingserve_port = "DOCLINGSERVE_PORT"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    http_port = "80"
    staging_host = "localhost"
    doclingserve_proto = "http"
    doclingserve_host = "localhost"
    doclingserve_port = "80"
