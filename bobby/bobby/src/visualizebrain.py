import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 480, 240
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("VEX Brain UI Simulation")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

# Button dimensions and positions
BUTTON_WIDTH = 240
BUTTON_HEIGHT = 150
LEFT_X = 20
RIGHT_X = 240
TOP_Y = 20
BOTTOM_Y = 140

# Font
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 32)

def draw_button(x, y, color, text):
    pygame.draw.rect(screen, color, (x, y, BUTTON_WIDTH, BUTTON_HEIGHT))
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x + BUTTON_WIDTH // 2, y + BUTTON_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

def draw_ui():
    screen.fill(BLACK)
    
    # Draw buttons
    draw_button(LEFT_X, TOP_Y, RED, "RED LEFT")
    draw_button(RIGHT_X, TOP_Y, RED, "RED RIGHT")
    draw_button(LEFT_X, BOTTOM_Y, BLUE, "BLUE LEFT")
    draw_button(RIGHT_X, BOTTOM_Y, BLUE, "BLUE RIGHT")
    
    # Draw title
    title_surface = title_font.render("Select Autonomous Mode", True, WHITE)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, 10))
    screen.blit(title_surface, title_rect)

def select_autonomous():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                for button_x, button_y, color, mode in [
                    (LEFT_X, TOP_Y, RED, "red_left"),
                    (RIGHT_X, TOP_Y, RED, "red_right"),
                    (LEFT_X, BOTTOM_Y, BLUE, "blue_left"),
                    (RIGHT_X, BOTTOM_Y, BLUE, "blue_right")
                ]:
                    if button_x <= x <= button_x + BUTTON_WIDTH and button_y <= y <= button_y + BUTTON_HEIGHT:
                        screen.fill(color)
                        text_surface = font.render(f"Selected: {mode}", True, WHITE)
                        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                        screen.blit(text_surface, text_rect)
                        pygame.display.flip()
                        pygame.time.wait(1000)  # Display for 1 second
                        return mode
        
        draw_ui()
        pygame.display.flip()

selected = select_autonomous()
print(f"Selected: {selected}")
pygame.quit()
