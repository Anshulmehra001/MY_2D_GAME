# assets/cheat.py
import pygame
import time
import sys

def run_cheat_check(screen, title_logo, fade_out_func):
    screen.blit(title_logo, (0, 0)); pygame.display.update()
    start_time = time.time()
    while time.time() - start_time < 2:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                key_map = {
                    pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4, pygame.K_5: 5,
                    pygame.K_6: 6, pygame.K_7: 7, pygame.K_8: 8, pygame.K_9: 9, pygame.K_0: 10
                }
                level_to_start = key_map.get(event.key)
                if level_to_start:
                    print(f"Cheat activated! Starting at Level {level_to_start}.")
                    fade_out_func(); return level_to_start
    return 0