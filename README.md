# ⚡ PeakSense v0.5.0

**Intelligent Power Spike Detection & Device Recognition for Home Assistant**

Automatically detect which household device is using power based on its unique consumption fingerprint.

## 🎯 Features

✅ **Interactive Setup** — Configure your power meter and devices during installation  
✅ **Device Auto-Learning** — Records spike patterns (signatures) for recognition  
✅ **Intelligent Matching** — AI-based similarity scoring (peak, average, duration, shape)  
✅ **Easy Management** — Add/edit/delete devices anytime via services or UI  
✅ **Confidence Scoring** — See how sure the system is (0-100%)  
✅ **Feedback Training** — Improve accuracy by correcting detections  
✅ **REST API** — Full access to events, devices, and statistics  
✅ **SQLite Database** — All data stored locally, no cloud required  

---

## 🚀 Installation (3 steps)

### Step 1: Install via HACS

```
HACS → Integrations → + Custom repositories
Repository: https://github.com/BryanGeldof/PeakSense
Category: Integration
→ Install → Restart HA
```

### Step 2: Add Integration & Configure

**Settings → Devices & Services → + Add Integration → PeakSense**

You will be asked:
1. **Power Meter** — Select your home's total power consumption sensor
2. **Devices** — (Optional) Add devices now or add them later

That's it! ✅

### Step 3: Create Automation

**Settings → Automations → Create New**

```yaml
alias: Feed power to PeakSense
trigger:
  - platform: state
    entity_id: sensor.p1_meter_total_power  # YOUR POWER METER!
action:
  - service: peaksense.update
    data:
      value: "{{ states('sensor.p1_meter_total_power') | float }}"
mode: queued
```

---

## 📊 What You Get

After setup, you have **4 new sensors**:
- `sensor.peaksense_last_event` — Peak wattage
- `sensor.peaksense_status` — Active/idle
- `sensor.peaksense_current_device` — Detected device name
- `sensor.peaksense_detection_confidence` — Confidence %

---

## 🎓 Training a Device (5 minutes)

### 1. Register Device

**Developer Tools → Services**

```yaml
service: peaksense.register_device
data:
  name: "Washing Machine"
  standby_power: 2
  notes: "ASKO W6984"
```

### 2. Run Device 5 Times

Turn on your washing machine (or other device) and let it run.

### 3. Record Signatures

For each run:
- Find `sensor.peaksense_last_event` → look at the `id`
- Call:

```yaml
service: peaksense.record_signature
data:
  event_id: 5
  device_id: 1
```

### 4. Test

Next time you run the device, check `sensor.peaksense_current_device` — it should detect it automatically!

---

## 🔧 Services

### peaksense.update
Send a power value
```yaml
service: peaksense.update
data:
  value: 1500
```

### peaksense.register_device
Register a new device
```yaml
service: peaksense.register_device
data:
  name: "Coffee Machine"
  standby_power: 3
  notes: "Delonghi Magnifica"
```

### peaksense.record_signature
Train on a spike
```yaml
service: peaksense.record_signature
data:
  event_id: 42
  device_id: 1
```

### peaksense.provide_feedback
Improve with feedback
```yaml
service: peaksense.provide_feedback
data:
  event_id: 42
  device_id: 1
  is_correct: true
```

### peaksense.update_device
Change device settings
```yaml
service: peaksense.update_device
data:
  device_id: 1
  standby_power: 5
```

### peaksense.delete_device
Remove a device
```yaml
service: peaksense.delete_device
data:
  device_id: 1
```

---

## 📈 REST API

### GET `/api/peaksense/events`
All spike events

### GET `/api/peaksense/devices`
All devices with statistics

### GET `/api/peaksense/stats`
Accuracy statistics

---

## ⚙️ Configuration Changes

To change your power meter or add devices later:

1. **Settings → Devices & Services → PeakSense**
2. Click the entry
3. Click the gear icon (options)
4. Edit power meter or devices

---

## 📋 Example: Full Setup

```yaml
# 1. Register devices
- service: peaksense.register_device
  data:
    name: "Washing Machine"
    standby_power: 2

- service: peaksense.register_device
  data:
    name: "Coffee Machine"
    standby_power: 3

# 2. Record signatures (when devices run)
- service: peaksense.record_signature
  data:
    event_id: 1
    device_id: 1

# 3. Feedback for improvement
- service: peaksense.provide_feedback
  data:
    event_id: 1
    device_id: 1
    is_correct: true
```

---

## 🎨 Dashboard Example

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - sensor.peaksense_last_event
      - sensor.peaksense_status
      - sensor.peaksense_current_device
      - sensor.peaksense_detection_confidence

  - type: button
    name: Test 1000W
    action_type: call-service
    service: peaksense.update
    service_data:
      value: 1000
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| No spikes detected | Check automation is running, verify power meter is correct |
| Wrong device detected | Need more training (5-7 signatures per device) |
| Low confidence | Device signatures might be too similar |
| Can't find event ID | Look in `sensor.peaksense_last_event` attributes |

---

## 📊 Database

Data is stored in `/config/peaksense.db` (SQLite):
- `events` — Detected spikes
- `devices` — Registered devices
- `signatures` — Learning data
- `detections` — Recognition results

---

## 📜 License

MIT License

---

**Happy device detection!** ⚡
