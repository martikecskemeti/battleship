#imports
import os
import urllib.request
import time

import pyglet, time
from pyglet.media import Player

from threading import Thread

def real_playsound () :
    sound = pyglet.media.load('mt.wav')
    player = Player()
    player.queue(sound)
    player.eos_action=player.EOS_LOOP
    player.play()
    pyglet.app.run()

def playsound():
    global player_thread
    player_thread = Thread(target=real_playsound)
    player_thread.start()
    
playsound()

rows, columns = os.popen('stty size', 'r').read().split()

def center(text):
    num = (int(columns) / 2) - (len(text) / 2)
    s = ' ' * int(num)
    return ('%s%s' % (s, text))

#start screen at the beginning of the game
def startScreen():
    
    #clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    
    b1 = RED+"__________         __    __  .__         "+PURPLE+"       .__    .__        "
    b2 = RED+"\______   \_____ _/  |__/  |_|  |   ____ "+PURPLE+"  _____|  |__ |__|_____    "
    b3 = RED+" |    |  _/\__  \\   __\   __\  | _/ __ \ "+PURPLE+" /  ___/  |  \|  \____  \  "
    b4 = RED+" |    |   \ / __ \|  |  |  | |  |_\  ___/ "+PURPLE+"\___ \|   Y  \  |  |_> >  "
    b5 = RED+" |______  /(____  /__|  |__| |____/\___  >"+PURPLE+"____  >___|  /__|   __/   "
    b6 = RED+"        \/      \/                     \/ "+PURPLE+"    \/     \/   |__|      "+ENDC

    print("\n")
    print (center(b1))
    print (center(b2))
    print (center(b3))
    print (center(b4))
    print (center(b5))
    print (center(b6))
    print("\n")

    print (center(YELLOW+")_"))
    print (center("_____|_|_____+__"))
    print (center("        |   "+OKGREEN+"x    x  x"+YELLOW+"   |"))
    print (center("\\----|------------------------------------------/"))
    print (center("\\                                             /"))
    print (center(OKBLUE+"/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\  "))
    print (center("\n"))
    print (center("                           Credits: M & M                            "+ENDC))
    print ("\n")

    #variables used for the multiplayer
    multiplayer = 0
    enemy = 0
    lifes = 17
    lastEnemyShotId = 0

    #menü
    while 1==1:
        command = input(center("Type '"+OKGREEN+"s"+ENDC+"' to start single screen game, '"+OKBLUE+"m"+ENDC+"' for multi screen game or '"+RED+"c"+ENDC+"' to close. "))
        if command == "s":
            placeships()
            break
        elif command == "m":
            multiStart()
            break
        elif command == "c":
            break
        elif command == "ultimatewincheat":
            winSituation(1)
            exit()

#this is the main game recursive function that runs until the game ends
def turn(map, mapDraw, player, playeronthismachine = 2):
    
    #used variables for the whole function
    changePlayer = True             #change player or not at the end if we have an error it wont change
    tmpPlayer = player              #we need a temporary player the be able to change on it if its needed. (if its a parameter we cant) -> this is bullshit. :D 
    couldHit = False                #if we could hit our enemy it changes to True
    global lifes
    global lastEnemyShotId
    
    #define enemy
    enemy = 0
    if player == 2:
        enemy = 1
    elif player == 1:
        enemy = 2

    #define enemy var but only in multi screen mode then get checking that maybe the other player won already
    if playeronthismachine == 1:

        #check enemy has won
        result = apiComm("get", enemy, "won")
        if result[0] != "[error]":
            winSituation(enemy)
            return
    
    #clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    #kirajzoljuk a képernyőt és bekérjük hogy hova lőjjünk, lekezeljük ha faszságot ír be
    print("Player "+str(player)+"'s turn")
    if playeronthismachine == 1:
        print("You have "+str(lifes)+" lives")
    print()
    drawMap(mapDraw, int(player)-1)
    whereToShoot = input(center("Choose where would you like to shoot! "))

    #converting coordinates
    try:
        whereToShoot = whereToShoot.split(" ")
        whereToShoot[0] = rep_num(whereToShoot[0])
        x = int(whereToShoot[0])-1      #x coordinate of shot
        y = int(whereToShoot[1])-1      #y coordinate of shot

    except (ValueError, IndexError, TypeError):
        input(center("Invalid format! Please give the coordinates like this: A 5 [press enter to continue]"))
        changePlayer = False
    
    #check coordinates for index error
    if changePlayer == True and not (x >= 0 and x < 10 and y >= 0 and y < 10):
        changePlayer = False
        input(center("Your coordinates are out of range. The table is 10 * 10 big! [press enter to continue]"))

    #if it hasnt been shoted already and we havent got any error so far
    if changePlayer == True:
        
        #draw shot if you are okey
        if not (mapDraw[player-1][x][y].isdigit() or mapDraw[player-1][x][y] == RED + "x" + ENDC):
            if map[enemy-1][x][y].isdigit():
                mapDraw[player-1][x][y] = map[enemy-1][x][y]
                couldHit = True
            else:
                print("videjött"+str(player))
                mapDraw[player-1][x][y] = RED + "x" + ENDC
            
            #print out the the map after the shot
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Player "+str(player)+"'s turn")
            drawMap(mapDraw, player-1)

            #ez csak 1 képernyős módban jöjjön be (2 képernyőnél úgy is csak a saját mapunk látjuk)
            if playeronthismachine == 2:
                input("[press enter to continue]")
        
        #if it has been shoted already
        else:
            input(center("You shot here already before. Choose other coordinates! [press enter to continue]"))
            changePlayer = False
    
    #megnézzük kilőttük -e az ellenfelet teljesen
    if checkDrawMap(mapDraw,player-1) == True:
        apiComm("set",player,"won",player)
        winSituation(player)
        return
    
    #mind a két játékos 1 képernyőn van
    if changePlayer == True:
        if playeronthismachine == 2:
            
            #eldöntjük hogy a következő körben ki lesz a következő körben
            if int(tmpPlayer) == 1:
                tmpPlayer = 2
            elif int(tmpPlayer) == 2:
                tmpPlayer = 1
        
        #a játékosok külön képernyőn tolják
        elif playeronthismachine == 1:

            #defining how much life the enemy lost
            lifesenemylost = 0
            if couldHit == True:
                lifesenemylost = 1
            
            #sending my shot to the enemy
            apiComm("set",player,"hit", lifesenemylost)

            #waiting for enemy shot
            while True:
                
                #checking enemy is ready
                answer = False
                answer = apiComm("get", enemy, "hit")

                # waiting for answer
                while not answer:
                    pass
                
                #checking the answer
                if answer[0] == "[error]" or int(answer[0]) == int(lastEnemyShotId):
                    iswon = False
                    iswon = apiComm("get", enemy, "won")
                    if iswon[0] != "[error]":
                        winSituation(enemy)
                    
                    print("Waiting for enemy to shot.")
                    # time.sleep(2)
                else:

                    #if we have a new shot minus lifes then break the while for new turn
                    if int(lastEnemyShotId) < int(answer[0]):
                        lastEnemyShotId = answer[0]
                        if int(answer[1]) == 1:
                            lifes -= lifesenemylost

                        break
    
    #change player
    turn(map, mapDraw, tmpPlayer, playeronthismachine)

#choose where to put the ships
def placeships(playersonthismachine = 2):

    for i in range(0,playersonthismachine):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Place your ships in the ocean!")
        print()
        drawMap(map, i)
        carrier = ship(5, "carrier", i)
        coordinates(i,carrier[0],carrier[1],carrier[2],5)

        os.system('cls' if os.name == 'nt' else 'clear')
        print("Place your ships in the ocean!")
        print()
        drawMap(map, i)
        battleship = ship(4, "battleship", i)
        coordinates(i,battleship[0],battleship[1],battleship[2],4)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print ("Place your ships in the ocean!")
        print()
        drawMap(map, i)
        cruiser = ship(3, "cruiser", i)
        coordinates(i,cruiser[0],cruiser[1],cruiser[2],3)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Place your ships in the ocean!")
        print()
        drawMap(map, i)
        submarine = ship(3, "submarine", i)
        coordinates(i,submarine[0],submarine[1],submarine[2],3)

        os.system('cls' if os.name == 'nt' else 'clear')
        print("Place your ships in the ocean!")
        print()
        drawMap(map, i)
        destroyer = ship(2, "destroyer", i)
        coordinates(i,destroyer[0],destroyer[1],destroyer[2],2)
    
    if playersonthismachine == 2:
        turn(map, mapDraw, 1)

#win screen
def winSituation(player):
    os.system('cls' if os.name == 'nt' else 'clear')
    if player == 1:
        print()
        print (center(YELLOW+"   __________.__                               ____ "+RED+"                     ._."))
        print (center(YELLOW+"   \______   \  | _____  ___.__. ___________  /_   |"+RED+" __  _  ______   ____| |"))
        print (center(YELLOW+"    |     ___/  | \__  \<   |  |/ __ \_  __ \  |   | "+RED+"\ \/ \/ /  _ \ /    \ |"))
        print (center(YELLOW+"    |    |   |  |__/ __ \\___  \  ___/|  |  \/  |   |"+RED+"  \     (  <_> )   |  \|"))
        print (center(YELLOW+"    |____|   |____(____  / ____|\___  >__|     |___| "+RED+"  \/\_/ \____/|___|  /_"))
        print (center(YELLOW+"                       \/\/         \/               "+RED+"                  \/\/"+ENDC))
        print()
    elif player == 2:
        print()
        print (center(OKGREEN+" __________.__                              ________  "+RED+"                     ._."))
        print (center(OKGREEN+" \______   \  | _____  ___.__. ___________  \_____  \ "+RED+" __  _  ______   ____| |"))
        print (center(OKGREEN+"  |     ___/  | \__  \<   |  |/ __ \_  __ \  /  ____/ "+RED+" \ \/ \/ /  _ \ /    \ |"))
        print (center(OKGREEN+"  |    |   |  |__/ __ \\___  \  ___/|  |  \/ /       \ "+RED+"  \     (  <_> )   |  \|"))
        print (center(OKGREEN+"  |____|   |____(____  / ____|\___  >__|    \_______ \  "+RED+" \/\_/ \____/|___|  /_"))
        print (center(OKGREEN+"                     \/\/         \/                \/  "+RED+"                 \/\/"+ENDC))
        print()
    exit()

#this function will draw the map to the console
def drawMap(map, mapID):
    row_names = ["A","B","C","D","E","F","G","H","I","J"]
    col_names = ["  ","1.","2.","3.","4.","5.","6.","7.","8.","9.","10."]
    print (center((OKBLUE+"".join(col_names)+ENDC)))
    for i in range(0,10):
        print (center((OKBLUE+str(row_names[i])+ENDC+" " + " ".join(map[mapID][i]))))


def rep_num(m):
    row_names = ["A","B","C","D","E","F","G","H","I","J"]
    n = 0
    for i in row_names:
        n += 1
        if m ==  i:
            m = str(n)
            return m

def checkDrawMap(drawMap,player):
    result = 0
    for i in range(0,len(drawMap[player])):
        for n in range(0,len(drawMap[player][i])):
            result += str(drawMap[player][i][n]).count("5")
            result += str(drawMap[player][i][n]).count("4")
            result += str(drawMap[player][i][n]).count("3")
            result += str(drawMap[player][i][n]).count("2")

    if result == 17:
        return True
    else:
        return False


def ship(length, shipname, player):
    
    #loop it until we get proper coordinates
    while True:
        
        #for checkin ok coordinates    
        x = 0

        #if coordinates arent good ask for coordinates
        print()
        print(center("To give orientation to your ships use H for horizontal, V for verical."))
        carrier = input(center("Give coordinates for "+RED+shipname+ENDC+" [e.g. H A 1]: "))
        
        #checks the numeric parts of the coordinates that it is in the index range
        shipCoo = carrier.split(" ")

        #checks for the right form of input
        while True:
            row_names = ["A","B","C","D","E","F","G","H","I","J"]
            if len(shipCoo) == 3:
                if shipCoo[0] == "H" or shipCoo[0] == "V":
                    if shipCoo[1] in row_names:
                        break
                    else:
                        carrier = input(center("Give orientation and coordinates for "+RED+shipname+ENDC+": "))
                        shipCoo = carrier.split(" ")
                else:
                    carrier = input(center("Give orientation and coordinates for "+RED+shipname+ENDC+": "))
                    shipCoo = carrier.split(" ")
            else:
                carrier = input(center("Give orientation and coordinates for "+RED+shipname+ENDC+": "))
                shipCoo = carrier.split(" ")
    
        #checks the starting coordinates
        shipCoo[1] = rep_num(shipCoo[1])

        if int(shipCoo[1]) > 0 and int(shipCoo[1]) <= 10 and int(shipCoo[2]) > 0 and int(shipCoo[2]) <= 10:
            x += 1
        
        #checking the ship endpoint if its horizontal or vertical
        if shipCoo[0] == "V":
            if int(shipCoo[1])+length-1 > 0 and int(shipCoo[1])+length-1 <= 10 and int(shipCoo[2]) > 0 and int(shipCoo[2]) <= 10:
                x += 1
        elif shipCoo[0] == "H":
            if int(shipCoo[1]) > 0 and int(shipCoo[1]) <= 10 and int(shipCoo[2])+length-1 > 0 and int(shipCoo[2])+length-1 <= 10:
                x += 1

        #checks ship collide
        if x == 2:
            if shipCoo[0] == "H":
                for i in range(length):
                    if map[player][int(shipCoo[1])-1][int(shipCoo[2])+ i - 1].isdigit():
                        x = 0
                print (center("Ooops, you have already placed a ship there!"))
                                
            elif shipCoo[0] == "V":
                for i in range(length):
                    if map[player][int(shipCoo[1])+ i - 1][int(shipCoo[2])-1].isdigit():
                        x = 0
                print (center("Ooops, you have already placed a ship there!"))
        
        #both coordinates are okey
        if x == 2:
            return shipCoo

#putting down the ships
def coordinates(p,o,y,z,w):
    if o == "H":
        z = int(z)
        for n in range(w):
            z += 1
            map[p][int(y)-1][int(z)-2] = str(w)

    elif o == "V":
        y = int(y)
        for n in range(w):
            y += 1
            map[p][int(y)-2][int(z)-1] = str(w)



#communication with the api server
def apiComm(action, player=False, option=False, value = False):
    
    #get datas from the server
    if action == "get":
        
        #sending request
        with urllib.request.urlopen('http://battleshipio.standapp.hu/get/'+str(player)+'/'+str(option)) as response:
            answer = response.read()
        
        #checking answer. if no errors it returns the answer, if we have an error it returns false
        if answer == "[error]":
            return False
        else:
            answer = str(answer).split("'")
            answer = str(answer[1]).split(";")
            return answer
            
    #insert data to the database
    elif action == "set":
        
        #sending request
        with urllib.request.urlopen('http://battleshipio.standapp.hu/set/'+str(player)+'/'+str(option)+'/'+str(value)) as response:
            answer = response.read()

        #if everything is OK 
        if answer.decode("utf-8") == "[ok]":
            return True
        else:
            return False

    #emptying out the database
    elif action == "truncate":
        
        #sending request
        with urllib.request.urlopen('http://battleshipio.standapp.hu/truncate') as response:
            answer = response.read()

        #if everything is OK 
        if answer.decode("utf-8") == "[ok]":
            return True
        else:
            return False

def multiStart():
    
    #You belive or not this for choosing player :)
    multiplayer = input("Which player would you like to be? [1,2] ")
    enemy = 0

    #printing out that we are emptying the db, do it end then defining the who will be the enemy
    if int(multiplayer) == 1:
        print("Truncating database!")
        apiComm("truncate")
        enemy = 2
    else:
        enemy = 1
    
    #sending to the server that we are here, and we want to play
    print("Hi everyone! I want to play with someone!")
    apiComm("set",multiplayer,"imready","")

    #now waiting for enemy
    while True:
        
        #checking enemy is ready
        answer = False
        answer = apiComm("get", enemy, "imready")
        
        #waiting for the answer to arrive
        while not answer:
            pass

        #checking the answer
        if answer[0] == "[error]":
            print("No one wants to play with me. I feel alone :(")
        else:
            print("Finally! Let's play!")
            break
    
    #placing down the ships
    placeships(1)

    #serialize
    serializedmap = ""
    for i in range(0,len(map[0])):
        for j in range(0,len(map[0][i])):
            serializedmap += str(map[0][i][j])
    
    #sending it to the server
    apiComm("set", multiplayer, "mymap", serializedmap)

    #now waiting for enemy
    serializedmap = ""
    while True:
        
        #checking enemy is ready
        serializedmap = False
        serializedmap = apiComm("get", enemy, "mymap")
        
        # waiting for answer
        while not serializedmap:
            pass

        #checking the answer
        if serializedmap[0] == "[error]":
            print("Your enemy hasn't finished placing ships")
            # time.sleep(2)
        else:
            print("Finally! Let's play!")
            # time.sleep(2)
            break
    
    #now converting the serializedmap to a 2 dimensons list 
    serializedmap = list(serializedmap[1])
    tmpmap = []
    imhereinthemap = 0
    for i in range(0, 10):
        tmpmap.append([])
        for j in range(0, 10):
            tmpmap[i].append(serializedmap[imhereinthemap])
            imhereinthemap += 1
    
    #setting the enemy's map
    map[enemy-1] = tmpmap

    #now lets start the game
    turn(map, mapDraw, int(multiplayer), 1)

#init maps
#map for ships
map = []
for p in range(0,2):
    map.append([])
    for i in range(0, 10):
        map[p].append([])
        for j in range(0,10):
            map[p][i].append("~")

#map for drawing
mapDraw = []
for p in range(0,2):
    mapDraw.append([])
    for i in range(0, 10):
        mapDraw[p].append([])
        for j in range(0,10):
            mapDraw[p][i].append("~")

#variables used for the multiplayer
multiplayer = 0
enemy = 0
lifes = 17
lastEnemyShotId = 0

#colors
PURPLE = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'

startScreen()