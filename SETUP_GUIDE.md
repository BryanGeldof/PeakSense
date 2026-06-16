# PeakSense Automation Templates
# Copy-paste these into your automations!

# ============================================
# 1. FEED POWER METER DATA
# ============================================

- alias: "PeakSense: Feed power meter"
  trigger:
    - platform: state
      entity_id: sensor.p1_meter_total_power  # CHANGE THIS!
  action:
    - service: peaksense.update
      data:
        value: "{{ states('sensor.p1_meter_total_power') | float }}"
  mode: queued

# ============================================
# 2. REGISTER DEVICES (run once)
# ============================================

- alias: "PeakSense: Register Coffee Machine"
  trigger:
    - platform: time
      at: "05:00:00"
  action:
    - service: peaksense.register_device
      data:
        name: "Coffee Machine"
        standby_power: 5
        notes: "Delonghi Magnifica ESAM3300"

- alias: "PeakSense: Register Washing Machine"
  trigger:
    - platform: time
      at: "05:05:00"
  action:
    - service: peaksense.register_device
      data:
        name: "Washing Machine"
        standby_power: 2
        notes: "ASKO W6984, max 2000W"

- alias: "PeakSense: Register Dishwasher"
  trigger:
    - platform: time
      at: "05:10:00"
  action:
    - service: peaksense.register_device
      data:
        name: "Dishwasher"
        standby_power: 3
        notes: "Bosch SHX68ZN55N, max 2400W"

- alias: "PeakSense: Register Electric Oven"
  trigger:
    - platform: time
      at: "05:15:00"
  action:
    - service: peaksense.register_device
      data:
        name: "Oven"
        standby_power: 1
        notes: "Oven, max 3000W"

# ============================================
# 3. NOTIFICATION ON DEVICE DETECTION
# ============================================

- alias: "PeakSense: Notify device detection"
  trigger:
    - platform: state
      entity_id: sensor.peaksense_current_device
      from: "unknown"
  condition:
    - condition: template
      value_template: "{{ states('sensor.peaksense_detection_confidence') | float > 75 }}"
  action:
    - service: notify.notify
      data:
        title: "Device Detected"
        message: |
          Device: {{ states('sensor.peaksense_current_device') }}
          Power: {{ states('sensor.peaksense_last_event') }}W
          Confidence: {{ states('sensor.peaksense_detection_confidence') }}%

# ============================================
# 4. RECORD TRAINING DATA
# Run this when a device is running, fill in event_id + device_id
# ============================================

- alias: "PeakSense: Record Coffee Machine Signature"
  trigger:
    - platform: homeassistant
      event: start
  action:
    - service: peaksense.record_signature
      data:
        event_id: 5      # FILL IN: from sensor.peaksense_last_event.id
        device_id: 1     # FILL IN: device number from registration

# ============================================
# 5. DETECT STANDBY POWER
# ============================================

- alias: "PeakSense: Detect standby power nightly"
  trigger:
    - platform: time
      at: "23:00:00"
  action:
    - service: peaksense.update
      data:
        value: "{{ states('sensor.p1_meter_total_power') | float }}"
  # This records baseline power with no devices running

# ============================================
# 6. FEEDBACK ON DETECTION
# Call this when you see a wrong detection
# ============================================

- alias: "PeakSense: Correction feedback"
  trigger:
    - platform: homeassistant
      event: start
  action:
    - service: peaksense.provide_feedback
      data:
        event_id: 42      # FILL IN: the event ID
        device_id: 1      # FILL IN: correct device ID
        is_correct: false # Set to true if detection WAS correct

# ============================================
# 7. UPDATE DEVICE INFO
# ============================================

- alias: "PeakSense: Update device standby power"
  trigger:
    - platform: homeassistant
      event: start
  action:
    - service: peaksense.update_device
      data:
        device_id: 1
        standby_power: 3  # New standby power
        notes: "Updated: confirmed 3W standby"

# ============================================
# 8. TRACK HIGH CONSUMPTION DEVICES
# ============================================

- alias: "PeakSense: Alert on high consumption"
  trigger:
    - platform: state
      entity_id: sensor.peaksense_last_event
  condition:
    - condition: template
      value_template: "{{ states('sensor.peaksense_last_event') | float > 3000 }}"
  action:
    - service: notify.notify
      data:
        title: "High Power Consumption"
        message: |
          Detected: {{ states('sensor.peaksense_current_device') }}
          Power: {{ states('sensor.peaksense_last_event') }}W

# ============================================
# 9. DAILY TRAINING ROUTINE
# ============================================

- alias: "PeakSense: Morning training"
  trigger:
    - platform: time
      at: "06:00:00"
  action:
    - service: notify.notify
      data:
        message: "Time to train PeakSense! Run your devices and record signatures."
        title: "PeakSense Training"

# ============================================
# 10. STATISTICS LOGGING
# Log detection accuracy daily
# ============================================

- alias: "PeakSense: Daily accuracy check"
  trigger:
    - platform: time
      at: "23:30:00"
  action:
    - service: logger.set_level
      data:
        peaksense: debug
    # Check /config/peaksense.db for stats
