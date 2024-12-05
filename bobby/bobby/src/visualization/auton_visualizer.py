import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle, Circle
import matplotlib.image as mpimg
import os
from matplotlib.widgets import Button

class AutonVisualizer:
    def __init__(self, field_size=(144, 144)):  # Field size in inches
        self.field_size = field_size
        self.robot_width = 14  # inches
        self.robot_length = 18  # inches
        
        # Setup plot
        self.fig, self.ax = plt.subplots(figsize=(12, 12))
        self.ax.set_xlim(0, field_size[0])
        self.ax.set_ylim(0, field_size[1])
        
        # Load and display field image
        script_dir = os.path.dirname(__file__)  # Get the directory where the script is located
        image_path = os.path.join(script_dir, 'TopView.png')
        try:
            self.field_img = mpimg.imread(image_path)
            self.ax.imshow(self.field_img, extent=[0, field_size[0], 0, field_size[1]], origin='lower')
        except FileNotFoundError:
            print(f"Warning: {image_path} not found. Using grid background.")
            self.ax.grid(True)
        
        # Robot state
        self.robot_x = field_size[0]/2
        self.robot_y = 20  # Starting position
        self.robot_angle = 0  # degrees
        
        # System states
        self.piston_state = "closed"
        self.conveyor_running = False
        
        # Path tracking
        self.path_x = [self.robot_x]
        self.path_y = [self.robot_y]
        self.events = []  # To track piston and conveyor events
        
        # Create robot patch
        self.robot_patch = Rectangle(
            (self.robot_x - self.robot_width/2, self.robot_y - self.robot_length/2),
            self.robot_width, self.robot_length,
            angle=self.robot_angle,
            facecolor='red',
            alpha=0.7
        )
        self.ax.add_patch(self.robot_patch)
        
        # Add direction indicator (front of robot)
        self.direction_indicator = Circle(
            (self.robot_x, self.robot_y + self.robot_length/4),
            radius=2,
            color='green'
        )
        self.ax.add_patch(self.direction_indicator)
        
        # Path line
        self.path_line, = self.ax.plot([], [], 'b-', linewidth=2, alpha=0.5)
        
        # Status text
        self.status_text = self.ax.text(5, field_size[1]-10, '', fontsize=10, color='white', bbox=dict(facecolor='black', alpha=0.7))
        
        # Add indicators for piston and conveyor outside the plot
        self.piston_indicator = self.ax.text(150, 160, 'Piston: Closed', fontsize=12, color='red')
        self.conveyor_indicator = self.ax.text(150, 150, 'Conveyor: Off', fontsize=12, color='blue')

        # Button for resetting the visualization
        self.reset_ax = plt.axes([0.7, 0.05, 0.1, 0.075])
        self.reset_button = Button(self.reset_ax, 'Reset')
        self.reset_button.on_clicked(self.reset_visualization)
        
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
        self.piston_indicator.set_text('Piston: Open')

    def piston_close(self):
        """Simulate closing the piston."""
        self.piston_state = "closed"
        print("Piston closed.")
        self.piston_indicator.set_text('Piston: Closed')

    def conveyor_start(self):
        """Simulate starting the conveyor."""
        self.conveyor_running = True
        print("Conveyor started.")
        self.conveyor_indicator.set_text('Conveyor: On')

    def conveyor_stop(self):
        """Simulate stopping the conveyor."""
        self.conveyor_running = False
        print("Conveyor stopped.")
        self.conveyor_indicator.set_text('Conveyor: Off')
        
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
        anim = FuncAnimation(
            self.fig, self.update_animation,
            frames=len(self.path_x),
            interval=5,  # Reduced interval for smoother animation
            blit=True
        )
        
        plt.title("Robot Autonomous Path Visualization")
        plt.xlabel("Field X (inches)")
        plt.ylabel("Field Y (inches)")
        plt.show()

    def reset_visualization(self, event):
        """Reset the visualization to the initial state."""
        self.set_start_position(self.field_size[0]/2, 20, 0)
        self.path_x = [self.robot_x]
        self.path_y = [self.robot_y]
        self.events = []
        self.piston_indicator.set_text('Piston: Closed')
        self.conveyor_indicator.set_text('Conveyor: Off')
        self.path_line.set_data([], [])
        plt.draw()

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
    
    # You can set custom starting position and orientation here
    # viz.set_start_position(x, y, angle)
    # x, y: position in inches from bottom-left corner
    # angle: degrees (0 = facing up, 90 = facing right, etc.)
    viz.set_start_position(72, 20, 0)
    
    # Run and visualize the autonomous routine
    viz.run_auton(match_auton)