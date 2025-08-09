import pygame
import os
import random

# --- Basic Setup ---
pygame.init()
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(CURRENT_DIR, "level8_assets")

# Create the asset directory if it doesn't exist
if not os.path.exists(ASSET_DIR):
    os.makedirs(ASSET_DIR)

# --- Color Palette ---
DARK_GREY = (40, 42, 54)
MEDIUM_GREY = (68, 71, 90)
LIGHT_GREY = (90, 95, 120)
BROWN = (85, 60, 40)
DARK_BROWN = (65, 45, 30)
GOLEM_EYE = (255, 180, 50)
BAT_RED_EYE = (255, 50, 50)

# --- Helper Function to Save Surfaces ---
def save_sprite(surface, name):
    """Saves a pygame surface to a file in the asset directory."""
    path = os.path.join(ASSET_DIR, name)
    pygame.image.save(surface, path)
    print(f"Successfully created '{name}'")

# --- 1. Generate Cave Background (bg_level8.png) ---
def create_background(width, height):
    surface = pygame.Surface((width, height))
    surface.fill(DARK_GREY)
    # Add some stalactites/stalagmites for texture
    for _ in range(30):
        # Stalactites (from top)
        x = random.randint(0, width)
        h = random.randint(20, 100)
        w = random.randint(15, 40)
        pygame.draw.polygon(surface, MEDIUM_GREY, [(x, 0), (x - w // 2, h), (x + w // 2, h)])
        # Stalagmites (from bottom)
        x = random.randint(0, width)
        h = random.randint(20, 80)
        w = random.randint(20, 50)
        pygame.draw.polygon(surface, MEDIUM_GREY, [(x, height), (x - w // 2, height - h), (x + w // 2, height - h)])
    return surface

# --- 2. Generate Rocky Platform (platform.png) ---
def create_platform(width, height):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    # Main rock shape
    pygame.draw.rect(surface, BROWN, (0, 0, width, height), border_radius=5)
    # Add some cracks and details
    for _ in range(10):
        x1 = random.randint(5, width - 5)
        y1 = random.randint(5, height - 5)
        x2 = x1 + random.randint(-20, 20)
        y2 = y1 + random.randint(-10, 10)
        pygame.draw.line(surface, DARK_BROWN, (x1, y1), (x2, y2), 2)
    return surface

# --- 3. Generate Bat Sprites (bat_idle.png, bat_attack.png) ---
def create_bat(is_attacking):
    surface = pygame.Surface((60, 40), pygame.SRCALPHA)
    body_center = (30, 20)
    # Body
    pygame.draw.ellipse(surface, (30, 30, 30), (18, 12, 24, 16))
    if is_attacking:
        # Wings spread
        pygame.draw.polygon(surface, (50, 50, 50), [body_center, (5, 5), (15, 25)])
        pygame.draw.polygon(surface, (50, 50, 50), [body_center, (55, 5), (45, 25)])
        # Red eyes
        pygame.draw.circle(surface, BAT_RED_EYE, (25, 18), 2)
        pygame.draw.circle(surface, BAT_RED_EYE, (35, 18), 2)
    else:
        # Wings folded
        pygame.draw.polygon(surface, (50, 50, 50), [body_center, (10, 10), (18, 20)])
        pygame.draw.polygon(surface, (50, 50, 50), [body_center, (50, 10), (42, 20)])
    return surface

# --- 4. Generate Golem Boss (golem_idle.png, golem_attack.png) ---
def create_golem(is_attacking):
    surface = pygame.Surface((180, 220), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(surface, MEDIUM_GREY, (40, 80, 100, 120), border_radius=15)
    # Head
    pygame.draw.rect(surface, LIGHT_GREY, (55, 40, 70, 50), border_radius=10)
    # Eyes
    pygame.draw.circle(surface, GOLEM_EYE, (75, 65), 5)
    pygame.draw.circle(surface, GOLEM_EYE, (105, 65), 5)
    # Left Arm (from golem's perspective)
    pygame.draw.rect(surface, LIGHT_GREY, (5, 90, 35, 80), border_radius=10)

    if is_attacking:
        # Right arm raised for a smash
        pygame.draw.rect(surface, LIGHT_GREY, (140, 20, 35, 100), border_radius=10)
        # Brighter eyes
        pygame.draw.circle(surface, (255, 255, 150), (75, 65), 7)
        pygame.draw.circle(surface, (255, 255, 150), (105, 65), 7)
    else:
        # Right arm at rest
        pygame.draw.rect(surface, LIGHT_GREY, (140, 90, 35, 80), border_radius=10)
    return surface

# --- 5. Generate Rock Projectile (rock.png) ---
def create_rock(size):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    radius = size // 2 - 2
    points = []
    for i in range(10): # 10 points for a jagged look
        angle = (i / 10) * 2 * 3.14159
        r = radius + random.randint(-4, 4)
        x = center + r * pygame.math.Vector2(1, 0).rotate_rad(angle).x
        y = center + r * pygame.math.Vector2(1, 0).rotate_rad(angle).y
        points.append((x,y))
    pygame.draw.polygon(surface, LIGHT_GREY, points)
    pygame.draw.polygon(surface, DARK_GREY, points, 3) # Outline
    return surface

# --- Main Execution ---
if __name__ == "__main__":
    print("Generating assets for Level 8...")

    # Create and save all assets
    save_sprite(create_background(800, 480), "bg_level8.png")
    save_sprite(create_platform(150, 40), "platform.png")
    save_sprite(create_bat(is_attacking=False), "bat_idle.png")
    save_sprite(create_bat(is_attacking=True), "bat_attack.png")
    save_sprite(create_golem(is_attacking=False), "golem_idle.png")
    save_sprite(create_golem(is_attacking=True), "golem_attack.png")
    save_sprite(create_rock(40), "rock.png")

    print("-" * 30)
    print(f"All assets have been saved in the '{ASSET_DIR}' folder.")
    print("You can now run your main Level 8 game file.")
    pygame.quit()