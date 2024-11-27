# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       Advay Chandorkar                                             #
# 	Created:      11/19/2024, 6:42:43 PM                                       #
# 	Description:  bobby settin                                                 #
#                                                                              #
# ---------------------------------------------------------------------------- #

from vex import *
import math

brain = Brain()
controller = Controller()

# Drive motors
left_drive_1 = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
left_drive_2 = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
right_drive_1 = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
right_drive_2 = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)

# Conveyor motor
conveyor_motor1 = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)
flag = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)

# Pneumatic pistons connected to three-wire ports
piston1 = Pneumatics(brain.three_wire_port.c)

# Constants
CONVEYOR_SPEED = 100
KP = 0.5  # proportional gain or the kashimr parmar
KI = 0.01  # integral gain
KD = 0.1  # derivative gain
WHEEL_DIAMETER_INCHES = 4.0
WHEEL_CIRCUMFERENCE_INCHES = math.pi * WHEEL_DIAMETER_INCHES

flagup = False

def toggle_flag_position(flagup=True):
    if flagup:
        # Run flag motor for 1 second (300 ms) to move down
        flag.spin(FORWARD, 30, PERCENT)
        sleep(300)
        flag.stop()
    else:
        # Run flag motor for 1 second (300 ms) to move up
        flag.spin(REVERSE, 25, PERCENT)
        sleep(300)
        flag.stop()

def inches_to_degrees(target_distance_inches):
    return (target_distance_inches / WHEEL_CIRCUMFERENCE_INCHES) * 360

def pid_drive(target_distance_inches):
    """
    Drives the robot forward by a specified distance (in inches) using PID control.
    """
    # Convert target distance from inches to motor degrees
    target_degrees = inches_to_degrees(target_distance_inches)
    
    # Reset motor positions
    left_drive_1.position(DEGREES)
    right_drive_1.position(DEGREES)
    
    error_sum = 0
    last_error = 0
    threshold = 5

    # PID loop for driving
    while True:
        current_position = (left_drive_1.position(DEGREES) + right_drive_1.position(DEGREES)) / 2
        error = target_degrees - current_position

        if abs(error) < threshold:
            break

        error_sum += error
        derivative = error - last_error
        pid_output = (KP * error) + (KI * error_sum) + (KD * derivative)

        left_drive_1.spin(FORWARD, pid_output, PERCENT)
        left_drive_2.spin(FORWARD, pid_output, PERCENT)
        right_drive_1.spin(FORWARD, pid_output, PERCENT)
        right_drive_2.spin(FORWARD, pid_output, PERCENT)

        last_error = error
        sleep(20)

    left_drive_1.stop()
    left_drive_2.stop()
    right_drive_1.stop()
    right_drive_2.stop()

def autonomous():
    # Move forward for 2 seconds
    left_drive_1.spin(FORWARD, 35, PERCENT)
    left_drive_2.spin(FORWARD, 35, PERCENT)
    right_drive_1.spin(FORWARD, 35, PERCENT)
    right_drive_2.spin(FORWARD, 35, PERCENT)
    sleep(2000)

    # Stop motors
    left_drive_1.stop()
    left_drive_2.stop()
    right_drive_1.stop()
    right_drive_2.stop()
    sleep(500)

    # Stop motors
    left_drive_1.stop()
    left_drive_2.stop()
    right_drive_1.stop()
    right_drive_2.stop()

def display_controls_summary():
    """
    Displays a summary of controls on the controller screen.
    """
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print("L1/R1 PISTON OPEN")
    controller.screen.set_cursor(2, 1)
    controller.screen.print("L2/R2 PISTON CLOSE")
    controller.screen.set_cursor(3, 1)
    controller.screen.print("R JOYSTICK")
    
def drive_task():
    brain.screen.print("Driver control mode started")
    display_controls_summary()
    sleep(1000)

    while True:
        forward = controller.axis3.position()  # Forward/backward control
        turn = controller.axis4.position()     # Left/right turn control

        left_speed = forward + turn
        right_speed = forward - turn

        left_drive_1.spin(REVERSE, left_speed, PERCENT)
        left_drive_2.spin(REVERSE, left_speed, PERCENT)
        right_drive_1.spin(REVERSE, right_speed, PERCENT)
        right_drive_2.spin(REVERSE, right_speed, PERCENT)

        # Conveyor control using right joystick (vertical axis only)
        conveyor_speed = controller.axis2.position()
        if conveyor_speed != 0:
            conveyor_motor1.spin(FORWARD, conveyor_speed, PERCENT)
        else:
            conveyor_motor1.stop()

        # Pneumatic control using L1 and R1 buttons
        if controller.buttonL1.pressing():
            piston1.close()
        if controller.buttonR1.pressing():
            piston1.close()
        elif controller.buttonR2.pressing():
            piston1.open()
        elif controller.buttonL2.pressing():
            piston1.open()
        
        # Flag control
        if controller.buttonUp.pressing():
            toggle_flag_position()
            sleep(300)  # Debounce delay
        elif controller.buttonDown.pressing():
            toggle_flag_position(False)
            sleep(300)  # Debounce delay

        
        sleep(10)

# Competition setup
competition = Competition(drive_task, autonomous)