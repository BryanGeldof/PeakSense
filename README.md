# ⚡ PeakSense v0.6.0

**Automatic Household Device Detection for Home Assistant - NO CODE Setup**

> Automatically recognize which device is using power by analyzing the unique "fingerprint" of its consumption pattern.

## 🎯 What is PeakSense?

PeakSense watches your home's power consumption and learns to recognize each appliance by the distinct way it uses electricity. Once trained, it tells you which device is running in real-time.

### Perfect for:
- 🔌 Energy monitoring and optimization
- 📊 Home Assistant Energy Dashboard
- 🏠 Smart home automation
- ⚡ Understanding which devices consume power

---

## ⚡ Installation (2 Minutes - NO CODE!)

### Step 1: Install via HACS

```
HACS → Integrations → Custom Repositories
Add: https://github.com/BryanGeldof/PeakSense
Type: Integration
→ Install → Restart Home Assistant
```

### Step 2: Configure (Interactive Setup)

**Settings → Devices & Services → + Add Integration → PeakSense**

The setup wizard will ask you:
1. **Select your power meter** (sensor or custom calculation like grid-solar+battery)
2. **Add devices to monitor** (optional - can add anytime later)

**That's it!** ✅ Automation is created automatically!

---

## 📊 What You Get

After setup, 5 new sensors appear:

| Sensor | Shows | Example |
|--------|-------|---------|
| `sensor.peaksense_last_event` | Peak power of last spike | 1850 W |
| `sensor.peaksense_status` | Is a spike happening? | active / idle |
| `sensor.peaksense_current_device` | Detected device | "Washing Machine" |
| `sensor.peaksense_detection_confidence` | How sure? | 92% |
| `sensor.{device_name}_power` | Per-device power | "Washing Machine Power": 1850 W |

**Per-device sensors can be added directly to Energy Dashboard!**

---

## 🎓 Training Your First Device (5 Minutes)

### 1. Register Device

**Developer Tools → Services**

```
Service: peaksense.register_device
Data:
  name: "Washing Machine"
  standby_power: 2
```

### 2. Run Device 5 Times

Turn on your washing machine and let it complete its cycle.

### 3. Record Signatures

After each run:
- Look at `sensor.peaksense_last_event` → note the `id`
- Call:

```
Service: peaksense.record_signature
Data:
  event_id: 5
  device_id: 1
```

### 4. Test

Next time you run the device, `sensor.peaksense_current_device` should show "Washing Machine" automatically!

---

## 🎨 Using in Energy Dashboard

1. **Settings → Dashboards → Energy**
2. **Configure consumption**
3. Add sensor: `sensor.washing_machine_power` (or any device you trained)

Now your Energy Dashboard shows each device's consumption!

---

## 💡 How It Works (In Plain English)

1. **Detects spikes** — When power jumps above 800W, PeakSense starts listening
2. **Records pattern** — Stores peak wattage, average, duration, and shape
3. **Learns signatures** — After 5 similar spikes, it recognizes the device
4. **Matches patterns** — When a new spike matches a known device, it identifies it
5. **Shows power** — Stores the power value in a sensor for that device

### Example:
```
Your Washing Machine uses 1900W
After 5 training runs, PeakSense knows: 1900W peak = Washing Machine
Tomorrow when you run it again: 1850W peak → "Ah, that's the Washing Machine!" (92% confidence)
```

---

## 🔧 Services (For Advanced Users)

### peaksense.update
Manually send a power value (normally automatic):
```
Data: {"value": 1200}
```

### peaksense.register_device
Register a new device:
```
Data: {"name": "Coffee Machine", "standby_power": 3}
```

### peaksense.record_signature
Record a spike as training data:
```
Data: {"event_id": 5, "device_id": 1}
```

### peaksense.delete_device
Remove a device:
```
Data: {"device_id": 1}
```

---

## ❓ FAQ

**Q: Do I need to write automations?**  
A: NO! PeakSense auto-creates the automation that reads your power meter.

**Q: Can I use a calculated power (grid - solar + battery)?**  
A: YES! During setup, select any sensor or helper (custom calculation).

**Q: How many devices can I train?**  
A: Unlimited! Add as many as you want.

**Q: How accurate is it?**  
A: Very! With 5+ training runs, accuracy is usually 90%+. More runs = more accurate.

**Q: Can I see which device is using power right now?**  
A: YES! Check `sensor.peaksense_current_device` and the per-device power sensors.

**Q: Does it work with solar panels and batteries?**  
A: YES! Use your net consumption (grid - solar + battery discharge).

**Q: Can I add this to Energy Dashboard?**  
A: YES! Use the per-device sensors like `sensor.washing_machine_power`.

---

## 🚀 Next Steps

1. ✅ Set up PeakSense
2. ✅ Train your first device (5 runs)
3. ✅ Add device sensor to Energy Dashboard
4. ✅ Train more devices
5. ✅ Watch PeakSense identify your appliances!

---

## 📞 Getting Help

- **Settings → System → Logs** - Search for "peaksense" to see what's happening
- **Developer Tools → Services** - Test services manually
- **GitHub Issues** - Report problems

---

## 📜 License

MIT - Free to use and modify

---

**Enjoy automatic device detection!** ⚡
