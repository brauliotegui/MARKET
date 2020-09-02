
import numpy as np
import cv2
import random

TILE_SIZE = 32              # basically defines size of each tile and to how many pixels it correspond (that is 32*32 pixels = 1 tile)
OFS = 50                    # the black area around the supermarket picture (OFFSET)

# this is a represantation of the market with one symbol '#', '.', 'b' or similar for each tile on the png-file
MARKET = """
##################
##..............##
##..##..##..##..b#
##..##..##..##..b#
##..##..##..##..##
##..##..##..##..##
##..##..##..##..##
##...............#
##..##..##..##...#
##..##..##..##...#
##...............#
##################
""".strip()


class TiledMap:             # constructor for the map, connecting the image to the code, builds the objects from the class; here I understand it only on a higher level, but I believe for this weeks task this is enough

    def __init__(self, layout, tiles):
        self.tiles = tiles
        self.contents = [list(row) for row in layout.split('\n')]
        self.xsize =  len(self.contents[0])
        self.ysize = len(self.contents)
        self.image = np.zeros((self.ysize * TILE_SIZE, self.xsize * TILE_SIZE, 3), dtype=np.uint8)
        self.prepare_map()

    def get_tile_bitmap(self, char): # general format of tiles: [y-coord, x-coord, color-tuple]
        if char == '#':             #  if character is '#' in MARKET-> slice here, turning hash-symbols into blue squares
            return self.tiles[0:32, 0:32, :]
        elif char == 'b':           # gives shop-able items, like bananas or else, written into MARKET at the top
            return self.tiles[0:32, -1*TILE_SIZE:, :]
        else:
            return self.tiles[32:64, 64:96, :]

    def prepare_map(self):
        for y, row in enumerate(self.contents):
            for x, tile in enumerate(row):
                bm = self.get_tile_bitmap(tile)
                self.image[y * TILE_SIZE:(y+1)*TILE_SIZE,
                      x * TILE_SIZE:(x+1)*TILE_SIZE] = bm

    def draw(self, frame):
        frame[OFS:OFS+self.image.shape[0], OFS:OFS+self.image.shape[1]] = self.image

class Customer:             # our shopping ghost

    def __init__(self, tmap, image, x, y): # how its position on the map cn be definedwhen the calss is instantiated
         self.tmap = tmap
         self.image = image
         self.x = x
         self.y = y

    def draw(self, frame):              # puts the customer-object onto the map
        xpos = OFS + self.x * TILE_SIZE
        ypos = OFS + self.y * TILE_SIZE
        frame[ypos:ypos+TILE_SIZE, xpos:xpos+TILE_SIZE] = self.image

    def move(self, direction):          # defines movement of the customer-object, that is the new position for each moving event

        newx = self.x
        newy = self.y
        if direction == 'up':
            newy -= 1
        if direction == 'down':
            newy += 1
        if direction == 'left':
            newx -= 1
        if direction == 'right':
            newx += 1

        if self.tmap.contents[newy][newx] != '#':    #if statement allows customers to move only on dots, not on # in the MARKET
            self.x = newx                             # changed inorder not to be able to moveon #, but yet onto groceries
            self.y = newy


    def __repr__(self):                     # returns where the customer is drwan, if no errors occur
        return f"customer at {self.x}/{self.y}"

background = np.zeros((700, 1000, 3), np.uint8)  # not sure what this does
tiles = cv2.imread('tiles.png')                 # calls the empty supermarket image (which has to be in the same folder as the script)

# takes the position and thereby one of the different images from  the tiles.png
customer_image = tiles[-2*TILE_SIZE:-1*TILE_SIZE,:1*TILE_SIZE]  # this one gives a ghost
customer_image2 = tiles[-3*TILE_SIZE:-2*TILE_SIZE,:1*TILE_SIZE] # this one gives a pacman

tmap = TiledMap(MARKET, tiles)

c = Customer(tmap,customer_image, 15,10)
c2 = Customer(tmap,customer_image2, 13,10)

 # a simple way of increasing the number of (identical looking) customers, to include only one, the shorter version of bunch is used
bunch = [Customer(tmap, customer_image, 15, 10)]
#bunch = [Customer(tmap, customer_image, 15-np.random.randint(3), 10np.random.randint(3)) for c in range(10)]

# infinite loop to refresh the frame with supermarket and customers on
while True:
    frame = background.copy()
    tmap.draw(frame)
    for c in bunch:
        c.draw(frame)
    c2.draw(frame)


    cv2.imshow('frame', frame)

    key = chr(cv2.waitKey(1) & 0xFF) # key-settings allow to interact with the frame, exert movement based on the 'PC-gaming keys: wasd', use 'q' in the frame to exit
    if key == 'w':
        c.move('up')
    if key == 's':
        c.move('down')
    if key == 'a':
        c.move('left')
    if key == 'd':
        c.move('right')

    if key == 'q':
        break

cv2.destroyAllWindows()


# sniplets that might  be useful for implementing movement based on locations and transition probabilites, far from working
# Location_class filling with customers
#
# #Option 1:
#         if self.new_state == 'spices':
#             newx = self.spices[np.random.randint(ailse_start,aisle_end)]
#             newy = self.spices[np.random.randint(ailse_start,aisle_end)]
