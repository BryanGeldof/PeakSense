DOMAIN = "peaksense"

# Thresholds
SPIKE_START_THRESHOLD = 800  # W
SPIKE_END_THRESHOLD = 300    # W

# Detection
MIN_CONFIDENCE = 0.75  # 75% confidence required
SIMILARITY_THRESHOLD = 0.8

# Standby detection
STANDBY_DETECTION_DURATION = 120  # 2 minutes in seconds
STANDBY_SAMPLE_INTERVAL = 5  # 5 seconds

# Pattern matching
MIN_SAMPLES_FOR_PATTERN = 3  # Need at least 3 spikes to learn pattern
