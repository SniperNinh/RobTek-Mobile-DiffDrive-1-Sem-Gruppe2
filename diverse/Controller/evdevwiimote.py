import evdev, time

class WiiRemote:
    def __init__(self, InputDir="/dev/input", ):
        self.buttons = None
        self.gyroscope = None
        self.ir = None
        self.accelerometer = None
        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            if device.name == "Nintendo Wii Remote" and self.buttons == None:
                self.buttons = device
            elif device.name == "Nintendo Wii Remote Motion Plus" and self.gyroscope == None:
                self.gyroscope = device
            elif device.name == "Nintendo Wii Remote IR" and self.ir == None:
                self.ir = device
            elif device.name == "Nintendo Wii Remote Accelerometer" and self.accelerometer == None:
                self.accelerometer = device
            else:
                device.close()
                continue
        
        if self.buttons == None: raise ValueError("wii remote buttons not found in devices")
        if self.gyroscope == None: raise ValueError("wii remote gyroscope not found in devices")
        if self.ir == None: raise ValueError("wii remote ir not found in devices")
        if self.accelerometer == None: raise ValueError("wii remote accelerometer not found in devices")
    
    def get_but_events(self):
        """
        returns a list of tuples orginazed as (timestamp, button, value)
        """
        key_events = []
        try:
            for event in self.buttons.read():
                if event.type == evdev.ecodes.EV_KEY:
                    event_tuple = (event.timestamp(), event.code, event.value)
                    key_events.extend(event_tuple)
        except BlockingIOError: pass
        return key_events
    def get_acc_val(self):
        """
        returns a tuple containing the values of the 3 axes in the format (x, y, z)
        """
        return (
            self.accelerometer.absinfo(3)[0],
            self.accelerometer.absinfo(4)[0],
            self.accelerometer.absinfo(5)[0])
    def get_gyro_val(self):
        """
        returns a tuple containing the values of the 3 axes in the format (x, y, z)
        """
        return (
            self.gyroscope.absinfo(3)[0],
            self.gyroscope.absinfo(4)[0],
            self.gyroscope.absinfo(5)[0])
    def get_ir_val(self):
        """
        returns a tuple of tuples containing the values of the format ((x0, y0), (x1, y1), (x2, y2), (x3, y3))
        """
        return (
            (self.ir.absinfo(16)[0], wiimote.ir.absinfo(17)[0]),
            (self.ir.absinfo(18)[0], wiimote.ir.absinfo(19)[0]),
            (self.ir.absinfo(20)[0], wiimote.ir.absinfo(21)[0]),
            (self.ir.absinfo(22)[0], wiimote.ir.absinfo(23)[0]))