from .const import MIN_CONFIDENCE

class PatternMatcher:
    def __init__(self):
        self.storage = None

    def match_event(self, event, known_devices):
        if not known_devices:
            return {'device_id': None, 'device_name': None, 'confidence': 0, 'matches': {}}

        matches = {}
        for device in known_devices:
            signatures = self.storage.get_device_signatures(device['id'])
            if not signatures:
                continue
            scores = [self._similarity(event, sig) for sig in signatures]
            avg_score = sum(scores) / len(scores) if scores else 0
            if avg_score > 0:
                matches[device['name']] = round(avg_score * 100, 1)

        if matches:
            best = max(matches, key=matches.get)
            best_score = matches[best] / 100
            if best_score >= MIN_CONFIDENCE:
                device = next((d for d in known_devices if d['name'] == best), None)
                return {'device_id': device['id'] if device else None, 'device_name': best, 'confidence': round(best_score, 2), 'matches': matches}
        
        return {'device_id': None, 'device_name': None, 'confidence': 0, 'matches': matches}

    def _similarity(self, event, signature):
        scores = []
        peak_diff = abs(event['peak'] - signature['peak'])
        peak_score = max(0, 1 - (peak_diff / max(event['peak'], signature['peak'])))
        scores.append(peak_score * 0.4)
        
        avg_diff = abs(event['avg'] - signature['avg'])
        avg_score = max(0, 1 - (avg_diff / max(event['avg'], signature['avg'])))
        scores.append(avg_score * 0.3)
        
        dur_diff = abs(event['duration'] - signature['duration'])
        dur_score = max(0, 1 - (dur_diff / max(event['duration'], signature['duration'])))
        scores.append(dur_score * 0.15)
        
        if event.get('variance', 0) > 0 and signature.get('variance', 0) > 0:
            var_diff = abs(event['variance'] - signature['variance'])
            var_score = max(0, 1 - (var_diff / max(event['variance'], signature['variance'])))
            scores.append(var_score * 0.15)
        
        return sum(scores)
