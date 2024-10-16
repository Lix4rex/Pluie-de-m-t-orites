#### LIBRARY ####

from tkinter import *
from PIL import Image, ImageTk
from random import randint



#### VARIABLES ####

game_name = "SPACESHIP"


started = False


fen = Tk()
bg_color = "gray"

main_frame = Frame(fen, bg = bg_color)

title = Label(main_frame, text = game_name, font = "Courier 40 bold", fg = "blue", bg = bg_color)
play_button = Button(main_frame, text = "PLAY", font = "Courier 30 bold", bg = "black", fg = "blue")
quit_button = Button(main_frame,  text = "QUIT", font = "Courier 20 bold", bg = "black", fg = "blue")


game_frame = Frame(fen)

x_max = 400
y_max = 600

y = 7*y_max/8  # Constant
x = x_max/2
spaceship_size = 50

speed = 2
move = 0


dt = 10  # miliseconds (Refresh time)

canvas = Canvas(game_frame, width = x_max, height = y_max, bg = bg_color)

image = Image.open("Image/spaceship.png")
resize_image = image.resize((spaceship_size, spaceship_size))
spaceship_image = ImageTk.PhotoImage(resize_image)
spaceship = canvas.create_image(x - spaceship_size/2, y, anchor=NW, image = spaceship_image)


life = 3
heart_size = 50

image = Image.open("Image/heart.png")
resize_image = image.resize((heart_size, heart_size))
heart_image = ImageTk.PhotoImage(resize_image)

image = Image.open("Image/empty_heart.png")
resize_image = image.resize((heart_size, heart_size))
empty_heart_image = ImageTk.PhotoImage(resize_image)

x_hearts = 10
y_hearts = y_max/2

heart1 = canvas.create_image(x_hearts, y_hearts - 3*heart_size/2, anchor = NW, image = heart_image)
heart2 = canvas.create_image(x_hearts, y_hearts - heart_size/2, anchor = NW, image = heart_image)
heart3 = canvas.create_image(x_hearts, y_hearts + heart_size/2, anchor = NW, image = heart_image)

hearts = [heart1, heart2, heart3]


missile_size = 30
missile_speed = 4
missile_cadence = 20
waiting = False
missile_compt = 0

image = Image.open("Image/missile.png")
resize_image = image.resize((int(missile_size/2), missile_size))
missile_image = ImageTk.PhotoImage(resize_image)


score = 0
score_size = 20
score_info = canvas.create_text(5*score_size, 2*score_size, text = "Score : " + str(score), font = "Courier " + str(score_size) + " bold")

asteroid_size = 50
asteroid_speed = 2
asteroid_cadence = 50
asteroid_compt = 0
image = Image.open("Image/asteroid.png")
resize_image = image.resize((asteroid_size, asteroid_size))
asteroid_image= ImageTk.PhotoImage(resize_image)
asteroids = []



#### CLASS ####

class Space():
    def __init__(self, height):
        self.item = Label(main_frame, height = height,  text = "", bg = bg_color)


class Missile():
    def __init__(self, self_missile_speed):
        self.x = x + spaceship_size/2
        self.y = y
        self.item = canvas.create_image(self.x, self.y, anchor = NW, image = missile_image)
        self.speed = self_missile_speed
        self.loop()

    def loop(self):
        global score, asteroids, asteroid_cadence, asteroid_speed

        if score >= 25 and asteroid_cadence >= 50: 
            asteroid_cadence -= 10
        if score >= 50 and asteroid_cadence >= 40:
            asteroid_cadence -= 10
        if score >= 100 and asteroid_cadence >= 30:
            asteroid_cadence -= 10

        if score >= 200 and asteroid_speed <= 2 :
            asteroid_speed += 1

        if score >= 1000 and asteroid_speed <= 4 :
            asteroid_speed += 1

        self.y -= self.speed
        canvas.coords(self.item, self.x, self.y)

        destroyed_asteroid = []

        for asteroid in asteroids:
            if self.contact(asteroid):
                score += 1
                canvas.itemconfig(score_info, text = "Score : " + str(score))
                asteroid.destroyed = True
                destroyed_asteroid.append(asteroid)
                self.y = -42  # This missile will be destroyed at the next iteration

        for asteroid in destroyed_asteroid :
            asteroids.remove(asteroid)

        if self.y >= 0 and not(lose()):
            fen.after(dt, self.loop)
        else:
            canvas.delete(self.item)

    def contact(self, asteroid):
        return (asteroid.x <= self.x <= asteroid.x + asteroid_size or self.x <= asteroid.x <= self.x + missile_size) and asteroid.y <= self.y <= asteroid.y + asteroid_size


class Asteroid():
    def __init__(self, self_asteroid_speed):
        self.x = randint(0, x_max - asteroid_size)
        self.y = 0
        self.item = canvas.create_image(self.x, self.y, anchor = NW, image = asteroid_image)
        self.speed = self_asteroid_speed
        self.destroyed = False
        self.loop()

    def loop(self):
        global score
        if self.destroyed :
            canvas.delete(self.item)
        elif self.y >= y_max :
            score -= 1
            canvas.itemconfig(score_info, text = "Score : " + str(score))
            canvas.delete(self.item)
        elif not(lose()) :
            self.y += self.speed
            canvas.coords(self.item, self.x, self.y)
            fen.after(dt, self.loop)



#### FUNCTION ####

def lose():
    return life == 0

def loop():
    global x, move, missile_compt, waiting, asteroids, life, asteroid_compt

    x += move
    if waiting :
        missile_compt += 1
    if missile_compt >= missile_cadence :  # Prevent players from launching missile by spamming 
        waiting = False
        missile_compt = 0

    if move < 0 and x <= 0 :
        move = 0 

    if move > 0 and x + spaceship_size >= x_max :
        move = 0

    asteroid_compt += 1
    if asteroid_compt >= asteroid_cadence :
        asteroid_compt = 0
        launch_rock()

    touched_asteroid = []
    for asteroid in asteroids :
        if asteroid.y <= y <= asteroid.y + asteroid_size and (asteroid.x <= x <= asteroid.x + asteroid_size or x <= asteroid.x <= x + spaceship_size):
            touched_asteroid.append(asteroid)
            asteroid.y = y_max + 42  # This asteroid will be destroyed at the next iteration
            life -= 1 
            canvas.itemconfig(hearts[life], image = empty_heart_image)

    for asteroid in touched_asteroid :
        asteroids.remove(asteroid)

    canvas.coords(spaceship, x , y)

    if not(lose()):
        fen.after(dt, loop)


def right(event):
    global move
    if started :
        move = speed

def left(event):
    global move
    if started :
        move = -speed

def launch_missile(event):
    global waiting
    if not(waiting) :
        waiting = True
        Missile(missile_speed)


def launch_rock():
    asteroids.append(Asteroid(asteroid_speed))


def play():
    global started
    main_frame.destroy()
    game_frame.pack()
    started = True
    loop()




#### PRINT ####

height = str(x_max) + "x" + str(y_max)
fen.geometry(height)

fen.resizable(width = False, height = False)
fen.title(game_name)
fen.configure(bg = bg_color)


## Main frame ##

Space(8).item.pack()

title.pack()

Space(12).item.pack()

play_button.config(command = play)
play_button.pack()

main_frame.bind("<Return>", play)

Space(1).item.pack()

quit_button.config(command = fen.destroy)
quit_button.pack()

main_frame.pack()


## Game frame ##


fen.bind("d", right)
fen.bind("<Right>", right)
fen.bind("q", left)
fen.bind("<Left>", left)

fen.bind("<space>", launch_missile)

canvas.pack()


fen.mainloop()