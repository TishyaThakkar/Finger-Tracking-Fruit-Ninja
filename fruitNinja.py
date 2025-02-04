import random
import time

import cv2
import mediapipe as mp
import numpy as np
import pygame

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Load fruit image
fruit_img = pygame.image.load("fruit.png")  # Replace with actual fruit image path
fruit_img = pygame.transform.scale(fruit_img, (50, 50))

# Initialize OpenCV and MediaPipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

# Fruit properties
fruits = []
score = 0
class Fruit:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.randint(3, 7)
        self.active = True

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            global game_over
            game_over = True  # End game if a fruit falls
            self.active = False

    def draw(self):
        screen.blit(fruit_img, (self.x, self.y))

# Button properties
button_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 - 25, 100, 50)
restart_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 50, 100, 50)
quit_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 120, 100, 50)
button_pressed_time = None
started = False
game_over = False

# Game loop
running = True
while running:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(np.rot90(cv2.flip(frame, 1)))
    frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))
    screen.blit(frame_surface, (0, 0))
    
    results = hands.process(rgb_frame)
    finger_pos = None
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y = int(index_finger.x * WIDTH), int(index_finger.y * HEIGHT)
            finger_pos = (x, y)
            pygame.draw.circle(screen, (0, 255, 0), finger_pos, 10)  # Draw finger tracker
    
    if game_over:
        font = pygame.font.Font(None, 48)
        text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 100))
        
        pygame.draw.rect(screen, (255, 230, 150), restart_rect, border_radius=25)
        restart_text = font.render("Restart", True, (0, 0, 0))
        screen.blit(restart_text, (restart_rect.x + 10, restart_rect.y + 10))
        
        pygame.draw.rect(screen, (255, 100, 100), quit_rect, border_radius=25)
        quit_text = font.render("Quit", True, (0, 0, 0))
        screen.blit(quit_text, (quit_rect.x + 25, quit_rect.y + 10))
        
        if finger_pos:
            if restart_rect.collidepoint(finger_pos):
                started = False
                game_over = False
                fruits = []
                score = 0
            elif quit_rect.collidepoint(finger_pos):
                running = False
    
    elif not started:
        button_color = (255, 230, 150)  # Soft yellow color
        if finger_pos and button_rect.collidepoint(finger_pos):
            if button_pressed_time is None:
                button_pressed_time = time.time()
            elapsed_time = time.time() - button_pressed_time if button_pressed_time else 0
            darkening_factor = min(100, int(elapsed_time / 3 * 100))
            button_color = (255 - darkening_factor, 230 - darkening_factor, 150 - darkening_factor)
            if elapsed_time >= 3:
                started = True
                button_pressed_time = None
        else:
            button_pressed_time = None
        
        pygame.draw.rect(screen, button_color, button_rect, border_radius=25)
        font = pygame.font.Font(None, 36)
        text = font.render("Start", True, (0, 0, 0))
        screen.blit(text, (button_rect.x + 25, button_rect.y + 10))
    else:
        if random.randint(1, 50) == 1:  # Randomly spawn fruits
            fruits.append(Fruit(random.randint(50, WIDTH - 50), 0))
        
        for fruit in fruits:
            fruit.update()
            fruit.draw()
            if finger_pos and fruit.active:
                fx, fy = fruit.x + 25, fruit.y + 25
                if np.linalg.norm(np.array(finger_pos) - np.array([fx, fy])) < 30:
                    fruit.active = False  # Remove fruit if finger is near
                    score += 1  # Increase score
        
        fruits = [fruit for fruit in fruits if fruit.active]
        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
    
    pygame.display.update()
    clock.tick(30)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

cap.release()
cv2.destroyAllWindows()
pygame.quit()
