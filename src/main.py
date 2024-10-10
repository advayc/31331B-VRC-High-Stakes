# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       walto                                                        #
# 	Created:      10/4/2024, 3:20:43 PM                                        #
# 	Description:  V5 project with Arcade Drive and Conveyor Belt (R2 control)  #
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

# Max motor speed (percent) for motors controlled by buttons
MAX_SPEED = 100

# Deadband to prevent small joystick movements from causing unwanted motion
DEADBAND = 1

# Sensitivity multiplier
SENSITIVITY = 1.2

# Conveyor belt speed
CONVEYOR_SPEED = 50  # Adjust this value as needed

def apply_deadband(value, deadband):
    if abs(value) < deadband:
        return 0
    return value * (abs(value) - deadband) / (100 - deadband)

def apply_sensitivity(value, sensitivity):
    return value * sensitivity

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def drive_task():
    while True:
        # Arcade control with increased sensitivity
        forward = -apply_sensitivity(apply_deadband(controller.axis3.position(), DEADBAND), SENSITIVITY)
        turn = -apply_sensitivity(apply_deadband(controller.axis1.position(), DEADBAND), SENSITIVITY)

        # Calculate left and right motor speeds
        left_speed = forward + turn
        right_speed = forward - turn

        # Normalize speeds if they exceed 100%
        max_raw = max(abs(left_speed), abs(right_speed))
        if max_raw > 100:
            left_speed = (left_speed / max_raw) * 100
            right_speed = (right_speed / max_raw) * 100

        # Clamp speeds to ensure they're within -100 to 100 range
        left_speed = clamp(left_speed, -100, 100)
        right_speed = clamp(right_speed, -100, 100)

        # Send values to drive motors
        left_drive_1.spin(FORWARD, left_speed, PERCENT)
        left_drive_2.spin(FORWARD, left_speed, PERCENT)
        right_drive_1.spin(FORWARD, right_speed, PERCENT)
        right_drive_2.spin(FORWARD, right_speed, PERCENT)

        # Control conveyor belt with R2 button
        if controller.buttonR2.pressing():
            conveyor_motor.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
        else:
            conveyor_motor.stop()

        # Delay to prevent excessive CPU usage
        sleep(10)

# Run the drive code
drive = Thread(drive_task)

# Python now drops into REPL