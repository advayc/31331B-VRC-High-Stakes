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

# Conveyor belt speed
CONVEYOR_SPEED = 80  # Adjust this value as needed

def drive_task():
    while True:
        # Arcade control
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

        # Delay to prevent excessive CPU usage
        sleep(10)

def autonomous_routine():
    # Move forward for 1 second
    left_drive_1.spin(FORWARD, 100, PERCENT)
    left_drive_2.spin(FORWARD, 100, PERCENT)
    right_drive_1.spin(FORWARD, 100, PERCENT)
    right_drive_2.spin(FORWARD, 100, PERCENT)
    sleep(1000)  # Move forward for 1000 milliseconds (1 second)
    
    # Run the intake (conveyor) for 1 second
    conveyor_motor.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
    sleep(1000)  # Run intake for 1000 milliseconds (1 second)
    
    # Stop the conveyor
    conveyor_motor.stop()

    # Move forward for another second
    left_drive_1.spin(FORWARD, 100, PERCENT)
    left_drive_2.spin(FORWARD, 100, PERCENT)
    right_drive_1.spin(FORWARD, 100, PERCENT)
    right_drive_2.spin(FORWARD, 100, PERCENT)
    sleep(1000)  # Move forward for 1000 milliseconds (1 second)

    # Stop the motors
    left_drive_1.stop()
    left_drive_2.stop()
    right_drive_1.stop()
    right_drive_2.stop()

# Run the drive code in a thread
drive = Thread(drive_task)

# Wait for button X to start the autonomous routine
while True:
    if controller.buttonX.pressing():
        # Start autonomous routine
        autonomous_routine()
        break  # Exit the loop after starting autonomous

# Python now drops into REPL
