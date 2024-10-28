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

# Brain should be defined by default
brain = Brain()

controller = Controller()

left_drive_1 = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
left_drive_2 = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
right_drive_1 = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
right_drive_2 = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)
conveyor_motor = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)

# Pneumatic piston connected to three-wire port A
piston = DigitalOut(brain.three_wire_port.a)

# Conveyor belt speed
CONVEYOR_SPEED = 95

# PID constants
Kp, Ki, Kd = 1.0, 0.1, 0
# Integral for PID control
integral = 0
previous_error = 0

# PID drive function to calculate motor speeds
def calculate_pid(target, current_position):
    global integral, previous_error
    # Calculate the error
    error = target - current_position
    # Proportional term
    P = Kp * error
    
    # Integral term
    integral += error
    I = Ki * integral

    # Derivative term
    D = Kd * (error - previous_error)

    # Update previous error
    previous_error = error
    
    # Calculate final motor speed by getting the sum of the proportional intergral and derivative term
    speed = P + I + D
    return speed

def drive_task():
    target_position = 0

    while True:
        # Get current position
        current_position = left_drive_1.position(DEGREES)
        
        # Calculate speed based on PID control
        forward_speed = calculate_pid(target_position, current_position)
        
        # Arcade control
        turn = -controller.axis1.position()  # Left stick horizontal

        # Calculate left and right motor speeds
        left_speed = forward_speed + turn
        right_speed = forward_speed - turn

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
            piston.set(True)  # Extend piston
        elif controller.buttonR1.pressing():
            piston.set(False)  # Retract piston

        # Delay to prevent excessive CPU usage
        sleep(10)

# Autonomous routine to move forward, turn left, and activate conveyor

def autonomous():
    # Move forward at medium speed
    left_speed = 50
    right_speed = 50
    left_drive_1.spin(FORWARD, left_speed, PERCENT)
    left_drive_2.spin(FORWARD, left_speed, PERCENT)
    right_drive_1.spin(FORWARD, right_speed, PERCENT)
    right_drive_2.spin(FORWARD, right_speed, PERCENT)
    
    # Run for 2 seconds
    sleep(2000)
    
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
    
    # Run both for 2 seconds
    sleep(2000)
    
    # Stop all motors
    left_drive_1.stop()
    left_drive_2.stop()
    right_drive_1.stop()
    right_drive_2.stop()
    conveyor_motor.stop()

autonomous()

# Run the drive code
drive = Thread(drive_task)

# Python now drops into REPL
