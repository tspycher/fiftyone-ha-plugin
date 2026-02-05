"""Constants for the FiftyOne integration."""

DOMAIN = "fiftyone"

# API Configuration
API_BASE_URL = "https://api.fiftyone.dev"

# Platforms
PLATFORMS = ["sensor", "camera", "image"]

# Configuration keys
CONF_API_URL = "api_url"
CONF_IMAGE_SOURCES = "image_sources"

# Update intervals (seconds)
DEFAULT_SCAN_INTERVAL = 600  # 10 minutes

# Attribution
ATTRIBUTION = "Data provided by FiftyOne API"

# Webcam names
WEBCAM_NAMES = {
    "basel": "Basel",
    "bern": "Bern",
    "lucern": "Lucerne",
    "zurich": "Zurich",
}
