import pygame
import random
import math

pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Hunter")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
PURPLE = (160, 32, 240)
GRAY = (128, 128, 128)

difficulty_multiplier = 1

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont(None, 72)
medium_font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 26)

def create_pixelated_surface(width, height):
    return pygame.Surface((width, height), pygame.SRCALPHA)

# ---------------- PLAYER ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self, skin="default"):
        super().__init__()
        self.skin = skin
        self.speed = 5
        self.normal_speed = 5
        self.lives = 5
        self.angle = 0
        self.shield_timer = 0
        self.update_image()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))

    def update_image(self):
        color = GOLD if self.skin == "gold" else GREEN
        base_image = self.create_pixelated_player(color)

        # ---- SHIELD BUBBLE ----
        if self.shield_timer > 0:
            bubble_surface = create_pixelated_surface(80, 80)
            pygame.draw.circle(bubble_surface, (0, 150, 255, 60), (40, 40), 38)
            pygame.draw.circle(bubble_surface, (0, 180, 255), (40, 40), 38, 3)
            bubble_surface.blit(base_image, base_image.get_rect(center=(40, 40)))
            self.image = bubble_surface
        else:
            self.image = base_image

        self.original_image = self.image.copy()

    def create_pixelated_player(self, color):
        surface = create_pixelated_surface(25, 25)
        pixels = [
            (1,0,1),(2,0,1),(3,0,1),
            (0,1,1),(1,1,1),(2,1,1),(3,1,1),(4,1,1),
            (0,2,1),(1,2,0),(2,2,0),(3,2,0),(4,2,1),
            (0,3,1),(1,3,1),(2,3,1),(3,3,1),(4,3,1),
            (1,4,1),(2,4,1),(3,4,1),
        ]
        for x,y,val in pixels:
            if val:
                pygame.draw.rect(surface,color,(x*5,y*5,5,5))
        return surface

    def update(self):
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed; moving=True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed; moving=True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed; moving=True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed; moving=True

        if moving: self.angle += 5
        else: self.angle = 0

        self.update_image()
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.clamp_ip(screen.get_rect())

        if self.shield_timer > 0:
            self.shield_timer -= 1

# ---------------- ENEMY ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type="normal"):
      super().__init__()
      self.enemy_type = enemy_type

      self.image = self.create_pixelated_enemy()
      self.rect = self.image.get_rect()

      self.rect.x = random.randint(0, SCREEN_WIDTH - 20)
      self.rect.y = random.randint(-100, -40)

      self.speed = random.randint(3, 6)
      self.wave_offset = random.uniform(0, 2 * math.pi)

    # Kamikaze
      if enemy_type == "kamikaze":
          self.speed = 4

    # Shooter
      if enemy_type == "shooter":
          self.rect.y = 80
          self.speed = 3
          self.shoot_timer = 0
      # Purple enemy (faster normal)
      if enemy_type == "fast_purple":
        self.speed = random.randint(5, 8)  # slightly faster than normal


    def create_pixelated_enemy(self):
        surface = create_pixelated_surface(20, 20)
        pixels = [
            (1,0,1),(2,0,1),(3,0,1),
            (0,1,1),(1,1,1),(2,1,1),(3,1,1),(4,1,1),
            (0,2,1),(1,2,0),(2,2,0),(3,2,0),(4,2,1),
            (0,3,1),(1,3,1),(2,3,1),(3,3,1),(4,3,1),
            (1,4,1),(2,4,1),(3,4,1),
        ]
        if self.enemy_type == "kamikaze":
          color = (255, 120, 0)
        elif self.enemy_type == "shooter":
          color = BLUE
        elif self.enemy_type == "fast_purple":
           color = PURPLE
        else:
          color = RED

        for x,y,val in pixels:
            if val:
                pygame.draw.rect(surface, color, (x*4,y*4,4,4))
        return surface

    def update(self):

    # NORMAL
      if self.enemy_type == "normal":
          self.rect.y += self.speed * difficulty_multiplier
          self.rect.x += math.sin(self.wave_offset + self.rect.y * 0.01) * 2

    # KAMIKAZE (homes toward player)
      elif self.enemy_type == "kamikaze":
          dx = player.rect.centerx - self.rect.centerx
          dy = player.rect.centery - self.rect.centery
          distance = math.hypot(dx, dy)

          if distance != 0:
              dx /= distance
              dy /= distance

          self.rect.x += dx * self.speed * difficulty_multiplier
          self.rect.y += dy * self.speed * difficulty_multiplier


    # SHOOTER (strafe + shoot)
      elif self.enemy_type == "shooter":
        self.rect.x += self.speed * difficulty_multiplier

        # bounce left/right
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.speed *= -1

        # shoot every 10 seconds
        self.shoot_timer += 1
        if self.shoot_timer >= FPS * 1:
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)
            self.shoot_timer = 0

      # NORMAL / FAST PURPLE
      elif self.enemy_type in ["normal", "fast_purple"]:
        self.rect.y += self.speed
        self.rect.x += math.sin(self.wave_offset + self.rect.y * 0.01) * 2


      if self.rect.top > SCREEN_HEIGHT:
        self.kill()


# ---------------- BULLET ----------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image=create_pixelated_surface(3,8)
        pygame.draw.rect(self.image,WHITE,(0,0,3,8))
        self.rect=self.image.get_rect(center=(x,y))
        self.speed=-20
        self.trail_timer=0

    def update(self):
        self.rect.y+=self.speed
        self.trail_timer+=1
        if self.trail_timer%5==0:
            trail=Particle(self.rect.centerx,self.rect.centery,WHITE,20)
            particles.add(trail)
            all_sprites.add(trail)
        if self.rect.bottom<0:
            self.kill()

# ---------------- ENEMY BULLET ----------------
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_pixelated_surface(4, 10)
        pygame.draw.rect(self.image, PURPLE, (0, 0, 4, 10))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# ---------------- PARTICLE ----------------
class Particle(pygame.sprite.Sprite):
    def __init__(self,x,y,color=BLUE,lifetime=30):
        super().__init__()
        self.image=create_pixelated_surface(2,2)
        pygame.draw.rect(self.image,color,(0,0,2,2))
        self.rect=self.image.get_rect(center=(x,y))
        self.lifetime=lifetime
        self.alpha=255

        self.vx = 0
        self.vy = 0


    def update(self):
      self.rect.x += self.vx
      self.rect.y += self.vy

      self.lifetime -= 1
      if self.lifetime <= 0:
          self.kill()
      else:
          self.alpha = max(0, self.alpha - 6)
          self.image.set_alpha(self.alpha)


# ---------------- SHOP (UI IMPROVED ONLY) ----------------
class Shop:
    def __init__(self):
        self.items = {
            "gold_skin": {"name":"Golden Skin","cost":50},
            "extra_life": {"name":"Extra Life","cost":20},
            "shield": {"name":"Temporary Shield (10s)","cost":10}
        }

        self.buttons=[]
        y=260
        for key in self.items:
            rect=pygame.Rect(SCREEN_WIDTH//2-240,y,480,90)
            self.buttons.append((rect,key))
            y+=120

    def draw(self,screen,score):
        screen.fill((12,12,25))

        panel = pygame.Rect(SCREEN_WIDTH//2-320,130,640,520)
        pygame.draw.rect(screen,(25,25,50),panel,border_radius=20)
        pygame.draw.rect(screen,(100,100,200),panel,4,border_radius=20)

        title = font.render("SPACE SHOP",True,GOLD)
        screen.blit(title,(SCREEN_WIDTH//2-title.get_width()//2,160))

        score_text = medium_font.render(f"Your Score: {score}",True,WHITE)
        screen.blit(score_text,(SCREEN_WIDTH//2-score_text.get_width()//2,220))

        mouse_pos = pygame.mouse.get_pos()

        for rect,key in self.buttons:
            item=self.items[key]

    # Extra Life disabled if already at max
            # ---- CONDITIONS ----
            # Extra Life disabled if already at max
            if key == "extra_life" and player.lives >= 5:
              affordable = False
              disabled = True
# Golden Skin disabled if already owned or not enough lives
            elif key == "gold_skin" and (player.skin == "gold" or player.lives < 5):
              affordable = False
              disabled = True
            else:
              affordable = score >= item["cost"]
              disabled = False



            hovering = rect.collidepoint(mouse_pos) and affordable


            base_color = (40,100,200) if affordable else (80,40,40)
            hover_color = (70,150,255) if affordable else (120,60,60)
            color = hover_color if hovering else base_color

            pygame.draw.rect(screen,color,rect,border_radius=15)
            pygame.draw.rect(screen,WHITE,rect,3,border_radius=15)

            # ICONS
            icon_x = rect.x + 40
            icon_y = rect.centery

            if key=="gold_skin":
                pygame.draw.circle(screen,GOLD,(icon_x,icon_y),20)
            elif key=="extra_life":
                pygame.draw.circle(screen,RED,(icon_x-8,icon_y-5),10)
                pygame.draw.circle(screen,RED,(icon_x+8,icon_y-5),10)
                pygame.draw.polygon(screen,RED,[(icon_x-18,icon_y-2),
                                                (icon_x+18,icon_y-2),
                                                (icon_x,icon_y+18)])
            elif key=="shield":
                pygame.draw.circle(screen,BLUE,(icon_x,icon_y),20,3)

            name_text = medium_font.render(item["name"],True,WHITE)
            screen.blit(name_text,(rect.x+90,rect.y+18))

            if disabled:
              if key == "extra_life":
                cost_text = small_font.render("MAX LIVES", True, GRAY)
              elif key == "gold_skin":
                if player.skin == "gold":
                  cost_text = small_font.render("ALREADY OWNED", True, GRAY)
                else:
                  cost_text = small_font.render("Requires 5 Lives", True, GRAY)
              else:
                cost_text = small_font.render("Unavailable", True, GRAY)

            else:
              cost_text = small_font.render(
                                            f"Cost: {item['cost']} pts",
                                            True,
                                            YELLOW if affordable else GRAY
                                            )



            screen.blit(cost_text,(rect.x+90,rect.y+50))

        hint = small_font.render("Press T to Close Shop",True,GRAY)
        screen.blit(hint,(SCREEN_WIDTH//2-hint.get_width()//2,610))

    def handle_click(self,pos,score,player):
      for rect,key in self.buttons:
          if rect.collidepoint(pos):
              item=self.items[key]

            # ---- GOLD SKIN ----
              if key == "gold_skin":
                if score >= item["cost"] and player.skin != "gold" and player.lives == 5:
                  score -= item["cost"]
                  player.skin = "gold"
                  player.update_image()


            # ---- EXTRA LIFE (MAX 5) ----
              elif key=="extra_life":
                if player.lives < 5 and score >= item["cost"]:
                  score -= item["cost"]
                  player.lives += 1


            # ---- SHIELD ----
              elif key=="shield":
                  if score >= item["cost"]:
                      score -= item["cost"]
                      player.shield_timer=FPS*10
                      player.update_image()

      return score

# ---------------- GAME RESET ----------------
def reset_game():
    global all_sprites,enemies,bullets,particles,enemy_bullets,player,score,enemy_timer,shoot_cooldown,kills

    all_sprites=pygame.sprite.Group()
    enemies=pygame.sprite.Group()
    bullets=pygame.sprite.Group()
    particles=pygame.sprite.Group()

    player=Player()
    all_sprites.add(player)

    score=0
    kills=0
    enemy_timer=0
    shoot_cooldown=0

    enemy_bullets = pygame.sprite.Group()

# ---------------- SETUP ----------------
stars=[(random.randint(0,SCREEN_WIDTH),
        random.randint(0,SCREEN_HEIGHT)) for _ in range(100)]

shop=Shop()
game_state="START"
reset_game()
FIRE_RATE=10

# ---------------- GAME LOOP ----------------
running=True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

        if game_state=="START":
            if event.type==pygame.KEYDOWN and event.key==pygame.K_RETURN:
                game_state="PLAYING"

        elif game_state=="PLAYING":
            if event.type==pygame.KEYDOWN and event.key==pygame.K_t:
                game_state="SHOP"

        elif game_state=="SHOP":
            if event.type==pygame.KEYDOWN and event.key==pygame.K_t:
                game_state="PLAYING"
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                score=shop.handle_click(event.pos,score,player)

        elif game_state in ["GAME_OVER","STATS"]:
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_r:
                    reset_game()
                    game_state="PLAYING"
                if event.key==pygame.K_s:
                    game_state="STATS"
                if event.key==pygame.K_m:
                    game_state="GAME_OVER"

    if game_state=="PLAYING":

        keys=pygame.key.get_pressed()
        mouse_buttons=pygame.mouse.get_pressed()

        # ----- DIFFICULTY SCALING -----
        if score >= 300:
          difficulty_multiplier = 4
        elif score >= 200:
          difficulty_multiplier = 3
        elif score >= 100:
          difficulty_multiplier = 2
        else:
          difficulty_multiplier = 1


        if shoot_cooldown>0:
            shoot_cooldown-=1

        if (keys[pygame.K_SPACE] or mouse_buttons[0]) and shoot_cooldown==0:
            bullet=Bullet(player.rect.centerx,player.rect.top)
            bullets.add(bullet)
            all_sprites.add(bullet)
            for _ in range(5):
                p=Particle(player.rect.centerx+random.randint(-10,10),
                           player.rect.top)
                particles.add(p)
                all_sprites.add(p)
            shoot_cooldown=FIRE_RATE

        enemy_timer+=1
        if enemy_timer >= 60:

          roll = random.random()

          if roll < 0.1:
            enemy = Enemy("kamikaze")
          elif roll < 0.15:
            enemy = Enemy("shooter")
          elif roll < 0.2:
            enemy = Enemy("fast_purple")
          else:
            enemy = Enemy("normal")

          enemies.add(enemy)
          all_sprites.add(enemy)
          enemy_timer = 0

        all_sprites.update()

        hits=pygame.sprite.groupcollide(enemies,bullets,True,True)
        for enemy_hit in hits:

            if enemy_hit.enemy_type == "kamikaze":
              score += 3
              color = (255, 120, 0)
            elif enemy_hit.enemy_type == "shooter":
              score += 5
              color = BLUE
            elif enemy_hit.enemy_type == "fast_purple":
              score += 2
              color = PURPLE
            else:
              score += 1
              color = RED

            kills += 1


            for _ in range(10):
              explosion = Particle(
              enemy_hit.rect.centerx + random.randint(-20,20),
              enemy_hit.rect.centery + random.randint(-20,20),
              color,
              40
              )
              particles.add(explosion)
              all_sprites.add(explosion)

        collision_enemies = pygame.sprite.spritecollide(player,enemies,True)
        # Enemy bullet collision
        collision_enemy_bullets = pygame.sprite.spritecollide(player, enemy_bullets, True)

        for bullet in collision_enemy_bullets:
          if player.shield_timer == 0:
            player.lives -= 1


        for e in collision_enemies:
          if player.shield_timer == 0:

        # ---- BIG FIERY ORANGE PLAYER EXPLOSION ----
            for _ in range(60):
              angle = random.uniform(0, 2 * math.pi)
              speed = random.uniform(2, 8)

              explosion = Particle(
                player.rect.centerx,
                player.rect.centery,
                random.choice([(255,140,0), (255,100,0), (255,200,0)]),
                60
              )

    # Add outward movement
              explosion.vx = math.cos(angle) * speed
              explosion.vy = math.sin(angle) * speed

              particles.add(explosion)
              all_sprites.add(explosion)

# Shockwave ring
              pygame.draw.circle(screen, (255,120,0), player.rect.center, 60, 4)

            player.lives -=1
        if player.lives<=0:
            game_state="GAME_OVER"


    screen.fill(BLACK)
    for star in stars:
        pygame.draw.circle(screen,WHITE,star,1)

    if game_state=="START":
        glow = abs(math.sin(pygame.time.get_ticks()*0.003))*255
        title = font.render("SPACE HUNTER",True,(255,int(glow),0))
        screen.blit(title,(SCREEN_WIDTH//2-title.get_width()//2,200))

        pygame.draw.rect(screen,(40,40,80),(SCREEN_WIDTH//2-250,330,500,150),border_radius=20)
        screen.blit(medium_font.render("Press ENTER to Start",True,WHITE),(SCREEN_WIDTH//2-150,360))
        screen.blit(small_font.render("Move: Arrow Keys / WASD",True,GRAY),(SCREEN_WIDTH//2-120,405))
        screen.blit(small_font.render("Shoot: SPACE or Mouse",True,GRAY),(SCREEN_WIDTH//2-110,435))

        # Add "Made by Sourish" at the bottom
        made_by_text = small_font.render("Made by Sourish", True, GRAY)
        screen.blit(made_by_text, (SCREEN_WIDTH//2 - made_by_text.get_width()//2, SCREEN_HEIGHT - 40))


    elif game_state=="PLAYING":
      all_sprites.draw(screen)

    # ---- HEART LIVES DISPLAY (CENTERED, MAX 5) ----
      max_hearts = min(player.lives, 5)
      spacing = 45
      total_width = max_hearts * spacing
      start_x = SCREEN_WIDTH // 2 - total_width // 2

      for i in range(max_hearts):
        x = start_x + i * spacing
        y = 30

    # Dark red hardcore heart
        hardcore_red = (200, 0, 0)
        pygame.draw.circle(screen, hardcore_red, (x-8, y-5), 10)
        pygame.draw.circle(screen, hardcore_red, (x+8, y-5), 10)
        pygame.draw.polygon(screen, hardcore_red, [
        (x-18, y-2),
        (x+18, y-2),
        (x, y+18)
        ])

      # Kamikaze vs Other Enemies Collision
      kamikazes = [e for e in enemies if e.enemy_type == "kamikaze"]
      for kamikaze in kamikazes:
        collided = pygame.sprite.spritecollide(kamikaze, enemies, False)
        for other in collided:
          if other != kamikaze:
            # Explosion but NO points
            for _ in range(10):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 6)
                explosion = Particle(
                    kamikaze.rect.centerx + math.cos(angle) * speed * 2,
                    kamikaze.rect.centery + math.sin(angle) * speed * 2,
                    (255, 120, 0),
                    30
                )
                particles.add(explosion)
                all_sprites.add(explosion)
            kamikaze.kill()
            break  # Stop checking once exploded



    # Black outline (bigger heart behind)
        pygame.draw.circle(screen, (0,0,0), (x-9, y-6), 11)
        pygame.draw.circle(screen, (0,0,0), (x+9, y-6), 11)
        pygame.draw.polygon(screen, (0,0,0), [
          (x-19, y-3),
          (x+19, y-3),
          (x, y+20)
        ])

    # Dark red hardcore heart
        hardcore_red = (200, 0, 0)

        pygame.draw.circle(screen, hardcore_red, (x-8, y-5), 10)
        pygame.draw.circle(screen, hardcore_red, (x+8, y-5), 10)
        pygame.draw.polygon(screen, hardcore_red, [
          (x-18, y-2),
          (x+18, y-2),
          (x, y+18)
        ])


      screen.blit(medium_font.render(f"Score: {score}",True,WHITE),(10,10))
      screen.blit(small_font.render("Press T for Shop",True,WHITE),(SCREEN_WIDTH-170,10))


    elif game_state=="SHOP":
        shop.draw(screen,score)

    elif game_state=="GAME_OVER":
        glow = abs(math.sin(pygame.time.get_ticks()*0.004))*255
        title = font.render("GAME OVER",True,(255,0,int(glow)))
        screen.blit(title,(SCREEN_WIDTH//2-title.get_width()//2,200))

        pygame.draw.rect(screen,(50,20,20),(SCREEN_WIDTH//2-260,320,520,180),border_radius=20)
        screen.blit(medium_font.render(f"Final Score: {score}",True,WHITE),(SCREEN_WIDTH//2-120,350))
        screen.blit(small_font.render("Press R to Play Again",True,WHITE),(SCREEN_WIDTH//2-110,400))
        screen.blit(small_font.render("Press S for Stats Screen",True,WHITE),(SCREEN_WIDTH//2-120,430))

        # Add "Made by Sourish" at the bottom
        made_by_text = small_font.render("Made by Sourish", True, GRAY)
        screen.blit(made_by_text, (SCREEN_WIDTH//2 - made_by_text.get_width()//2, SCREEN_HEIGHT - 40))


    elif game_state=="STATS":
        pygame.draw.rect(screen,(20,20,60),(SCREEN_WIDTH//2-260,260,520,250),border_radius=20)
        screen.blit(font.render("STATS",True,BLUE),(SCREEN_WIDTH//2-90,200))
        screen.blit(medium_font.render(f"Final Score: {score}",True,WHITE),(SCREEN_WIDTH//2-120,300))
        screen.blit(medium_font.render(f"Enemies Destroyed: {kills}",True,WHITE),(SCREEN_WIDTH//2-160,340))
        screen.blit(small_font.render("Press R to Play Again",True,WHITE),(SCREEN_WIDTH//2-110,390))
        screen.blit(small_font.render("Press M to Return",True,WHITE),(SCREEN_WIDTH//2-90,420))

        # Add "Made by Sourish" at the bottom
        made_by_text = small_font.render("Made by Sourish", True, GRAY)
        screen.blit(made_by_text, (SCREEN_WIDTH//2 - made_by_text.get_width()//2, SCREEN_HEIGHT - 40))


    pygame.display.flip()

pygame.quit()