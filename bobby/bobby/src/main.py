# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       Arghya Vyas and Advay Chandorkar                             #
# 	Created:      12/3/2024, 6:24:37 PM                                        #
# 	Description:  jjjjjjkjkj                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
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
    # Correction factor to adjust for overshooting
    CORRECTION_FACTOR = 1.5  # Robot travels 1.5x the intended distance
    corrected_distance = target_distance_inches / CORRECTION_FACTOR
    return (corrected_distance / WHEEL_CIRCUMFERENCE_INCHES) * 360

def get_scaled_pid_constants(distance_inches):
    """
    Adjusts PID constants based on the distance to travel.
    Returns scaled values of KP, KI, and KD.
    """
    if distance_inches > 24:  # Long distance
        return 0.55, 0.015, 0.2  # Reduced Kp, slightly increased Kd
    elif distance_inches > 12:  # Medium distance
        return 0.45, 0.008, 0.12  # Reduced Kp, slightly increased Kd
    else:  # Short distance
        return 0.35, 0.004, 0.1  # Reduced Kp for greater precision
def pid_drive(target_distance_inches):
    """
    Drives the robot forward by a specified distance (in inches) using dynamically tuned PID control.
    """
    # Get scaled PID constants
    KP, KI, KD = get_scaled_pid_constants(target_distance_inches)
    
    # Convert target distance from inches to motor degrees
    target_degrees = inches_to_degrees(target_distance_inches)
    
    # Reset motor positions
    left_drive_1.set_position(0, DEGREES)
    right_drive_1.set_position(0, DEGREES)
    
    error_sum = 0
    last_error = 0
    threshold = 5  # Adjusted threshold for stopping accuracy

    # PID loop for driving
    while True:
        current_position = (left_drive_1.position(DEGREES) + right_drive_1.position(DEGREES)) / 2
        error = target_degrees - current_position

        if abs(error) < threshold:
            break

        # Accumulate error with anti-windup
        error_sum = max(min(error_sum + error, 1000), -1000)  
        derivative = error - last_error
        pid_output = (KP * error) + (KI * error_sum) + (KD * derivative)

        # Cap the PID output to prevent excessive speeds
        pid_output = max(min(pid_output, 80), -80)  # Lower max speed to reduce overshoot

        # Spin motors with PID output
        left_drive_1.spin(FORWARD, pid_output, PERCENT)
        left_drive_2.spin(FORWARD, pid_output, PERCENT)
        right_drive_1.spin(FORWARD, pid_output, PERCENT)
        right_drive_2.spin(FORWARD, pid_output, PERCENT)

        last_error = error
        sleep(20)

    # Stop all motors with a brake
    left_drive_1.stop(BRAKE)
    left_drive_2.stop(BRAKE)
    right_drive_1.stop(BRAKE)
    right_drive_2.stop(BRAKE)
def rotate_left():
    """
    Rotates the robot 90 degrees to the left using motor control.
    Assumes a differential drive system with equal speeds on left and right sides.
    """
    # Constants for rotation
    TURN_SPEED = 50  # Speed percentage for the turn
    TURN_DURATION_MS = 350  # Adjust this based on your robot's turning behavior

    # Spin motors to turn left
    left_drive_1.spin(REVERSE, TURN_SPEED, PERCENT)
    left_drive_2.spin(REVERSE, TURN_SPEED, PERCENT)
    right_drive_1.spin(FORWARD, TURN_SPEED, PERCENT)
    right_drive_2.spin(FORWARD, TURN_SPEED, PERCENT)

    # Turn for a specified duration
    sleep(TURN_DURATION_MS)

    # Stop all motors with a brake
    left_drive_1.stop(BRAKE)
    left_drive_2.stop(BRAKE)
    right_drive_1.stop(BRAKE)
    right_drive_2.stop(BRAKE)

def autonomous():
    piston1.open()
    pid_drive(32)   
   # Pause
    piston1.close()
    sleep(500)
    pid_drive(-6)
    sleep(200)
    conveyor_motor1.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
    pid_drive(-5)
    rotate_left()

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
