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

# Pneumatic piston connected to three-wire port c and d
piston1 = DigitalOut(brain.three_wire_port.c)
piston2 = DigitalOut(brain.three_wire_port.d)

# Conveyor belt speed
CONVEYOR_SPEED = 100

def autonomous():
    # Move forward at medium speed
    left_speed = 50
    right_speed = 50
    left_drive_1.spin(FORWARD, left_speed, PERCENT)
    left_drive_2.spin(FORWARD, left_speed, PERCENT)
    right_drive_1.spin(FORWARD, right_speed, PERCENT)
    right_drive_2.spin(FORWARD, right_speed, PERCENT)
    
    # Run for 2 seconds
    sleep(1000)
    
    # Turn left (right motors forward, left motors reverse)
    left_drive_1.spin(REVERSE, left_speed, PERCENT)
    left_drive_2.spin(REVERSE, left_speed, PERCENT)
    right_drive_1.spin(FORWARD, right_speed, PERCENT)
    right_drive_2.spin(FORWARD, right_speed, PERCENT)
    
    # Turn for 1 second
    sleep(1000)
    
    # Stop turning
    left_drive_1.stop()
    left_drive_2.stop()
    right_drive_1.stop()
    right_drive_2.stop()
    
    # Move forward and activate the conveyor motor
    left_drive_1.spin(FORWARD, left_speed, PERCENT)
    left_drive_2.spin(FORWARD, left_speed, PERCENT)
    right_drive_1.spin(FORWARD, right_speed, PERCENT)
    right_drive_2.spin(FORWARD, right_speed, PERCENT)
    conveyor_motor.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
    conveyor_motor.spin(REVERSE, CONVEYOR_SPEED, PERCENT)
    piston1.set(True)  # Extend piston
    piston2.set(True)  # Extend piston
    piston1.set(False)  # Extend piston
    piston2.set(False)  # Extend piston

    # Run both for 2 seconds
    sleep(2000)
    
    # Stop all motors
    left_drive_1.stop()
    left_drive_2.stop()
    right_drive_1.stop()
    right_drive_2.stop()
    conveyor_motor.stop()

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

        # Control pneumatic piston with L1 and L2 buttons
        if controller.buttonL1.pressing():
            piston1.set(True)  # Extend piston
            piston2.set(True)  # Extend piston
        elif controller.buttonR1.pressing():
            piston1.set(False)  # Retract piston
            piston2.set(False)  # Retract piston

        # Delay to prevent excessive CPU usage
        sleep(10)

autonomous()
# Run the drive code
drive = Thread(drive_task)
competition = Competition(drive_task, autonomous)
# Python now drops into REPL
