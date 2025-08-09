# assets/level6.py
import pygame
import random
import os
import sys


def main(screen, clock):
    # --- Local Level Setup ---
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    FPS = 60
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS = os.path.join(BASE_DIR, "level6_assets")
    FONT_BIG = pygame.font.SysFont("lucidaconsole", 48, bold=True)
    FONT_SMALL = pygame.font.SysFont("lucidaconsole", 36, bold=True)
    WHITE, BLACK, GOLD, GREY, RED = (255, 255, 255), (0, 0, 0), (255, 215, 0), (100, 100, 100), (200, 0, 0)

    # --- Asset Loading ---
    try:
        bg = pygame.transform.scale(pygame.image.load(os.path.join(ASSETS, "bg_level6.png")).convert(),
                                    (SCREEN_WIDTH, SCREEN_HEIGHT))
        doraemon_img = pygame.transform.scale(pygame.image.load(os.path.join(ASSETS, "doraemon.png")).convert_alpha(),
                                              (90, 70))
        fire_img = pygame.transform.scale(pygame.image.load(os.path.join(ASSETS, "fire_circle.png")).convert_alpha(),
                                          (60, 60))
        bird_img = pygame.transform.scale(pygame.image.load(os.path.join(ASSETS, "flying_bird.png")).convert_alpha(),
                                          (70, 50))
    except Exception as e:
        print(f"Error loading level 6 assets: {e}");
        return "QUIT_TO_MENU"

    hit_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "hit.wav"))

    # --- Classes ---
    class Doraemon(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__();
            self.image = doraemon_img;
            self.rect = self.image.get_rect(center=(150, SCREEN_HEIGHT // 2));
            self.mask = pygame.mask.from_surface(self.image);
            self.speed = 5

        def update(self, keys):
            if keys[pygame.K_UP]: self.rect.y -= self.speed
            if keys[pygame.K_DOWN]: self.rect.y += self.speed
            self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    class Obstacle(pygame.sprite.Sprite):
        def __init__(self, kind):
            super().__init__();
            self.image = fire_img if kind == "fire" else bird_img;
            self.rect = self.image.get_rect(x=SCREEN_WIDTH + random.randint(100, 300),
                                            y=random.randint(50, SCREEN_HEIGHT - 100));
            self.mask = pygame.mask.from_surface(self.image);
            self.speed = 6

        def update(self):
            self.rect.x -= self.speed
            if self.rect.right < 0: self.kill()

    # --- Screen Functions (Handles both Victory and Game Over) ---
    def end_screen(is_victory):
        doraemon_x = -100
        doraemon_y = SCREEN_HEIGHT // 2

        # Define buttons
        button1_rect = pygame.Rect(SCREEN_WIDTH / 2 - 150, 280, 300, 60)
        button2_rect = pygame.Rect(SCREEN_WIDTH / 2 - 150, 360, 300, 60)

        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"
                    if not is_victory and event.key == pygame.K_r: return "RESTART"  # Keyboard shortcut for restart
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if button1_rect.collidepoint(mouse_pos):
                        return "NEXT_LEVEL" if is_victory else "RESTART"
                    if button2_rect.collidepoint(mouse_pos):
                        return "QUIT_TO_MENU"

            # Drawing
            if is_victory:
                screen.blit(bg, (0, 0))
                screen.blit(doraemon_img, (doraemon_x, doraemon_y))
                if doraemon_x < 150: doraemon_x += 3

                msg1 = FONT_BIG.render("Castle Reached!", True, GOLD)
                screen.blit(msg1, (SCREEN_WIDTH // 2 - msg1.get_width() // 2, 100))

                # Button 1: Next Level
                pygame.draw.rect(screen, GOLD if button1_rect.collidepoint(mouse_pos) else GREY, button1_rect,
                                 border_radius=15)
                btn1_text = FONT_SMALL.render("Next Level", True, (255, 255, 255));
                screen.blit(btn1_text, btn1_text.get_rect(center=button1_rect.center))
            else:  # Game Over
                screen.fill(BLACK)
                msg1 = FONT_BIG.render("Game Over!", True, RED)
                screen.blit(msg1, (SCREEN_WIDTH // 2 - msg1.get_width() // 2, 150))

                # Button 1: Restart
                pygame.draw.rect(screen, GOLD if button1_rect.collidepoint(mouse_pos) else GREY, button1_rect,
                                 border_radius=15)
                btn1_text = FONT_SMALL.render("Restart", True, (255, 255, 255));
                screen.blit(btn1_text, btn1_text.get_rect(center=button1_rect.center))

            # Button 2: Quit (for both screens)
            pygame.draw.rect(screen, RED if button2_rect.collidepoint(mouse_pos) else GREY, button2_rect,
                             border_radius=15)
            btn2_text = FONT_SMALL.render("Quit to Menu", True, (255, 255, 255));
            screen.blit(btn2_text, btn2_text.get_rect(center=button2_rect.center))

            pygame.display.flip()
            clock.tick(FPS)

    # --- Game Instance Loop (for a single attempt) ---
    def run_game_instance():
        all_sprites = pygame.sprite.Group();
        obstacles = pygame.sprite.Group()
        player = Doraemon();
        all_sprites.add(player)
        spawn_timer = 0;
        distance = 0;
        goal_distance = 5000;
        font = pygame.font.SysFont("Arial", 28)

        while True:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"

            spawn_timer += 1
            if spawn_timer > 50:
                obstacle = Obstacle(random.choice(["fire", "bird"]));
                all_sprites.add(obstacle);
                obstacles.add(obstacle);
                spawn_timer = 0

            player.update(keys);
            obstacles.update()
            if pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask):
                hit_sound.play();
                return "GAME_OVER"

            distance += 3
            if distance >= goal_distance: return "VICTORY"

            screen.blit(bg, (0, 0));
            all_sprites.draw(screen)  # STATIC BACKGROUND
            text = font.render(f"Distance: {distance}/{goal_distance}", True, (255, 255, 255));
            screen.blit(text, (10, 10))
            pygame.display.flip();
            clock.tick(FPS)

    # --- Level Start and Restart Loop ---
    while True:
        game_result = run_game_instance()

        if game_result == "QUIT_TO_MENU":
            return "QUIT_TO_MENU"

        elif game_result == "VICTORY":
            end_result = end_screen(is_victory=True)
            if end_result == "NEXT_LEVEL": return "COMPLETED"
            if end_result == "QUIT_TO_MENU": return "QUIT_TO_MENU"
            if end_result == "RESTART": continue

        elif game_result == "GAME_OVER":
            end_result = end_screen(is_victory=False)
            if end_result == "RESTART": continue
            if end_result == "QUIT_TO_MENU": return "QUIT_TO_MENU"