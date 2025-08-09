# assets/level5.py
import pygame
import os
import random
import sys


def main(screen, clock):
    # --- Local Level Setup ---
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    FPS = 60
    FONT = pygame.font.SysFont("arial", 24, bold=True)
    BIG_FONT = pygame.font.SysFont("arial", 48, bold=True)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LEVEL5_DIR = os.path.join(BASE_DIR, "level5_assets")

    # --- Asset Loading ---
    def safe_load(path, target_size=None):
        try:
            image = pygame.image.load(path).convert_alpha()
            if target_size: image = pygame.transform.smoothscale(image, target_size)
            return image
        except pygame.error:
            print(f"[WARN] Missing {path}, using placeholder")
            surf = pygame.Surface(target_size or (100, 100), pygame.SRCALPHA);
            surf.fill((255, 0, 255));
            return surf

    bg_level5 = safe_load(os.path.join(LEVEL5_DIR, "bg_level5.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
    story_level5 = safe_load(os.path.join(LEVEL5_DIR, "story_level5.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
    story_level5_end = safe_load(os.path.join(LEVEL5_DIR, "story_level5_end.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
    dragon_attack_img = safe_load(os.path.join(LEVEL5_DIR, "dragon_attack.png"), (180, 130))
    dragon_fly_left = safe_load(os.path.join(LEVEL5_DIR, "flying_dragon_left.png"), (150, 120))
    dragon_fly_right = safe_load(os.path.join(LEVEL5_DIR, "flying_dragon_right.png"), (150, 120))
    fire_image = safe_load(os.path.join(LEVEL5_DIR, "fire_image.png"), (30, 30))
    nobita_idle = safe_load(os.path.join(BASE_DIR, "nobita_idle.png"), (70, 100))
    sword_slash = safe_load(os.path.join(BASE_DIR, "sword_slash.png"), (40, 40))

    # --- Sound Effects ---
    slash_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "slash.wav"))
    hit_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "hit.wav"))

    # --- Classes ---
    class Nobita(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.idle_image = nobita_idle
            self.attack_image = pygame.Surface(
                (nobita_idle.get_width() + sword_slash.get_width(), nobita_idle.get_height()), pygame.SRCALPHA)
            self.attack_image.blit(nobita_idle, (0, 0));
            self.attack_image.blit(sword_slash, (nobita_idle.get_width() - 10, 20))
            self.image = self.idle_image
            self.rect = self.image.get_rect(midbottom=(100, SCREEN_HEIGHT - 50))
            self.speed = 5;
            self.health = 100;
            self.attacking = False;
            self.attack_cooldown = 0
            self.hit_this_swing = False  # <-- BUG FIX: Add flag to prevent multiple hit sounds

        def update(self, keys):
            if not self.attacking:
                if keys[pygame.K_LEFT]: self.rect.x -= self.speed
                if keys[pygame.K_RIGHT]: self.rect.x += self.speed
                if keys[pygame.K_UP]: self.rect.y -= self.speed
                if keys[pygame.K_DOWN]: self.rect.y += self.speed
            self.rect.clamp_ip(screen.get_rect())
            if self.attacking:
                self.attack_cooldown -= 1
                if self.attack_cooldown <= 0: self.attacking = False; self.image = self.idle_image

        def attack(self):
            if not self.attacking:
                self.attacking = True;
                self.image = self.attack_image;
                self.attack_cooldown = 15
                self.hit_this_swing = False  # <-- BUG FIX: Reset flag on new attack
                slash_sound.play()

        def slash_rect(self):
            return pygame.Rect(self.rect.right, self.rect.top, 40, self.rect.height)

    class Fireball(pygame.sprite.Sprite):
        def __init__(self, x, y, direction):
            super().__init__();
            self.image = fire_image;
            self.rect = self.image.get_rect(center=(x, y));
            self.direction = direction;
            self.speed = 7;
            self.damage = 10

        def update(self):
            self.rect.x += self.speed * self.direction
            if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH: self.kill()

    class Dragon(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__();
            self.image = dragon_fly_left;
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2));
            self.health = 300
            self.speed_y = 2;
            self.direction_y = 1;
            self.direction = -1;
            self.attack_timer = 0;
            self.fireballs = pygame.sprite.Group()
            self.phase2 = False;
            self.flame_state = False;
            self.flame_timer = 0;
            self.flame_pause_timer = 0

        def update(self, nobita_rect):
            self.rect.y += self.speed_y * self.direction_y
            if self.rect.top <= 50 or self.rect.bottom >= SCREEN_HEIGHT - 50: self.direction_y *= -1
            if nobita_rect.centerx < self.rect.centerx:
                self.direction = -1; self.image = dragon_fly_left if not self.phase2 or not self.flame_state else self.image
            else:
                self.direction = 1; self.image = dragon_fly_right if not self.phase2 or not self.flame_state else self.image
            if self.health <= 150 and not self.phase2: self.phase2 = True; self.flame_state = True; self.flame_timer = 0; self.flame_pause_timer = 0
            if not self.phase2:
                if self.attack_timer <= 0:
                    self.fireballs.add(Fireball(self.rect.centerx, self.rect.centery,
                                                self.direction)); self.attack_timer = random.randint(40, 70)
                else:
                    self.attack_timer -= 1
            else:
                if abs(
                    self.rect.centerx - nobita_rect.centerx) > 150: self.rect.x += -2 if self.rect.centerx > nobita_rect.centerx else 2
                if self.flame_state:
                    self.image = dragon_attack_img;
                    self.flame_timer += 1
                    if self.flame_timer >= FPS * 5: self.flame_state = False; self.flame_pause_timer = 0; self.flame_timer = 0
                else:
                    self.flame_pause_timer += 1
                    if self.flame_pause_timer >= FPS * 3: self.flame_state = True; self.flame_pause_timer = 0
            self.fireballs.update()

        def flame_hitbox(self):
            if self.direction == -1:
                return pygame.Rect(self.rect.left - 60, self.rect.top + 30, 60, 40)
            else:
                return pygame.Rect(self.rect.right, self.rect.top + 30, 60, 40)

    def draw_health_bars(nobita, dragon):
        pygame.draw.rect(screen, (255, 0, 0), (20, 20, nobita.health * 2, 20));
        pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20), 2)
        pygame.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH - 320, 20, int(300 * (dragon.health / 300)), 20));
        pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH - 320, 20, 300, 20), 2)

    def show_story(image, text):
        screen.blit(image, (0, 0));
        text_surface = FONT.render(text, True, (255, 255, 255));
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        pygame.draw.rect(screen, (0, 0, 0, 180), text_rect.inflate(20, 10));
        screen.blit(text_surface, text_rect);
        pygame.display.flip();
        pygame.time.wait(3500)

    def run_game_loop():
        nobita = Nobita();
        dragon = Dragon();
        all_sprites = pygame.sprite.Group(nobita, dragon)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: nobita.attack()
                    if event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"
            keys = pygame.key.get_pressed();
            nobita.update(keys);
            dragon.update(nobita.rect)

            for fireball in dragon.fireballs:
                if nobita.rect.colliderect(
                    fireball.rect): nobita.health -= fireball.damage; fireball.kill(); hit_sound.play()
            if dragon.phase2 and dragon.flame_state and dragon.flame_hitbox().colliderect(nobita.rect):
                nobita.health -= 1
                # To prevent sound spam, we can play it less often for continuous damage
                if pygame.time.get_ticks() % 10 == 0: hit_sound.play()

            # --- HIT SOUND BUG FIX ---
            if nobita.attacking and nobita.slash_rect().colliderect(dragon.rect):
                dragon.health -= 2
                if not nobita.hit_this_swing:
                    hit_sound.play()
                    nobita.hit_this_swing = True

            if nobita.health <= 0: return "GAME_OVER"
            if dragon.health <= 0: return "VICTORY"
            screen.blit(bg_level5, (0, 0));
            all_sprites.draw(screen);
            dragon.fireballs.draw(screen);
            draw_health_bars(nobita, dragon);
            pygame.display.flip();
            clock.tick(FPS)

    show_story(story_level5, "Nobita and his friends enter the dragon’s lair...")
    while True:
        result = run_game_loop()
        if result == "QUIT_TO_MENU": return "QUIT_TO_MENU"
        if result == "VICTORY": show_story(story_level5_end,
                                           ""); return "COMPLETED"
        if result == "GAME_OVER":
            screen.fill((0, 0, 0));
            msg = BIG_FONT.render("Game Over", True, (255, 0, 0));
            screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)))
            prompt = FONT.render("Press 'R' to Restart or 'Esc' to Quit to Menu", True, (255, 255, 255));
            screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20)))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r: waiting = False
                        if event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"