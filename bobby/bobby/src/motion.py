# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       motion.py                                                    #
# 	Author:       Advay Chandorkar                                             #
# 	Created:      12/3/2024, 6:24:37 PM                                        #
# 	Description:  bobby drive settings with motion profiling and PID           #
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
        flag.spin(FORWARD, 30, PERCENT)
        sleep(300)
        flag.stop()
    else:
        flag.spin(REVERSE, 25, PERCENT)
        sleep(300)
        flag.stop()

def inches_to_degrees(target_distance_inches):
    return (target_distance_inches / WHEEL_CIRCUMFERENCE_INCHES) * 360

# Motion Profiling Constants
MAX_VELOCITY = 80  # caps the maximum speed to 80% for control
ACCELERATION = 10  # how quickly robot speeds up (percent per second)
DECELERATION = 10  # how quickly robot slows down (percent per second)

def motion_profile_pid_drive(target_distance_inches):
    """
    combines motion profiling with pid control for smooth, accurate movements
    
    motion profile: handles acceleration/deceleration curves
    pid: ensures position accuracy
    
    the function:
    1. calculates target position in degrees
    2. uses motion profile to control velocity
    3. applies pid corrections for accuracy
    4. smoothly accelerates and decelerates
    5. stops when target is reached within threshold
    """
    target_degrees = inches_to_degrees(target_distance_inches)
    left_drive_1.set_position(0, DEGREES)
    right_drive_1.set_position(0, DEGREES)
    
    current_velocity = 0
    current_position = 0
    error_sum = 0
    last_error = 0
    threshold = 5  # Adjusted threshold for stopping accuracy

    # PID Constants
    KP, KI, KD = get_scaled_pid_constants(target_distance_inches)

    while True:
        current_position = (left_drive_1.position(DEGREES) + right_drive_1.position(DEGREES)) / 2
        error = target_degrees - current_position

        if abs(error) < threshold:
            break

        # Accumulate error with anti-windup
        error_sum = max(min(error_sum + error, 1000), -1000)  
        derivative = error - last_error
        pid_output = (KP * error) + (KI * error_sum) + (KD * derivative)

        # Determine if we should accelerate, maintain speed, or decelerate
        remaining_distance = target_degrees - current_position
        if remaining_distance < (current_velocity ** 2) / (2 * DECELERATION):
            current_velocity = max(current_velocity - DECELERATION * 0.02, 0)
        else:
            current_velocity = min(current_velocity + ACCELERATION * 0.02, MAX_VELOCITY)

        # Combine PID output with motion profiling
        final_output = max(min(pid_output, current_velocity), -current_velocity)

        # Spin motors with the final output
        left_drive_1.spin(FORWARD, final_output, PERCENT)
        left_drive_2.spin(FORWARD, final_output, PERCENT)
        right_drive_1.spin(FORWARD, final_output, PERCENT)
        right_drive_2.spin(FORWARD, final_output, PERCENT)

        last_error = error
        sleep(20)

    left_drive_1.stop(BRAKE)
    left_drive_2.stop(BRAKE)
    right_drive_1.stop(BRAKE)
    right_drive_2.stop(BRAKE)

def get_scaled_pid_constants(distance_inches):
    if distance_inches > 24:  # Long distance
        return 0.55, 0.015, 0.2
    elif distance_inches > 12:  # Medium distance
        return 0.45, 0.008, 0.12
    else:  # Short distance
        return 0.35, 0.004, 0.1

def rotate_left():
    TURN_SPEED = 50
    TURN_DURATION_MS = 350

    left_drive_1.spin(REVERSE, TURN_SPEED, PERCENT)
    left_drive_2.spin(REVERSE, TURN_SPEED, PERCENT)
    right_drive_1.spin(FORWARD, TURN_SPEED, PERCENT)
    right_drive_2.spin(FORWARD, TURN_SPEED, PERCENT)

    sleep(TURN_DURATION_MS)

    left_drive_1.stop(BRAKE)
    left_drive_2.stop(BRAKE)
    right_drive_1.stop(BRAKE)
    right_drive_2.stop(BRAKE)

def autonomous():
    """
    executes the autonomous routine
    
    sequence:
    1. open piston (grab game element)
    2. drive to scoring position (32 inches)
    3. close piston (release game element)
    4. back up (-6 inches)
    5. run conveyor
    6. back up more (-5 inches)
    7. rotate left (prepare for next task)
    
    each movement uses motion profiling with pid for smooth, accurate execution
    """
    piston1.open()
    motion_profile_pid_drive(32)
    piston1.close()
    sleep(500)
    motion_profile_pid_drive(-6)
    sleep(200)
    conveyor_motor1.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
    motion_profile_pid_drive(-5)
    rotate_left()

def display_controls_summary():
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
        forward = controller.axis3.position()
        turn = controller.axis4.position()

        left_speed = forward + turn
        right_speed = forward - turn

        left_drive_1.spin(REVERSE, left_speed, PERCENT)
        left_drive_2.spin(REVERSE, left_speed, PERCENT)
        right_drive_1.spin(REVERSE, right_speed, PERCENT)
        right_drive_2.spin(REVERSE, right_speed, PERCENT)

        conveyor_speed = controller.axis2.position()
        if conveyor_speed != 0:
            conveyor_motor1.spin(FORWARD, conveyor_speed, PERCENT)
        else:
            conveyor_motor1.stop()

        if controller.buttonL1.pressing():
            piston1.close()
        if controller.buttonR1.pressing():
            piston1.close()
        elif controller.buttonR2.pressing():
            piston1.open()
        elif controller.buttonL2.pressing():
            piston1.open()
        
        if controller.buttonUp.pressing():
            toggle_flag_position()
            sleep(300)
        elif controller.buttonDown.pressing():
            toggle_flag_position(False)
            sleep(300)

        sleep(10)

competition = Competition(drive_task, autonomous)