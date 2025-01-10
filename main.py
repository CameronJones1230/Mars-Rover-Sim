import pygame
from sys import exit
import math
import text
import random
from settings import *
from text import Scheduler
from tkinter import *
import time

pygame.init()

# Creating the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Rover Simulation")
clock = pygame.time.Clock()

# Loads images
background = pygame.transform.scale(pygame.image.load("background/background.png").convert(), (WIDTH, HEIGHT))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(PLAYER_START_X, PLAYER_START_Y)
        self.image = pygame.transform.rotozoom(pygame.image.load("rover.png").convert_alpha(), 0, PLAYER_SIZE)
        self.base_player_image = self.image
        self.hitbox_rect = self.base_player_image.get_rect(center=self.pos)
        self.rect = self.hitbox_rect.copy()
        self.speed = PLAYER_SPEED
        self.shoot = False
        self.shoot_cooldown = 0
        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)
        self.curAngle = 90
        self.direction =[0,0]

    def player_rotation(self):
       # self.mouse_coords = pygame.mouse.get_pos()
        #self.x_change_mouse_player = (self.mouse_coords[0] - WIDTH // 2)
        #self.y_change_mouse_player = (self.mouse_coords[1] - HEIGHT // 2)
       # self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player))
        self.angle = random.randrange(0, 360, 3)
        self.curAngle = (self.curAngle + self.angle) % 360
        #print(str(self.angle) + "angle")
        #print(str(self.curAngle) + "CurAngle")
        #print("\n")

        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=self.hitbox_rect.center)
        if(self.curAngle > 0 and self.curAngle < 90):
            self.direction = [1,1]
        elif (self.curAngle == 90):
            self.direction = [0, 1]
        elif (self.curAngle > 90 and self.curAngle < 180):
            self.direction = [-1,1]
        elif (self.curAngle == 180):
            self.direction = [-1, 0]
        elif (self.curAngle > 180 and self.curAngle < 270):
            self.direction = [-1, -1]
        elif (self.curAngle == 270):
            self.direction = [0, -1]
        elif (self.curAngle > 270 and self.curAngle < 360):
            self.direction = [1,-1]
        elif (self.curAngle == 360):
            self.direction = [1,0]

        #print(self.direction)
    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()
        #
        # if keys[pygame.K_q]:
        #     f = open("output.txt", "a")
        #     f.write(schedule.)
        #     f.close()
        #     pygame.quit()
        #     exit()
        # if keys[pygame.K_s]:
        #     self.velocity_y = self.speed
        # if keys[pygame.K_d]:
        #     self.velocity_x = self.speed
        # if keys[pygame.K_a]:
        #     self.velocity_x = -self.speed

        if (self.direction[0] == 1):
            self.velocity_y = -self.speed
        elif (self.direction[0] == -1):
            self.velocity_y = self.speed
        elif (self.direction[0] == 0):
            self.velocity_y = 0

        if (self.direction[1] == 1):
            self.velocity_x = self.speed
        elif (self.direction[1] == -1):
            self.velocity_x = -self.speed
        elif (self.direction[1] == 0):
            self.velocity_x = 0

        if self.velocity_x != 0 and self.velocity_y != 0:  # moving diagonally
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)

        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]:
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False

    def is_shooting(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            spawn_bullet_pos = self.pos + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)

    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def update(self):
        self.user_input()
        self.move()
        #self.player_rotation()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("bullet/1.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, BULLET_SCALE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.x_vel = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.angle * (2 * math.pi / 360)) * self.speed
        self.bullet_lifetime = BULLET_LIFETIME
        self.spawn_time = pygame.time.get_ticks()  # gets the specific time that the bullet was created

    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()

    def update(self):
        self.bullet_movement()




class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = pygame.math.Vector2()
        self.floor_rect = background.get_rect(topleft=(0, 0))
        self.horiz_multi = 4
        self.Vert_multi = 4
        self.blit_list = []

    def custom_draw(self):
        self.offset.x = player.rect.centerx - WIDTH // 3
        self.offset.y = player.rect.centery - HEIGHT // 3 - 25

        # draw the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        screen.blit(background, floor_offset_pos)
        #for i in range(self.horiz_multi + 1):
            #if self.horiz_multi >=0:
        #screen.blit(background, (int(floor_offset_pos.x + WIDTH),int(floor_offset_pos.y + WIDTH)))
        xcheck = 0
        ycheck = 0
        for i in range(self.horiz_multi+2):
            if (i >= 10 and xcheck == 0):
                i = (self.horiz_multi+2) - 5
                xcheck = 1
            for j in range(self.Vert_multi+2):
                if (j >= 10 and ycheck == 0):
                    j = (self.Vert_multi + 2) - 5
                    ycheck = 1
                screen.blit(background, (floor_offset_pos + (WIDTH*i,0)))
                screen.blit(background, (floor_offset_pos - (WIDTH * i, 0)))
                screen.blit(background, (floor_offset_pos - (0, HEIGHT*j)))
                screen.blit(background, (floor_offset_pos + (0, HEIGHT * j)))
                screen.blit(background, (floor_offset_pos + (WIDTH*i, HEIGHT * j)))
                screen.blit(background, (floor_offset_pos - (WIDTH * i, HEIGHT * j)))
                screen.blit(background, (floor_offset_pos.x - (WIDTH * i),(floor_offset_pos.y + (HEIGHT * j))))
                screen.blit(background, (floor_offset_pos.x + (WIDTH * i), (floor_offset_pos.y - (HEIGHT * j))))
                #screen.blit(background, (floor_offset_pos + (HEIGHT * i, WIDTH * j)))
                #screen.blit(background, (floor_offset_pos - (HEIGHT * i, WIDTH * j)))
        xcheck = 0
        ycheck = 0
        self.horiz_multi = abs(int(floor_offset_pos.x) // (WIDTH // 2))
        self.Vert_multi = abs(int(floor_offset_pos.y) // (HEIGHT // 2))
       # print(str(player.rect.center) + " " + str(self.horiz_multi))
        #screen.blit(background, floor_offset_pos + (player.rect.centerx/WIDTH,0))
        #screen.blit(background, floor_offset_pos - (WIDTH, 0))
        #screen.blit(background, floor_offset_pos + (0, HEIGHT))
        #screen.blit(background, floor_offset_pos - (0, HEIGHT))

        for sprite in all_sprites_group:
            offset_pos = sprite.rect.topleft - self.offset
            screen.blit(sprite.image, offset_pos)



root = Tk()
menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu)
root.title("Rover Configuration")
root.geometry("1000x400")
menu.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='New')
filemenu.add_command(label='Open...')
filemenu.add_separator()
filemenu.add_command(label='Exit', command=root.quit)
helpmenu = Menu(menu)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='About')
WP = IntVar()
WC = IntVar()
IBP = IntVar()
IBC = IntVar()
COMP = IntVar()
COMCOMP = IntVar()
RP = IntVar()
RC = IntVar()
WPow = IntVar()
IBPow = IntVar()
COMPPOW = IntVar()
RPOW = IntVar()
battery = IntVar()
Recharge = IntVar()


label = Label(root, text="Weather Period")
label.grid(row=0, column=0, padx=10, pady=10)
entry = Entry(root, textvariable=WP)
entry.grid(row=0, column=1, padx=10, pady=10)
label1 = Label(root, text="Weather CompTime")
label1.grid(row=0, column=2, padx=10, pady=10)
entry1 = Entry(root, textvariable=WC)
entry1.grid(row=0, column=3, padx=10, pady=10)

labelPow1 = Label(root, text="Weather PowerComp")
labelPow1.grid(row=0, column=4, padx=10, pady=10)
entryPow1 = Entry(root, textvariable=WPow)
entryPow1.grid(row=0, column=5, padx=10, pady=10)

label2 = Label(root, text="Info Bus Period")
label2.grid(row=1, column=0, padx=10, pady=10)
entry2 = Entry(root, textvariable=IBP)
entry2.grid(row=1, column=1, padx=10, pady=10)
label3 = Label(root, text="Info Bus CompTime")
label3.grid(row=1, column=2, padx=10, pady=10)
entry4 = Entry(root, textvariable=IBC)
entry4.grid(row=1, column=3, padx=10, pady=10)

labelPow1 = Label(root, text="Info Bus PowerComp")
labelPow1.grid(row=1, column=4, padx=10, pady=10)
entryPow1 = Entry(root, textvariable=IBPow)
entryPow1.grid(row=1, column=5, padx=10, pady=10)

label5 = Label(root, text="Com Period")
label5.grid(row=2, column=0, padx=10, pady=10)
entry6 = Entry(root, textvariable=COMP)
entry6.grid(row=2, column=1, padx=10, pady=10)
label7 = Label(root, text="Com CompTime")
label7.grid(row=2, column=2, padx=10, pady=10)
entry8 = Entry(root, textvariable=COMCOMP)
entry8.grid(row=2, column=3, padx=10, pady=10)

labelPow1 = Label(root, text="Com PowerComp")
labelPow1.grid(row=2, column=4, padx=10, pady=10)
entryPow1 = Entry(root, textvariable=COMPPOW)
entryPow1.grid(row=2, column=5, padx=10, pady=10)

label = Label(root, text="Rotor Period")
label.grid(row=3, column=0, padx=10, pady=10)
entry = Entry(root, textvariable=RP)
entry.grid(row=3, column=1, padx=10, pady=10)
label1 = Label(root, text="Rotor CompTime")
label1.grid(row=3, column=2, padx=10, pady=10)
entry1 = Entry(root, textvariable=RC)
entry1.grid(row=3, column=3, padx=10, pady=10)

labelPow1 = Label(root, text="Rotor PowerComp")
labelPow1.grid(row=3, column=4, padx=10, pady=10)
entryPow1 = Entry(root, textvariable=RPOW)
entryPow1.grid(row=3, column=5, padx=10, pady=10)

var = StringVar()
var.set("RMS")  # Set a default value

var1 = StringVar()
var.set("None")  # Set a default value

var2 = BooleanVar()

# Create an OptionMenu (drop-down menu) with some options
dropdown = OptionMenu(root, var, "RMS", "EDF")
dropdown.grid(row=4, column=0, padx=10, pady=10)

dropdown = OptionMenu(root, var1, "None", "Ceiling","Inheritance")
dropdown.grid(row=4, column=1, padx=10, pady=10)

checkbox1 = Checkbutton(root, text="Default", variable=var2)
checkbox1.grid(row=4, column=2, padx=10, pady=10)

labelBattery = Label(root, text="max batterty (kW)")
labelBattery.grid(row=4, column=3, padx=10, pady=10)
entryBattery = Entry(root, textvariable=battery)
entryBattery.grid(row=4, column=4, padx=10, pady=10)

labelRecharge = Label(root, text="Battery Recharge Rate")
labelRecharge.grid(row=4, column=5, padx=10, pady=10)
entryRecharge = Entry(root, textvariable=Recharge)
entryRecharge.grid(row=4, column=6, padx=10, pady=10)



mainloop()

#print(var.get())
RMS = 0
if(var.get() == "RMS"):
    RMS = 1
else:
    RMS = 0
priorityInheritance = 0
priorityCeiling = 0
if(var1.get() == "None"):
    priorityInheritance = 0
    priorityCeiling = 0
elif(var1.get() == "Ceiling"):
    priorityInheritance = 0
    priorityCeiling = 1
else:
    priorityInheritance = 1
    priorityCeiling = 0

if(var2.get()):
    RMS = 1
    WP.set(20)
    WC.set(1)
    IBP.set(30)
    IBC.set(1)
    COMP.set(40)
    COMCOMP.set(1)
    RP.set(5)
    RC.set(1)
    WPow.set(0)
    IBPow.set(0)
    COMPPOW.set(0)
    RPOW.set(0)
    battery.set(10)
    Recharge.set(10)
    priorityInheritance = 0




all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

camera = Camera()
player = Player()
schedule = Scheduler(player,RMS,WP.get(),WC.get(),IBP.get(),IBC.get(),COMP.get(),COMCOMP.get(),RP.get(),RC.get(),WPow.get(),IBPow.get(),COMPPOW.get(),
                     RPOW.get(),battery.get(),Recharge.get(),priorityInheritance,priorityCeiling)
schedule.rmsPriorityGen()
schedule.priorityCeilingGen()
open("output", "w").close()
#print(schedule.ready)
#necromancer = Enemy((400, 400))

all_sprites_group.add(player)

while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            f = open("output.txt", "a")
            f.write(" " + str(schedule.DeadlinesMissed))
            f.close()
            pygame.quit()
            exit()



    if(schedule.RMS == 1):
        schedule.schedule()
    elif(schedule.RMS == 0):
        schedule.scheduleEDF()
    else:
        schedule.RoundRobin()


    screen.blit(background, (0, 0))

    camera.custom_draw()
    all_sprites_group.update()


    pygame.draw.rect(screen, (128,128,128), pygame.Rect(0, 530, 900, 500))
    pygame.draw.rect(screen, (128,128,128), pygame.Rect(900, 0, 400, 800))
    screen.blit(schedule.CurrentTask, schedule.CurrentTaskRect)
    screen.blit(schedule.ReadyText, schedule.ReadyTextRect)
    screen.blit(schedule.TerminatedText, schedule.TerminatedRect)
    screen.blit(schedule.StartText,schedule.StartTextRect)
    screen.blit(schedule.EndText,schedule.EndTextRect)
    screen.blit(schedule.CompText,schedule.CompTextRect)
    screen.blit(schedule.WeatherText, schedule.WeatherTextRect)
    screen.blit(schedule.BusText,schedule.BusTextRect)
    screen.blit(schedule.VMAText,schedule.VMATextRect)
    screen.blit(schedule.PowerText,schedule.PowerTextRect)
    screen.blit(schedule.RechargeText,schedule.RechargeTextRect)
    screen.blit(schedule.PowerUseText,schedule.PowerUseTextRect)
    screen.blit(schedule.TotalPowerText,schedule.TotalPowerTextRect)
    if(schedule.RMS == 2):
        screen.blit(schedule.RoundRobinText,schedule.RoundRobinTextRect)
    pygame.draw.rect(screen, (0,0,255), pygame.Rect(200, 635, schedule.Completion, 15))
    pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(920, 100, 200, 30))
    pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(1000, 200, 200, 30))
    screen.blit(schedule.VMAHeldText, schedule.VMAHeldTextRect)
    screen.blit(schedule.BusHeldText, schedule.BusHeldTextRect)
    #print(schedule.NoPowerTime)
   # print(schedule.ready)
    #pygame.draw.rect(screen, "red", player.hitbox_rect, width=2)
    # pygame.draw.rect(screen, "yellow", player.rect, width=2)

    pygame.display.update()
    clock.tick(FPS)




