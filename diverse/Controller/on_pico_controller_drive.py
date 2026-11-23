from WiFiHandler import WifiHandler
from diff_drive import DifferentialDrive

class onPicoControllerDrive:

    def __init__ (self):
        self.wifi = WifiHandler()
        self.diff_drive = DifferentialDrive()

    def run(self):
        while True:
            y_axis, z_axis, held_buttons = self.wifi.get_data()

            if(y_axis > 0):
                self.diff_drive.move_forward(y_axis)



           
