import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle, Circle
import matplotlib.image as mpimg
import os
from matplotlib.widgets import Button, TextBox

class AutonVisualizer:
    def __init__(self, field_size=(144, 144)):  # Field size in inches
        self.field_size = field_size
        self.robot_width = 14  # inches
        self.robot_length = 18  # inches
        
        # Setup plot with smaller size
        self.fig, self.ax = plt.subplots(figsize=(8, 6))  # Smaller figure size
        self.ax.set_xlim(0, field_size[0])
        self.ax.set_ylim(0, field_size[1])
        
        # Load and display field image
        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, 'TopView.png')
        try:
            self.field_img = mpimg.imread(image_path)
            self.ax.imshow(self.field_img, extent=[0, field_size[0], 0, field_size[1]], origin='lower')
        except FileNotFoundError:
            print(f"Warning: {image_path} not found. Using grid background.")
            self.ax.grid(True)
        
        # Initialize robot state and path tracking
        self.robot_x = field_size[0]/2
        self.robot_y = 20
        self.robot_angle = 0
        self.path_x = [self.robot_x]
        self.path_y = [self.robot_y]
        self.events = []
        
        # Initialize system states
        self.piston_state = "closed"
        self.conveyor_running = False
        
        # Create robot and direction indicator
        self.robot_patch = Rectangle((self.robot_x - self.robot_width/2, self.robot_y - self.robot_length/2),
                                     self.robot_width, self.robot_length, angle=self.robot_angle, facecolor='red', alpha=0.7)
        self.ax.add_patch(self.robot_patch)
        self.direction_indicator = Circle((self.robot_x, self.robot_y + self.robot_length/4), radius=2, color='green')
        self.ax.add_patch(self.direction_indicator)
        
        # Path line and status text
        self.path_line, = self.ax.plot([], [], 'b-', linewidth=2, alpha=0.5)
        self.status_text = self.ax.text(5, field_size[1]-10, '', fontsize=10, color='white', bbox=dict(facecolor='black', alpha=0.7))
        
        # Setup buttons and textboxes
        self.setup_buttons()
        self.setup_textboxes()

    def setup_buttons(self):
        # Button positions and functionality
        self.reset_ax = plt.axes([0.75, 0.9, 0.1, 0.05])  # Moved up and to the right
        self.reset_button = Button(self.reset_ax, 'Reset')
        self.reset_button.on_clicked(self.reset_visualization)

        self.start_ax = plt.axes([0.64, 0.9, 0.1, 0.05])  # Moved up and to the right
        self.start_button = Button(self.start_ax, 'Start')
        self.start_button.on_clicked(self.start_animation)

        self.stop_ax = plt.axes([0.53, 0.9, 0.1, 0.05])  # Moved up and to the right
        self.stop_button = Button(self.stop_ax, 'Stop')
        self.stop_button.on_clicked(self.stop_animation)

    def setup_textboxes(self):
        # Textboxes for inputting starting position and angle
        self.x_textbox_ax = plt.axes([0.1, 0.9, 0.1, 0.05])  # Moved up
        self.x_textbox = TextBox(self.x_textbox_ax, 'X', initial=str(self.robot_x))
        self.x_textbox.on_submit(self.update_start_x)

        self.y_textbox_ax = plt.axes([0.21, 0.9, 0.1, 0.05])  # Moved up
        self.y_textbox = TextBox(self.y_textbox_ax, 'Y', initial=str(self.robot_y))
        self.y_textbox.on_submit(self.update_start_y)

        self.angle_textbox_ax = plt.axes([0.32, 0.9, 0.1, 0.05])  # Moved up
        self.angle_textbox = TextBox(self.angle_textbox_ax, 'Angle', initial=str(self.robot_angle))
        self.angle_textbox.on_submit(self.update_start_angle)

    def update_start_x(self, text):
        try:
            self.robot_x = float(text)
        except ValueError:
            print("Invalid input for X position.")

    def update_start_y(self, text):
        try:
            self.robot_y = float(text)
        except ValueError:
            print("Invalid input for Y position.")

    def update_start_angle(self, text):
        try:
            self.robot_angle = float(text)
        except ValueError:
            print("Invalid input for angle.")

    def start_animation(self, event):
        self.reset_visualization(None)  # Reset visualization with new start position
        self.run_auton(match_auton)

    def stop_animation(self, event):
        if hasattr(self, 'anim'):
            self.anim.event_source.stop()

    def reset_visualization(self, event):
        self.set_start_position(self.robot_x, self.robot_y, self.robot_angle)
        self.path_x = [self.robot_x]
        self.path_y = [self.robot_y]
        self.events = []
        self.path_line.set_data([], [])
        plt.draw()

    def set_start_position(self, x, y, angle=0):
        """Set the starting position and angle of the robot"""
        self.robot_x = x
        self.robot_y = y
        self.robot_angle = angle
        self.path_x = [x]
        self.path_y = [y]
        self.events = []
        
    def move_robot(self, distance):
        """Move robot forward/backward by distance (inches)"""
        angle_rad = math.radians(self.robot_angle)
        steps = np.linspace(0, distance, 100)  # Increased steps for smoother animation
        
        start_x = self.robot_x
        start_y = self.robot_y
        
        for step in steps:
            dx = step * math.sin(angle_rad)
            dy = step * math.cos(angle_rad)
            
            self.robot_x = start_x + dx
            self.robot_y = start_y + dy
            self.path_x.append(self.robot_x)
            self.path_y.append(self.robot_y)
            self.events.append({
                'piston': self.piston_state,
                'conveyor': self.conveyor_running
            })
            
    def rotate_robot(self, angle_degrees):
        """Rotate robot by angle_degrees"""
        steps = np.linspace(0, angle_degrees, 50)  # Increased steps for smoother rotation
        start_angle = self.robot_angle
        
        for step in steps:
            self.robot_angle = (start_angle + step) % 360
            self.path_x.append(self.robot_x)
            self.path_y.append(self.robot_y)
            self.events.append({
                'piston': self.piston_state,
                'conveyor': self.conveyor_running
            })
    
    def piston_open(self):
        """Simulate opening the piston."""
        self.piston_state = "open"
        print("Piston opened.")

    def piston_close(self):
        """Simulate closing the piston."""
        self.piston_state = "closed"
        print("Piston closed.")

    def conveyor_start(self):
        """Simulate starting the conveyor."""
        self.conveyor_running = True
        print("Conveyor started.")

    def conveyor_stop(self):
        """Simulate stopping the conveyor."""
        self.conveyor_running = False
        print("Conveyor stopped.")
        
    def update_animation(self, frame):
        """Update function for animation"""
        if frame < len(self.path_x):
            # Update robot position
            x = self.path_x[frame]
            y = self.path_y[frame]
            
            # Update robot patch
            self.robot_patch.set_xy((x - self.robot_width/2, y - self.robot_length/2))
            self.robot_patch.angle = -self.robot_angle
            
            # Update direction indicator
            angle_rad = math.radians(self.robot_angle)
            indicator_x = x + (self.robot_length/4) * math.sin(angle_rad)
            indicator_y = y + (self.robot_length/4) * math.cos(angle_rad)
            self.direction_indicator.center = (indicator_x, indicator_y)
            
            # Update path
            self.path_line.set_data(self.path_x[:frame+1], self.path_y[:frame+1])
            
            # Update status text
            event = self.events[frame]
            status = f"Piston: {event['piston']}\nConveyor: {'ON' if event['conveyor'] else 'OFF'}"
            self.status_text.set_text(status)
            
        return self.robot_patch, self.direction_indicator, self.path_line, self.status_text
        
    def run_auton(self, routine_func):
        """Run an autonomous routine and animate it"""
        # Reset paths
        self.path_x = [self.robot_x]
        self.path_y = [self.robot_y]
        self.events = []
        
        # Run the autonomous routine
        routine_func(self)
        
        # Create animation
        self.anim = FuncAnimation(
            self.fig, self.update_animation,
            frames=len(self.path_x),
            interval=5,  # Reduced interval for smoother animation
            blit=True
        )
        
        plt.show()

def match_auton(robot):
    """Recreation of your autonomous routine"""
    robot.piston_open()
    robot.move_robot(32)
    robot.piston_close()
    robot.move_robot(-6)
    robot.conveyor_start()
    robot.move_robot(-5)
    robot.rotate_robot(90)
    robot.conveyor_stop()

if __name__ == "__main__":
    # Create visualizer
    viz = AutonVisualizer()
    viz.run_auton(match_auton)