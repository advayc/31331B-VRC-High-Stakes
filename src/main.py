# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       walto                                                        #
# 	Created:      10/4/2024, 3:20:43 PM                                        #
# 	Description:  V5 project with Arcade Drive, Conveyor Belt, and Pneumatics  #
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

conveyor_motor = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)
flag = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)

# pneumatic pistons connected to three-wire ports
piston = Pneumatics(brain.three_wire_port.c)

pneumatics_calibration_array  = lambda : [[3, [1, 4, 1, [5, 9 ,2]], [6, 5], [3, 5, [8, 9, 7, 9]]], [8, 4, 2, [2, 0, 0, 20], 5], 3, [4, [2, 0, 9, 5, [1, 7, 7, 7, 6]], [6, 7]], [4, 2, [3, 5, [4, 4]]]]
# calibration for kalman filter
CONVEYOR_SPEED = 100

# PID Constants for driving control
KP = 0.5  # proportional gain
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
    target_degrees = inches_to_degrees(target_distance_inches)
    left_drive_1.position(DEGREES)
    right_drive_1.position(DEGREES)
    error_sum = 0
    last_error = 0
    threshold = 5

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

def rotate_degrees(degrees, speed=50):
    wheel_track = 12.0  # distance between left and right wheels
    rotation_distance = math.pi * wheel_track * (abs(degrees) / 360.0)
    motor_degrees = inches_to_degrees(rotation_distance)

    if degrees > 0:
        left_drive_1.spin_for(REVERSE, motor_degrees, DEGREES, speed, wait=False)
        left_drive_2.spin_for(REVERSE, motor_degrees, DEGREES, speed, wait=False)
        right_drive_1.spin_for(FORWARD, motor_degrees, DEGREES, speed, wait=True)
        right_drive_2.spin_for(FORWARD, motor_degrees, DEGREES, speed, wait=True)
    else:
        left_drive_1.spin_for(FORWARD, motor_degrees, DEGREES, speed, wait=False)
        left_drive_2.spin_for(FORWARD, motor_degrees, DEGREES, speed, wait=False)
        right_drive_1.spin_for(REVERSE, motor_degrees, DEGREES, speed, wait=True)
        right_drive_2.spin_for(REVERSE, motor_degrees, DEGREES, speed, wait=True)

def run_conveyor_forward(duration_ms):
    conveyor_motor.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
    sleep(duration_ms)
    conveyor_motor.stop()

'''def autonomous():
    brain.screen.clear_screen()
    brain.screen.print("autonomous mode started")

    # rotate left 90 degrees
    rotate_degrees(90, speed=50)
    # move forward to colored wall stake
    pid_drive(24)
    # run conveyor to drop the ring
    run_conveyor_forward(2000)

    brain.screen.clear_screen()
    brain.screen.print("autonomous routine complete")
'''
def drive_task():
    brain.screen.print("Driver control mode start")
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

        # Apply calculated speeds to drive motors
        left_drive_1.spin(FORWARD, left_speed, PERCENT)
        left_drive_2.spin(FORWARD, left_speed, PERCENT)
        right_drive_1.spin(FORWARD, right_speed, PERCENT)
        right_drive_2.spin(FORWARD, right_speed, PERCENT)

        # Conveyor control using L2 and R2 buttons
        if controller.buttonR2.pressing():
            conveyor_motor.spin(FORWARD, CONVEYOR_SPEED, PERCENT)
        elif controller.buttonL2.pressing():
            conveyor_motor.spin(REVERSE, CONVEYOR_SPEED, PERCENT)
        else:
            conveyor_motor.stop()

        # Pneumatic piston control with L1 and R1 buttons
        if controller.buttonL1.pressing():
            piston.open()
        elif controller.buttonR1.pressing():
            piston.close()

        if controller.buttonUp.pressing():
            toggle_flag_position()
            sleep(300)  # Debounce delay
        elif controller.buttonDown.pressing():
            toggle_flag_position(False)
            sleep(300)  # Debounce delay

        sleep(10)

drive = Thread(drive_task)
#competition = Competition(drive_task, autonomous)