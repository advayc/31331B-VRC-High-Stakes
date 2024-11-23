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

# drive motors
left_drive_1 = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
left_drive_2 = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
right_drive_1 = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
right_drive_2 = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)

# conveyor motor
conveyor_motor = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)

# pneumatic pistons
piston1 = Pneumatics(brain.three_wire_port.c)

# constants
CONVEYOR_SPEED = 100
KP = 0.5
KI = 0.01
KD = 0.1
WHEEL_DIAMETER_INCHES = 4.0
WHEEL_CIRCUMFERENCE_INCHES = math.pi * WHEEL_DIAMETER_INCHES

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

def autonomous():
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

def display_controls_summary():
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print("L1/R1 PISTON OPEN")
    controller.screen.set_cursor(2, 1)
    controller.screen.print("L2/R2 PISTON CLOSE")
    controller.screen.set_cursor(3, 1)
    controller.screen.print("R JOYSTICK")

def drive_task():
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
            conveyor_motor.spin(FORWARD, conveyor_speed, PERCENT)
        else:
            conveyor_motor.stop()

        if controller.buttonL1.pressing():
            piston1.close()
        if controller.buttonR1.pressing():
            piston1.close()
        elif controller.buttonR2.pressing():
            piston1.open()
        elif controller.buttonL2.pressing():
            piston1.open()

        sleep(10)

# competition setup
drive = Thread(drive_task)
competition = Competition(drive_task, autonomous)
