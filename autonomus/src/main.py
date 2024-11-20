# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       AdvayChandorkar                                              #
# 	Created:      11/7/2024, 3:47:35 PM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# wannabe path planning code (i dont know what im doing)

from vex import *
import math

brain = Brain()
controller = Controller()

# Drive motors
left_drive_1 = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
left_drive_2 = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
right_drive_1 = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
right_drive_2 = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)

conveyor_motor = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)

# pneumatic pistons connected to three-wire ports
piston1 = DigitalOut(brain.three_wire_port.c)
piston2 = DigitalOut(brain.three_wire_port.d)

CONVEYOR_SPEED = 100

# PID Constants for driving control
KP = 0.5  # proportional gain
KI = 0.01  # integral gain
KD = 0.1  # derivative gain

WHEEL_DIAMETER_INCHES = 4.0
WHEEL_CIRCUMFERENCE_INCHES = math.pi * WHEEL_DIAMETER_INCHES

# Robot heading initialization (0 degrees means facing forward)
robot_heading = 0 

# Define grid size / field size using a 2d list
GRID_SIZE = 11
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Convert inches to degrees for motor movement
def inches_to_degrees(target_distance_inches):
    return (target_distance_inches / WHEEL_CIRCUMFERENCE_INCHES) * 360

# Update robot's heading
def update_heading(turn_degrees):
    global robot_heading
    robot_heading = (robot_heading + turn_degrees) % 360

# Path planning function to move the robot in a straight line
def pid_drive(target_distance_inches):
    """
    Drives the robot forward by a specified distance (in inches) using PID control.
    """
    target_degrees = inches_to_degrees(target_distance_inches)
    
    # Reset motor positions
    left_drive_1.position(DEGREES)
    right_drive_1.position(DEGREES)
    
    error_sum = 0
    last_error = 0
    threshold = 5

    while True:
        # Calculate the current error (difference from target)
        current_position = (left_drive_1.position(DEGREES) + right_drive_1.position(DEGREES)) / 2
        error = target_degrees - current_position

        # Stop if within the threshold
        if abs(error) < threshold:
            break

        # PID terms
        error_sum += error
        derivative = error - last_error
        pid_output = (KP * error) + (KI * error_sum) + (KD * derivative)

        # Apply PID output to motors
        left_drive_1.spin(FORWARD, pid_output, PERCENT)
        left_drive_2.spin(FORWARD, pid_output, PERCENT)
        right_drive_1.spin(FORWARD, pid_output, PERCENT)
        right_drive_2.spin(FORWARD, pid_output, PERCENT)

        last_error = error
        sleep(20)

    # Stop motors after reaching target
    left_drive_1.stop()
    left_drive_2.stop()
    right_drive_1.stop()
    right_drive_2.stop()

def turn_to_heading(target_heading):
    """
    Turns the robot to a specific heading (angle) using PID control.
    """
    global robot_heading
    error = (target_heading - robot_heading) % 360

    while abs(error) > 5:
        if error < 180:
            turn_speed = 50  # Positive for turning right
        else:
            turn_speed = -50  # Negative for turning left

        left_drive_1.spin(FORWARD, turn_speed, PERCENT)
        left_drive_2.spin(FORWARD, turn_speed, PERCENT)
        right_drive_1.spin(REVERSE, turn_speed, PERCENT)
        right_drive_2.spin(REVERSE, turn_speed, PERCENT)

        sleep(20)

        # Update heading after each turn
        update_heading(turn_speed)

        error = (target_heading - robot_heading) % 360

    # Stop motors after reaching target heading
    left_drive_1.stop()
    left_drive_2.stop()
    right_drive_1.stop()
    right_drive_2.stop()

def autonomous():
    brain.screen.print("Autonomous mode started")
    controller.screen.print("Autonomous mode started")    
    controller.screen.clear_screen()

    # Move the pistons forward (extend)
    piston1.set(True)
    piston2.set(True)
    brain.screen.print("Pistons extended")
    controller.screen.print("Pistons extended")
    controller.screen.clear_screen()
    sleep(500)  # Wait for 0.5 seconds while pistons are extended

    # Move the robot right by rotating 90 degrees
    turn_to_heading(90)
    pid_drive(10)  # Move forward 10 inches

    conveyor_motor.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
    brain.screen.print("Conveyor running")
    controller.screen.print("Conveyor running")
    controller.screen.clear_screen()
    sleep(1000)
    conveyor_motor.stop()  # Stop conveyor

    # Move the pistons back (retract)
    piston1.set(False)
    piston2.set(False)
    brain.screen.print("Pistons retracted")
    controller.screen.print("Pistons retracted")
    controller.screen.clear_screen()
    sleep(500)

    # Move right by rotating another 90 degrees to face the original direction (180 degrees)
    turn_to_heading(180)  # Turn 90 degrees to the right (South)

    # Move forward for 10 inches (to reach the original position)
    pid_drive(10)

    # Turn to the initial position (0 degrees, facing North)
    turn_to_heading(0)

    brain.screen.print("Autonomous mode complete")
    controller.screen.print("Autonomous mode complete")
    controller.screen.clear_screen()


def drive_task():
    brain.screen.print("Driver control mode start")
    
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print("L2: Conveyor FWD", sep="")
    controller.screen.set_cursor(2, 1)
    controller.screen.print("R2: Conveyor REV", sep="")
    controller.screen.set_cursor(3, 1)
    controller.screen.print("L1/R1: Pistons", sep="")

    sleep(1000)

    while True:
        # Arcade drive control using left joystick
        forward = -controller.axis3.position()  # Forward/backward control
        turn = -controller.axis1.position()     # Left/right turn control

        # Calculate speeds for each side of the drive
        left_speed = forward + turn
        right_speed = forward - turn

        # Apply calculated speeds to motors
        left_drive_1.spin(FORWARD, left_speed, PERCENT)
        left_drive_2.spin(FORWARD, left_speed, PERCENT)
        right_drive_1.spin(FORWARD, right_speed, PERCENT)
        right_drive_2.spin(FORWARD, right_speed, PERCENT)

        # Conveyor control using L2 and R2 buttons
        if controller.buttonL2.pressing():
            conveyor_motor.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
        elif controller.buttonR2.pressing():
            conveyor_motor.spin(REVERSE, CONVEYOR_SPEED, PERCENT)
        else:
            conveyor_motor.stop()

        # Pneumatic piston control with L1 and R1 buttons
        if controller.buttonL1.pressing():
            piston1.set(True)
            piston2.set(True)
        elif controller.buttonR1.pressing():
            piston1.set(False)
            piston2.set(False)

        sleep(10)
        
autonomous()
drive = Thread(drive_task)
competition = Competition(drive_task, autonomous)