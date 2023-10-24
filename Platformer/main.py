import pygame
import random
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

###############------------const----------------#############
PLAYER = 0
ZOM = 1
COIN = 2
KUNAI = 3
RASENGAN = 4
BOSS = 5

PASS_LOCK_1 = random.randint(50, 100)

SCREEN_W = 810
SCREEN_H = 540
LEFT_LIMIT = 0
RIGHT_LIMIT = 4000
JUMP_FORCE = 20

point = 0
ammo = 0
lives = 50
shooting = False
boss_appeared = False
super_saiyan = False
boss_defeated = 0

running = False
game_start = True
game_over = False
stage = 0

keyboard = [False, False, False, False, False] #A, W, D, J, K, move, jump and fire
speed = [12, 10, 0, 18, 10, 5] # speed of player, zom

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
black = (0, 0, 0)

font = pygame.font.SysFont("Arial", 30)
font_menu = pygame.font.SysFont("Arial", 50)

#######################################

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()

class Entity:
    def __init__(self, name, x, y, str, moving, dir) -> None:
        self.sprites = []
        self.sprites_flip = []
        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        self.load_sprites(str)
        self.name = name #ZOM, PLAYER, COIN, ...

        #animation
        self.index = 0 #image at the moment

        self.direction = dir #false right
        self.on_ground = False
        self.moving = moving
        self.visible = False

        self.jumping = False
        self.max_jump = 5
        self.jump_step = 0
        self.already_jump = False

        self.dead = False
        self.lives = 3

        self.ground = 0 # the location of the platform which is currently stepped on
        pass
    
    def load_sprites(self, str):
        for i in str:
            self.sprites.append(pygame.image.load(i))
            self.sprites_flip.append(pygame.transform.flip(pygame.image.load(i), True, False))
        
        self.width = self.sprites[0].get_rect().w
        self.height = self.sprites[0].get_rect().h
        pass


    def move(self):
        
        if self.moving:
            self.index += 1
            if self.index == 4: self.index = 1
            if self.direction:
                if self.name == PLAYER: self.x = clamp(LEFT_LIMIT, self.x - speed[self.name], RIGHT_LIMIT)
                else: self.x = self.x - speed[self.name]
            else:
                if self.name == PLAYER: self.x = clamp(LEFT_LIMIT, self.x + speed[self.name], RIGHT_LIMIT)
                else: self.x = self.x + speed[self.name]
        else: self.index = 0
        
        #Jump
        if self.already_jump:
            self.index = 5
            if self.jumping and self.jump_step != self.max_jump:
                self.y -= JUMP_FORCE
                self.jump_step += 1

            if self.jump_step == self.max_jump:# jump to max height
                self.jumping = False

            if self.jump_step != 0 and self.jumping == False: # landing
                self.y += JUMP_FORCE
                self.jump_step -= 1

            if self.jump_step == 0:
                self.already_jump = False
                self.index = 0


    def draw(self, screen, camera):
        if not self.direction:
            screen.blit(self.sprites[self.index], (self.x - camera.x, self.y - camera.y))
        else: screen.blit(self.sprites_flip[self.index], (self.x - camera.x, self.y - camera.y))
    
    def delete(self):
        for k in self.sprites:
            k.quit()



class Obstacle:
    def __init__(self, file, name) -> None:
        self.image = pygame.image.load(file)
        self.x = 0
        self.y = 0
        self.width = self.image.get_rect().w
        self.height = self.image.get_rect().h
        self.name = name

        self.visible = False
        pass

    def draw(self, screen, camera):
        screen.blit(self.image, (self.x - camera.x, self.y - camera.y))

class Rectangle:
    def __init__(self, x, y, w, h, str, value, color) -> None:
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.value = value
        if str != "":
            self.image = pygame.image.load(str)
        else:
            self.image = pygame.Surface([w, h])
            self.image.fill(color)
        pass

    def setColor(self, color):
        self.image.fill(color)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.x - camera.x, self.y - camera.y))
        if self.value != "":
            self.text = font.render(str(self.value), True, white)
            screen.blit(self.text, (self.x + 15 - camera.x, self.y + 15 - camera.y))


class Camera:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        pass

    def follow(self, target):
        self.x = clamp(LEFT_LIMIT, target.x - SCREEN_W // 2, RIGHT_LIMIT - SCREEN_W)
        #self.y = target.y - SCREEN_H // 2
        pass

class SoundEffect:
    def __init__(self):
        self.mainTrack = pygame.mixer.music.load("music/enchanted.mp3")
        self.countDownSound = pygame.mixer.Sound('sounds/count.wav')
        self.hammerSound = pygame.mixer.Sound('sounds/hammering.wav')
        self.popSound = pygame.mixer.Sound("sounds/pop.wav")
        self.missSound = pygame.mixer.Sound("sounds/miss.wav")
        self.levelSound = pygame.mixer.Sound("sounds/point.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)

    def playCountDown(self):
        self.countDownSound.play()
        self.countDownSound.set_volume(0.2)

    def stopCountDown(self):
        self.countDownSound.stop()

    def playHammer(self):
        self.hammerSound.play()
        self.hammerSound.set_volume(0.2)

    def stopHammer(self):
        self.hammerSound.stop()

    def playPop(self):
        self.popSound.play()
        self.popSound.set_volume(0.2)

    def stopPop(self):
        self.popSound.stop()

    def playMiss(self):
        self.missSound.play()
        self.missSound.set_volume(0.2)

    def stopMiss(self):
        self.missSound.stop()

    def playLevelUp(self):
        self.levelSound.play()
        self.levelSound.set_volume(0.2)

    def stopLevelUp(self):
        self.levelSound.stop()

class Button(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, color, width, height, x, y, str):
       # Call the parent class (Sprite) constructor
       pygame.sprite.Sprite.__init__(self)

       # Create an image of the block, and fill it with a color.
       # This could also be an image loaded from the disk.
       self.image = pygame.Surface([width, height])
       self.image.fill(color)

       # Fetch the rectangle object that has the dimensions of the image
       # Update the position of this object by setting the values of rect.x and rect.y
       self.rect = self.image.get_rect()
       self.rect.x, self.rect.y = x, y
       self.x, self.y = x, y
       #self.num = num
       #self.limit_time = limit_time
       #self.count = 0
       self.name = str
       self.text = font_menu.render(str, True, white)
       #self.appeared = False

    def is_mouse_pressed(self) -> bool:
        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
        x = self.rect.x
        y = self.rect.y
        if x + self.rect.w > mouse_pos_x and x < mouse_pos_x and y + self.rect.h > mouse_pos_y and y < mouse_pos_y:
            return True
        else:
            return False

    def update(self, mode, num):
        match mode:
            case 0:
                self.zombie_incoming(num)
            case 1:
                self.is_mouse_pressed(red)
        if self.appeared and self.limit_time != -1:
            self.count += 1
            print(self.count)
            if self.count == self.limit_time:
                self.zombie_disappear()
                return
    
    def draw(self, screen, camera):
        screen.blit(self.image, (self.x - camera.x, self.y - camera.y))
        screen.blit(self.text, (self.x + 50 - camera.x, self.y - camera.y))

def clamp(left, x, right):
    if x < left: return left
    elif x > right: return right
    else: return x
    pass



camera = Camera()
str_player = [
"image\idle.png",
"image\walk1.png",
"image\walk2.png",
"image\walk3.png",
"image\walk4.png",
"image\jump.png"
]

player = Entity(PLAYER, 405, 270, str_player, False, False)
print(player.width, player.height)
brick = Rectangle(0, 315, 4000, 100, "", "", white)
lock = Rectangle(1500, 200, 50, 50, "", 0, blue)


background = [Rectangle(0, 0, 0, 0, "image/R.png", "", white), 
              Rectangle(1760, 0, 0, 0, "image/R.png", "", blue),
              Rectangle(1760 * 2, 0, 0, 0, "image/R.png", "", blue)]

i = 0
count = 0
coin = []
zombie = []
gun_shot = []
boss = []
book = []

#pygame.mixer.music.unload()
#pygame.mixer.music.load("music/enchanted.mp3")
#pygame.mixer.music.play(-1)
#pygame.mixer.music.set_volume(0.2)
sounds = SoundEffect()

title = font_menu.render("RUN AND JUMP", True, white)
start = Button(red, 200, 50, 260, 150, "start")
#about = Button()
option = Button(red, 200, 50, 260, 220, "option")
about = Button(red, 200, 50, 260, 290, "about")
exit = Button(red, 200, 50, 260, 360, "exit")

normal_mode = Button(red, 300, 50, 260, 150, "normal mode")
hard_mode = Button(red, 300, 50, 260, 290, "hard mode")

super_mode = white
offer_option = False
about_text = False

while game_start:

    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_start = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if start.is_mouse_pressed() and not offer_option:
                game_start = False
                running = True
            elif option.is_mouse_pressed() and not offer_option:
                offer_option = True
            elif about.is_mouse_pressed() and not offer_option:
                about_text = True
            elif normal_mode.is_mouse_pressed() and offer_option:
                lives = 70
                offer_option = False
            elif hard_mode.is_mouse_pressed() and offer_option:
                lives = 50
                offer_option = False
            elif exit.is_mouse_pressed() and not offer_option:
                game_start = False
                running = False

    screen.fill(black)
    screen.blit(title, (230, 100))
    if offer_option:
        normal_mode.draw(screen, camera)
        hard_mode.draw(screen, camera)
    else:
        start.draw(screen, camera)
        option.draw(screen, camera)
        about.draw(screen, camera)
        exit.draw(screen, camera)
    if about_text:
        screen.blit(font_menu.render("Nhom 2 - L01. Heh", True, white), (100, 450))
    pygame.display.flip()
    clock.tick(30)
    pass

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    
    i = (i+1)%20
    if i == 0:
        rand = random.randint(0, 8)
        match rand:
            case 0:
                zombie.append(Entity(ZOM, 0, 290, ["image\zom1.png", "image\zom1.png", "image\zom1.png", "image\zom1.png", "image\zom1.png", "image\zom1.png"], True, False))
            case 1:
                zombie.append(Entity(ZOM, 0, 310, ["image\zom2.png", "image\zom2.png", "image\zom2.png", "image\zom2.png", "image\zom2.png", "image\zom2.png"], True, False))
            case 2:
                zombie.append(Entity(ZOM, RIGHT_LIMIT, 290, ["image\zom1.png", "image\zom1.png", "image\zom1.png", "image\zom1.png", "image\zom1.png", "image\zom1.png"], True, True))
            case 3:
                zombie.append(Entity(ZOM, RIGHT_LIMIT, 310, ["image\zom2.png", "image\zom2.png", "image\zom2.png", "image\zom2.png", "image\zom2.png", "image\zom2.png"], True, True))
            case 4:
                book.append(Entity(COIN, random.randint(LEFT_LIMIT, RIGHT_LIMIT), 290, ["image/book.png"], False, False))
            case _:
                coin.append(Entity(COIN, random.randint(LEFT_LIMIT, RIGHT_LIMIT), 290, ["image\coin.png"], False, False))


    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and not player.already_jump:
        player.jumping = True
        player.already_jump = True
    if (keys[pygame.K_a] and not keys[pygame.K_d]) or (not keys[pygame.K_a] and keys[pygame.K_d]):
        player.moving = True
        #print(camera.x, player.x, brick.x, brick.width)
    else: player.moving = False
    if keys[pygame.K_a]:
        player.direction = True
    if keys[pygame.K_d]:
        player.direction = False

    if keys[pygame.K_j] and not shooting and stage != 0:
        print("shoot")
        shooting = True
        match stage:
            case 1:
                gun_shot.append(Entity(KUNAI, player.x, player.y + 20, ["image\level1.png", "image\level1.png", "image\level1.png", "image\level1.png", "image\level1.png", "image\level1.png"], True, player.direction))
            case 2:
                gun_shot.append(Entity(RASENGAN, player.x, player.y + 20, ["image\level2.png", "image\level2.png", "image\level2.png", "image\level2.png", "image\level2.png", "image\level2.png"], True, player.direction))

###########--------------------level up------------------------------------
    match point:
        case 10:
            stage = 1
            sounds.playLevelUp()
        case 20: 
            stage = 2
            sounds.playLevelUp()
        case _:
            if point%30 == 0 and point != 0:
                boss.append(Entity(BOSS, 0, 220, ["image/boss.png", "image/boss.png", "image/boss.png", "image/boss.png", "image/boss.png", "image/boss.png"], True, False))
                boss_appeared = True
                sounds.playLevelUp()

#--------------------------------------##########################################
    text = font.render("POINT: " + str(point) + "    HP: " + str(lives), True, super_mode)

    screen.fill(black)
    player.move()
    camera.follow(player)
    
    

######----------------------------------------DRAW-AND CHECK COLLISION-----------------------------------#############
    for k in background:
        k.draw(screen, camera)
    screen.blit(text, (0, 0))
    for k in coin:
        k.draw(screen, camera)
        rect = pygame.Rect(k.x, k.y, k.width, k.height)
        if rect.colliderect(pygame.Rect(player.x, player.y, player.width, player.height)): 
            point += 1
            if super_saiyan: lives += 1
            sounds.playPop()
            coin.remove(k)
    for k in book:
        k.draw(screen, camera)
        rect = pygame.Rect(k.x, k.y, k.width, k.height)
        if rect.colliderect(pygame.Rect(player.x, player.y, player.width, player.height)): 
            point += 1
            if super_saiyan: lives += 10
            sounds.playPop()
            book.remove(k)
    player.draw(screen, camera)
    brick.draw(screen, camera)
    lock.draw(screen, camera)

    if shooting:
        gun_shot[0].move()
        gun_shot[0].draw(screen, camera)
        if gun_shot[0].x < LEFT_LIMIT or gun_shot[0].x > RIGHT_LIMIT:
            shooting = False
            gun_shot.remove(gun_shot[0])

    if not super_saiyan:
        rect = pygame.Rect(lock.x, lock.y, lock.width, lock.height)
        if rect.colliderect(pygame.Rect(player.x, player.y, player.width, player.height)):
            if lock.value != PASS_LOCK_1: lock.value += 1
            else: 
                lock.setColor(green)
                super_mode = red
                super_saiyan = True
                speed[RASENGAN] += 15

    


    for k in zombie:
        k.move()
        k.draw(screen, camera)
        rect = pygame.Rect(k.x, k.y, k.width, k.height)
        if rect.colliderect(pygame.Rect(player.x, player.y, player.width, player.height)):
            sounds.playHammer()
            lives -= 1
            #print("fail")
            pass
        if k.x < LEFT_LIMIT or k.x > RIGHT_LIMIT:
            zombie.remove(k)
            continue
        if shooting:
            if rect.colliderect(pygame.Rect(gun_shot[0].x, gun_shot[0].y, gun_shot[0].width, gun_shot[0].height)):
                if stage == 1: 
                    gun_shot.remove(gun_shot[0])
                    shooting = False
                zombie.remove(k)
    
    if boss_appeared:
        boss[0].move()
        boss[0].draw(screen, camera)
        rect = pygame.Rect(boss[0].x, boss[0].y, boss[0].width, boss[0].height)
        if rect.colliderect(pygame.Rect(player.x, player.y, player.width, player.height)):
            game_over = True
    
    if point % 50 == 0 and point != 0 and boss_appeared:
        boss_appeared = False
        boss_defeated += 1
        boss.remove(boss[0])

        #####_______________game over_____________________##########
    if lives <= 0:
        game_over = True
    if game_over:
        running = False
        pass

    pygame.display.flip()
    clock.tick(30)


while game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if exit.is_mouse_pressed():
                game_over = False

    screen.fill(black)
    title = font_menu.render("Your points: " + str(point) + ". Boss defeated: " + str(boss_defeated), True, white)
    screen.blit(title, (100, 100))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()