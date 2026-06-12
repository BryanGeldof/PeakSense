from .coordinator import PeakSenseCore

core = PeakSenseCore()

def process_power(value):
    return core.process_value(value)
