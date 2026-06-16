"""Pattern matching engine for device detection using spike signatures."""

from .const import MIN_CONFIDENCE, SIMILARITY_THRESHOLD


class PatternMatcher:
    """Matches detected spikes against known device signatures."""

    def __init__(self):
        self.storage = None  # Set by coordinator

    def match_event(self, event, known_devices):
        """
        Match a detected event against known device signatures.
        
        Returns: {
            'device_id': device_id or None,
            'device_name': device_name or None,
            'confidence': 0.0-1.0,
            'matches': [{'device_name': score, ...}]
        }
        """
        if not known_devices:
            return {
                'device_id': None,
                'device_name': None,
                'confidence': 0,
                'matches': {}
            }

        matches = {}
        
        for device in known_devices:
            device_id = device['id']
            device_name = device['name']
            
            # Get signatures for this device
            signatures = self.storage.get_device_signatures(device_id)
            
            if not signatures:
                continue
            
            # Calculate match score against all signatures
            scores = [self._calculate_similarity(event, sig) for sig in signatures]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            if avg_score > 0:
                matches[device_name] = round(avg_score * 100, 1)
        
        # Find best match
        if matches:
            best_device_name = max(matches, key=matches.get)
            best_score = matches[best_device_name] / 100
            
            if best_score >= MIN_CONFIDENCE:
                device = next((d for d in known_devices if d['name'] == best_device_name), None)
                return {
                    'device_id': device['id'] if device else None,
                    'device_name': best_device_name,
                    'confidence': round(best_score, 2),
                    'matches': matches
                }
        
        return {
            'device_id': None,
            'device_name': None,
            'confidence': 0,
            'matches': matches
        }

    def _calculate_similarity(self, event, signature):
        """
        Calculate similarity between event and signature using multiple metrics.
        Returns 0-1 score.
        """
        scores = []
        
        # Peak similarity (most important)
        peak_diff = abs(event['peak'] - signature['peak'])
        peak_score = max(0, 1 - (peak_diff / max(event['peak'], signature['peak'])))
        scores.append(peak_score * 0.4)  # 40% weight
        
        # Average similarity
        avg_diff = abs(event['avg'] - signature['avg'])
        avg_score = max(0, 1 - (avg_diff / max(event['avg'], signature['avg'])))
        scores.append(avg_score * 0.3)  # 30% weight
        
        # Duration similarity (in seconds)
        event_dur = event['duration']
        sig_dur = signature['duration']
        dur_diff = abs(event_dur - sig_dur)
        dur_score = max(0, 1 - (dur_diff / max(event_dur, sig_dur)))
        scores.append(dur_score * 0.15)  # 15% weight
        
        # Variance/shape similarity (the curve shape)
        event_var = event.get('variance', 0)
        sig_var = signature.get('variance', 0)
        if event_var > 0 and sig_var > 0:
            var_diff = abs(event_var - sig_var)
            var_score = max(0, 1 - (var_diff / max(event_var, sig_var)))
            scores.append(var_score * 0.15)  # 15% weight
        
        return sum(scores)

    def get_learning_progress(self, device_id, storage):
        """Get how well we know a device based on signature count."""
        signatures = storage.get_device_signatures(device_id)
        count = len(signatures)
        
        if count == 0:
            return {'status': 'needs_learning', 'count': 0, 'confidence': 'very_low'}
        elif count < 3:
            return {'status': 'learning', 'count': count, 'confidence': 'low'}
        elif count < 7:
            return {'status': 'improving', 'count': count, 'confidence': 'medium'}
        else:
            return {'status': 'well_learned', 'count': count, 'confidence': 'high'}
