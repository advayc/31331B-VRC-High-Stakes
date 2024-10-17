# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       walto                                                        #
# 	Created:      10/4/2024, 3:20:43 PM                                        #
# 	Description:  V5 project with Arcade Drive, Conveyor Belt, and Pneumatics  #
#                                                                              #
# ---------------------------------------------------------------------------- #

from vex import *

# Brain should be defined by default
brain = Brain()

# The controller
controller = Controller()

# Drive motors
left_drive_1 = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
left_drive_2 = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
right_drive_1 = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
right_drive_2 = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)

# Conveyor belt motor
conveyor_motor = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)

# Pneumatic piston connected to three-wire port A
piston = DigitalOut(brain.three_wire_port.a)

# Conveyor belt speed
CONVEYOR_SPEED = 95  # Adjust this value as needed

def drive_task():
    while True:
        # Arcade control without sensitivity and deadband
        forward = -controller.axis3.position()  # Left stick vertical
        turn = -controller.axis1.position()     # Left stick horizontal

        # Calculate left and right motor speeds
        left_speed = forward + turn
        right_speed = forward - turn

        # Send values to drive motors
        left_drive_1.spin(FORWARD, left_speed, PERCENT)
        left_drive_2.spin(FORWARD, left_speed, PERCENT)
        right_drive_1.spin(FORWARD, right_speed, PERCENT)
        right_drive_2.spin(FORWARD, right_speed, PERCENT)

        # Control conveyor belt with L2 and R2 buttons
        if controller.buttonL2.pressing():
            conveyor_motor.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
        elif controller.buttonR2.pressing():
            conveyor_motor.spin(REVERSE, CONVEYOR_SPEED, PERCENT)
        else:
            conveyor_motor.stop()

        # Control pneumatic piston with L1 and L2 buttons
        if controller.buttonL1.pressing():
            piston.set(True)  # Extend piston
        elif controller.buttonL2.pressing():
            piston.set(False)  # Retract piston

        # Delay to prevent excessive CPU usage
        sleep(10)

# Run the drive code
drive = Thread(drive_task)

# Python now drops into REPL
