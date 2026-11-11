# This file contains the WiiRemote class, which is a helper class for getting inputs from a wii remote
# This class only works for linux as it uses the linux-specific evdev module

import evdev

# usefull documentation: https://python-evdev.readthedocs.io/en/latest/index.html

class WiiRemote:
    def __init__(self, InputDir="/dev/input", but=True, gyro=True, ir=True, acc=True):
        self.buttons = None
        self.gyroscope = None
        self.ir = None
        self.accelerometer = None
        self.associate_wii_devices(get_but=but, get_gyro=gyro, get_ir=ir, get_acc=acc)
    
    def __del__(self):
        self.close()
    
    def associate_wii_devices(self, get_but=True, get_gyro=True, get_ir=True, get_acc=True):
        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            if device.name == "Nintendo Wii Remote" and self.buttons == None and get_but:
                self.buttons = device
                self.buttons.grab()
            elif device.name == "Nintendo Wii Remote Motion Plus" and self.gyroscope == None and get_gyro:
                self.gyroscope = device
                self.gyroscope.grab()
            elif device.name == "Nintendo Wii Remote IR" and self.ir == None and get_ir:
                self.ir = device
                self.ir.grab()
            elif device.name == "Nintendo Wii Remote Accelerometer" and self.accelerometer == None and get_acc:
                self.accelerometer = device
                self.accelerometer.grab()
            else:
                device.close()
                continue
        
        if self.buttons == None and get_but: raise ValueError("wii remote buttons not found in devices")
        if self.gyroscope == None and get_gyro: raise ValueError("wii remote gyroscope not found in devices")
        if self.ir == None and get_ir: raise ValueError("wii remote ir not found in devices")
        if self.accelerometer == None and get_acc: raise ValueError("wii remote accelerometer not found in devices")

    def get_but_events(self):
        """
        returns a list of lists of all button events orginazed as [[timestamp, button, value], [timestamp, button, value]]
        """
        key_events = []
        try:
            for event in self.buttons.read():
                if event.type == evdev.ecodes.EV_KEY:
                    event_val = [event.timestamp(), event.code, event.value]
                    key_events.append(event_val)
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
            (self.ir.absinfo(16)[0], self.ir.absinfo(17)[0]),
            (self.ir.absinfo(18)[0], self.ir.absinfo(19)[0]),
            (self.ir.absinfo(20)[0], self.ir.absinfo(21)[0]),
            (self.ir.absinfo(22)[0], self.ir.absinfo(23)[0]))
    
    def close(self):
        self.buttons.ungrab()
        self.gyroscope.ungrab()
        self.ir.ungrab()
        self.accelerometer.ungrab()