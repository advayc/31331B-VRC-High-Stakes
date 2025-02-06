# ---------------------------------------------------------------------------- #
#                                                                              #
#  Module:       main.py                                                      #
#  Author:       Arghya Vyas and Advay Chandorkar                             #
#  Created:      12/3/2024, 6:24:37 PM                                        #
#  Description:  PID autonomous with touchscreen autonomous selection and     #
#                motor temperature monitoring.                                #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *
import math

# Initialize the brain and controller
brain = Brain()
controller = Controller()

# Drive motors
left_drive_1 = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
left_drive_2 = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
left_drive_3 = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)
right_drive_1 = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)
right_drive_2 = Motor(Ports.PORT5, GearSetting.RATIO_18_1, True)
right_drive_3 = Motor(Ports.PORT6, GearSetting.RATIO_18_1, True)

# Conveyor motor
conveyor_motor1 = Motor(Ports.PORT7 GearSetting.RATIO_18_1, False)

# Pneumatic piston connected to three-wire ports
piston1 = Pneumatics(brain.three_wire_port.c)

# Constants
CONVEYOR_SPEED = 100
WHEEL_DIAMETER_INCHES = 4.0
WHEEL_CIRCUMFERENCE_INCHES = math.pi * WHEEL_DIAMETER_INCHES
TEMP_WARNING_THRESHOLD = 50  # Temperature threshold in Celsius
TEMP_CRITICAL_THRESHOLD = 55  # Critical overheating threshold

# Variables
selected_auton = None  # Stores the selected autonomous routine

# Helper Functions
# Helper Functions
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
        pid_output = max(min(pid_output, 75), -75)  # Lower max speed to reduce overshoot

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
    TURN_DURATION_MS = 400  # Adjust this based on your robot's turning behavior

    # Spin motors to turn left
    left_drive_1.spin(FORWARD, TURN_SPEED, PERCENT)
    left_drive_2.spin(FORWARD, TURN_SPEED, PERCENT)
    left_drive_3.spin(FORWARD, TURN_SPEED, PERCENT)
    right_drive_1.spin(REVERSE, TURN_SPEED, PERCENT)
    right_drive_2.spin(REVERSE, TURN_SPEED, PERCENT)
    right_drive_3.spin(REVERSE, TURN_SPEED, PERCENT)

    # Turn for a specified duration
    sleep(TURN_DURATION_MS)

    # Stop all motors with a brake
    left_drive_1.stop(BRAKE)
    left_drive_2.stop(BRAKE)
    left_drive_3.stop(BRAKE)
    right_drive_1.stop(BRAKE)
    right_drive_2.stop(BRAKE)
    right_drive_3.stop(BRAKE)
    
def rotate_right():
    """
    Rotates the robot 90 degrees to the left using motor control.
    Assumes a differential drive system with equal speeds on left and right sides.
    """
    # Constants for rotation
    TURN_SPEED = 50  # Speed percentage for the turn
    TURN_DURATION_MS = 420  # Adjust this based on your robot's turning behavior

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


def select_autonomous():
    """
    Displays an improved autonomous selection screen on the Brain with options for red and blue, left and right.
    """
    brain.screen.clear_screen()
    brain.screen.set_fill_color(Color.BLACK)
    brain.screen.draw_rectangle(0, 0, 480, 240)  # Black background

    # Button dimensions and positions
    button_width = 240
    button_height = 150
    left_x = 20
    right_x = 240
    top_y = 20
    bottom_y = 140

    # Function to draw a button
    def draw_button(x, y, color, text):
        brain.screen.set_fill_color(color)
        brain.screen.draw_rectangle(x, y, button_width, button_height)
        brain.screen.set_pen_color(Color.WHITE)
        brain.screen.set_cursor(y // 20 + 1, x // 10 + 1)
        brain.screen.print(text)

    # Draw buttons
    draw_button(left_x, top_y, Color.RED, "RED LEFT")
    draw_button(right_x, top_y, Color.RED, "RED RIGHT")
    draw_button(left_x, bottom_y, Color.BLUE, "BLUE LEFT")
    draw_button(right_x, bottom_y, Color.BLUE, "BLUE RIGHT")

    while True:
        if brain.screen.pressing():
            x, y = brain.screen.x_position(), brain.screen.y_position()

            for button_x, button_y, color, mode in [
                (left_x, top_y, Color.RED, "red_left"),
                (right_x, top_y, Color.RED, "red_right"),
                (left_x, bottom_y, Color.BLUE, "blue_left"),
                (right_x, bottom_y, Color.BLUE, "blue_right")
            ]:
                if button_x <= x <= button_x + button_width and button_y <= y <= button_y + button_height:
                    brain.screen.clear_screen()
                    brain.screen.set_fill_color(color)
                    brain.screen.draw_rectangle(0, 0, 480, 240)
                    brain.screen.set_pen_color(Color.WHITE)
                    brain.screen.set_cursor(5, 3)
                    return mode

def display_motor_temperatures():
    """
    Continuously displays motor temperatures on the brain screen.
    """
    while True:
        brain.screen.clear_screen()
        brain.screen.set_cursor(1, 1)
        brain.screen.print("Motor Temperatures:")

        temperatures = [
            left_drive_1.temperature('celsius'),
            left_drive_2.temperature('celsius'),
            right_drive_1.temperature('celsius'),
            right_drive_2.temperature('celsius'),
        ]

        # Check for warnings
        if any(temp >= TEMP_WARNING_THRESHOLD for temp in temperatures):
            controller.screen.clear_screen()
            controller.screen.set_cursor(1, 1)
            controller.screen.print("WARNING: MOTOR HOT!")

        sleep(500)

# Autonomous routines
def red_left_negative_corner():
    piston1.open()
    pid_drive(32.5)
    piston1.close()
    pid_drive(-6)
    conveyor_motor1.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
    sleep(200)
    conveyor_motor1.stop()
    pid_drive(-30)

def red_right_positive_corner():
    piston1.open()
    pid_drive(32)
    piston1.close()
    pid_drive(-6)
    conveyor_motor1.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
    sleep(200)
    conveyor_motor1.stop()
    pid_drive(-30)

# Autonomous entry point
def autonomous():
    if selected_auton == "red_left":
        red_left_negative_corner()
    elif selected_auton == "red_right":
        red_right_positive_corner()

# User Control Task
def drive_task():
    while True:
        forward = controller.axis3.position()
        turn = controller.axis4.position()

        left_speed = forward + turn
        right_speed = forward - turn

        left_drive_1.spin(REVERSE, left_speed, PERCENT)
        left_drive_2.spin(REVERSE, left_speed, PERCENT)
        right_drive_1.spin(REVERSE, right_speed, PERCENT)
        right_drive_2.spin(REVERSE, right_speed, PERCENT)

        # Conveyor control
        conveyor_speed = controller.axis2.position()
        if conveyor_speed != 0:
            conveyor_motor1.spin(FORWARD, conveyor_speed, PERCENT)
        else:
            conveyor_motor1.stop()

        # Pneumatic control
        if controller.buttonL1.pressing():
            piston1.close()
        elif controller.buttonR1.pressing():
            piston1.open()

        sleep(10)

# Main program
selected_auton = select_autonomous()
competition = Competition(drive_task, autonomous)
