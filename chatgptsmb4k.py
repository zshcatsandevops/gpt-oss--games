#!/usr/bin/env python3
# program.py – 600×400 NES‑style Super Mario Bros. (1‑1) in Pygame
# -------------------------------------------------------------
import sys, math
import pygame
from pygame.locals import *

# -------------------------------------------------------------
# CONFIGURATION
WIDTH, HEIGHT = 600, 400          # window size
FPS = 60                          # frames per second
GRAVITY = 0.6                     # gravity acceleration (pixels / frame²)
PLAYER_SPEED = 3                  # horizontal speed
JUMP_STRENGTH = 12                # initial jump velocity (negative)
TILE_SIZE = 32                    # each tile is 32×32 pixels

# -------------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Super Mario Bros. 1‑1 (Pygame)")

# -------------------------------------------------------------
# COLORS
SKY   = (135, 206, 235)
WHITE = (255, 255, 255)

# -------------------------------------------------------------
# PLACEHOLDER IMAGES
def placeholder(color):
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    surf.fill(color)
    return surf

mario_img   = placeholder((255, 0, 0))      # red square – Mario
block_img   = placeholder((139,69,19))     # brown block
pipe_top    = placeholder((0, 255, 0))      # green pipe top
pipe_body   = placeholder((34,139,34))     # dark green pipe body
coin_img    = placeholder((255, 215,0))    # gold coin
goomba_img  = placeholder((0,0,0))         # black square – Goomba

# -------------------------------------------------------------
# LEVEL MAP (1‑1 simplified)
level_map = [
"################################################################################",
"#                                                                                  #",
"#            $                 $                                                   #",
"#         #######    ######     ##                                                  #",
"#          ###      ##  ##   $   ##                                                  #",
"#         ######    #######     ##                                                  #",
"#          ###      ##  ##            $                                            #",
"#         ######    #######            ##                                            #",
"#          ###      ##  ##   $         ##                                            #",
"#   P                                                                G            #",
"################################################################################"
]

# -------------------------------------------------------------
class Camera:
    """Simple horizontal camera that follows the player."""
    def __init__(self, width):
        self.offset_x = 0
        self.width = width

    def apply(self, rect):
        return rect.move(-self.offset_x, 0)

    def update(self, target_rect):
        self.offset_x = max(0, target_rect.centerx - WIDTH // 2)
        level_width = len(level_map[0]) * TILE_SIZE
        max_offset = max(0, level_width - WIDTH)
        self.offset_x = min(self.offset_x, max_offset)

# -------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = mario_img
        self.rect = self.image.get_rect(topleft=pos)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def update(self, tiles):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[K_RIGHT]:
            self.vel_x = PLAYER_SPEED

        # Jump
        if keys[K_SPACE] and self.on_ground:
            self.vel_y = -JUMP_STRENGTH
            self.on_ground = False

        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10

        # Horizontal movement + collision
        self.rect.x += self.vel_x
        hit_list = pygame.sprite.spritecollide(self, tiles, False)
        for tile in hit_list:
            if self.vel_x > 0:   # moving right
                self.rect.right = tile.rect.left
            elif self.vel_x < 0: # moving left
                self.rect.left = tile.rect.right

        # Vertical movement + collision
        self.rect.y += self.vel_y
        hit_list = pygame.sprite.spritecollide(self, tiles, False)
        for tile in hit_list:
            if self.vel_y > 0:   # falling
                self.rect.bottom = tile.rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0: # jumping up
                self.rect.top = tile.rect.bottom
                self.vel_y = 0

# -------------------------------------------------------------
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect(topleft=pos)

class Goomba(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = goomba_img
        self.rect = self.image.get_rect(topleft=pos)
        self.vel_x = -1

    def update(self, tiles):
        self.rect.x += self.vel_x
        if pygame.sprite.spritecollideany(self, tiles):
            self.vel_x *= -1

# -------------------------------------------------------------
def create_level():
    """Parse level_map and return sprite groups + player."""
    tiles  = pygame.sprite.Group()
    coins  = pygame.sprite.Group()
    goombas= pygame.sprite.Group()

    for y, row in enumerate(level_map):
        for x, ch in enumerate(row):
            pos = (x * TILE_SIZE, y * TILE_SIZE)
            if ch == '#':
                tiles.add(Tile(pos, block_img))
            elif ch == 'P':          # player start
                global player
                player = Player(pos)
            elif ch == '$':          # coin
                coins.add(Coin((pos[0]+8, pos[1]-16)))
            elif ch == 'G':          # goomba
                goombas.add(Goomba(pos))
            elif ch == 'p':          # pipe top (rendered as block)
                tiles.add(Tile(pos, pipe_top))
            elif ch == 'b':          # pipe body (rendered as block)
                tiles.add(Tile(pos, pipe_body))

    return player, tiles, coins, goombas

player, tiles, coins, goombas = create_level()
camera = Camera(WIDTH)

# -------------------------------------------------------------
def draw_hud():
    font = pygame.font.SysFont(None, 24)
    score_text = f"Score: {len(coins)}"
    text_surf = font.render(score_text, True, WHITE)
    screen.blit(text_surf, (10, 10))

# -------------------------------------------------------------
def main():
    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Update
        player.update(tiles)
        goombas.update(tiles)

        # Coin collection
        collected = pygame.sprite.spritecollide(player, coins, True)
        if collected:
            print(f"Collected {len(collected)} coin(s)!")

        # Enemy collision
        if pygame.sprite.spritecollideany(player, goombas):
            print("Hit by Goomba! Game over.")
            pygame.quit()
            sys.exit()

        # Camera
        camera.update(player.rect)

        # Draw
        screen.fill(SKY)
        for sprite in tiles:
            screen.blit(sprite.image, camera.apply(sprite.rect))
        for coin in coins:
            screen.blit(coin.image, camera.apply(coin.rect))
        for goomba in goombas:
            screen.blit(goomba.image, camera.apply(goomba.rect))
        screen.blit(player.image, camera.apply(player.rect))

        draw_hud()
        pygame.display.flip()

# -------------------------------------------------------------
if __name__ == "__main__":
    main()
