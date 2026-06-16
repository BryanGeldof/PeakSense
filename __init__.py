update:
  name: Update
  description: Send a power value to PeakSense
  fields:
    value:
      name: Value
      description: Power value in watts
      required: true
      example: 1200
      selector:
        number:
          min: 0
          max: 10000

register_device:
  name: Register Device
  description: Register a new device for learning
  fields:
    name:
      name: Device Name
      description: Name of the device (e.g., "Washing Machine")
      required: true
      example: "Washing Machine"
      selector:
        text:
    standby_power:
      name: Standby Power
      description: Power consumption in standby mode (W)
      required: false
      example: 2
      selector:
        number:
          min: 0
          max: 1000
    notes:
      name: Notes
      description: Additional notes about the device
      required: false
      selector:
        text:

record_signature:
  name: Record Signature
  description: Record a spike as a device signature for learning
  fields:
    event_id:
      name: Event ID
      description: The ID of the spike event
      required: true
      example: 1
      selector:
        number:
          min: 1
    device_id:
      name: Device ID
      description: The device to train
      required: true
      example: 1
      selector:
        number:
          min: 1

label_event:
  name: Label Event
  description: Label an event (legacy method)
  fields:
    event_id:
      name: Event ID
      description: The event to label
      required: true
      example: 1
      selector:
        number:
          min: 1
    label:
      name: Label
      description: Label text
      required: true
      example: "Washing Machine"
      selector:
        text:

provide_feedback:
  name: Provide Feedback
  description: Train the model by providing feedback on detections
  fields:
    event_id:
      name: Event ID
      description: The spike event
      required: true
      example: 1
      selector:
        number:
          min: 1
    device_id:
      name: Device ID
      description: The device
      required: true
      example: 1
      selector:
        number:
          min: 1
    is_correct:
      name: Is Correct
      description: Whether the detection was correct
      required: true
      default: true
      selector:
        boolean:

update_device:
  name: Update Device
  description: Update device information
  fields:
    device_id:
      name: Device ID
      description: The device to update
      required: true
      example: 1
      selector:
        number:
          min: 1
    name:
      name: Name
      description: New device name
      required: false
      selector:
        text:
    standby_power:
      name: Standby Power
      description: New standby power value
      required: false
      selector:
        number:
          min: 0
          max: 1000
    notes:
      name: Notes
      description: New notes
      required: false
      selector:
        text:

delete_device:
  name: Delete Device
  description: Delete a device and all its data
  fields:
    device_id:
      name: Device ID
      description: The device to delete
      required: true
      example: 1
      selector:
        number:
          min: 1
