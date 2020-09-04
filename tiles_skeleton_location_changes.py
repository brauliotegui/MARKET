
import numpy as np
import cv2
import random
import time

TILE_SIZE = 32              # basically defines size of each tile and to how many pixels it correspond (that is 32*32 pixels = 1 tile)
OFS = 50                    # the black area around the supermarket picture (OFFSET)

# this is a represantation of the market with one symbol '#', '.', 'b' or similar for each tile on the png-file
MARKET = """
##################
##..............##
##..pq..aw..db..##
##..pq..aw..db..##
##..pq..aw..db..##
##..pq..aw..db..##
##..pq..aw..db..##
##...............#
##..xy..zx..xm...#
##..yx..xz..mx...#
##............s.s#
##################
""".strip()


class TiledMap:

    def __init__(self, layout, tiles):
        self.tiles = tiles
        self.contents = [list(row) for row in layout.split('\n')]
        self.xsize =  len(self.contents[0])
        self.ysize = len(self.contents)
        self.image = np.zeros((self.ysize * TILE_SIZE, self.xsize * TILE_SIZE, 3), dtype=np.uint8)
        self.prepare_map()

    def get_tile_bitmap(self, char):
        if char == '#':
            return self.tiles[0:32, 0:32, :]  #y, x, z
        elif char == 'b':
            return self.tiles[0:32, 128:160, :]
        elif char == 'd':
            return self.tiles[64:96, 128:160, :]
        elif char == 'w':
            return self.tiles[96:128, 128:160, :]
        elif char == 'a':
            return self.tiles[96:128, 160:192, :]
        elif char == 'q':
            return self.tiles[32:64, 128:160, :]
        elif char == 'p':
            return self.tiles[64:96, 192:224, :]
        elif char == 'x':
            return self.tiles[128:160, 128:160, :]
        elif char == 'y':
            return self.tiles[192:224, 96:128, :]
        elif char == 'z':
            return self.tiles[160:192, 96:128, :]
        elif char == 'm':
            return self.tiles[96:128, 224:256, :]
        elif char == 's':
            return self.tiles[32:64, 0:32, :]
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

class Customer:
    '''
    Customer class that models the customer behavior in a supermarket.
    '''


    def __init__(self,  tmap, image, x, y, current_location):
        self.tmap = tmap
        self.image = image
        self.x = x
        self.y = y
        self.current_location = current_location
        self.possible_locations = ['dairy', 'drinks', 'fruits', 'spices']
        self.transition_probabilities = {
               'dairy': [0.74391989, 0.00658083, 0.06437768, 0.06723891],
               'drinks': [0.10649731, 0.61064973, 0.06350757, 0.10600879],
               'fruits': [0.07036747, 0.07271306, 0.60711493, 0.04652072],
               'spices': [0.1490228 , 0.13192182, 0.09934853, 0.38925081]}

    def change_location(self):
         '''
         Choses a new location among the provided locations.

         Parameters
         ----------
         locations : The locations the customer might transition to.
         '''
         newx = self.x
         newy = self.y
         new_location = random.choices(self.possible_locations, self.transition_probabilities[self.current_location])[0]

         self.current_location = new_location
         if self.current_location == 'spices':
             newx = OFS + TILE_SIZE * np.random.randint(11,12)
             newy = OFS + TILE_SIZE * np.random.randint(1,10)
         elif self.current_location == 'fruits':
             newx = OFS + TILE_SIZE * np.random.randint(14,15)
             newy = OFS + TILE_SIZE * np.random.randint(1,10)
         elif self.current_location == 'drinks':
             newx = OFS + TILE_SIZE * np.random.randint(3,4)
             newy = OFS + TILE_SIZE * np.random.randint(1,10)
         elif self.current_location == 'dairy':
             newx = OFS + TILE_SIZE * np.random.randint(6,7)
             newy = OFS + TILE_SIZE * np.random.randint(1,10)
         frame[newy:newy+TILE_SIZE, newx:newx+TILE_SIZE] = self.image

         # if self.tmap.contents[newy][newx] != '#':
         #     self.x = newx
         #     self.y = newy

    def __repr__(self):                     # returns where the customer is drwan, if no errors occur
        return f'''is in location {self.current_location}'''

class Ghost:

    def __init__(self, tmap, image, x, y): # how its position on the map cn be definedwhen the calss is instantiated
         self.tmap = tmap
         self.image = image
         self.x = x
         self.y = y

    def draw(self, frame):              # puts the ghost-object onto the map
        xpos = OFS + self.x * TILE_SIZE
        ypos = OFS + self.y * TILE_SIZE
        frame[ypos:ypos+TILE_SIZE, xpos:xpos+TILE_SIZE] = self.image

    def move(self, direction):
        newx = self.x
        newy = self.y
        newy += random.randint(-1, 1)
        newx += random.randint(-1, 1)

        if self.tmap.contents[newy][newx] != '#':    #if statement allows customers to move only on dots, not on # in the MARKET
            self.x = newx                             # changed inorder not to be able to moveon #, but yet onto groceries
            self.y = newy

background = np.zeros((700, 1000, 3), np.uint8)  # not sure what this does
tiles = cv2.imread('better_tiles.png')                 # calls the empty supermarket image (which has to be in the same folder as the script)

# takes the position and thereby one of the different images from  the tiles.png


customer_image = tiles[-2*TILE_SIZE:-1*TILE_SIZE,:1*TILE_SIZE]  # this one gives a ghost
customer_image2 = tiles[3*TILE_SIZE:4*TILE_SIZE,1*TILE_SIZE:2*TILE_SIZE]

possible_locations = ['dairy', 'drinks', 'fruits', 'spices']

tmap = TiledMap(MARKET, tiles)

c = Customer(tmap,customer_image2, 15,10,'spices')
g = Ghost(tmap,customer_image, 12,9)


# infinite loop to refresh the frame with supermarket and customers on
while True:
    frame = background.copy()
    tmap.draw(frame)

    #c.draw(frame)
    c.change_location()

    g.move(frame)
    g.draw(frame)

    cv2.imshow('frame', frame)

    key = chr(cv2.waitKey(1) & 0xFF) # key-settings allow to interact with the frame, exert movement based on the 'PC-gaming keys: wasd', use 'q' in the frame to exit
    time.sleep(1)
    if key == 'q':
        break

    # possible_locations = ['Entrance','dairy', 'drinks', 'fruits', 'spices']
    # transition_probabilities = {'Entrance': [0.0, 0.21572721, 0.29645094, 0.36464857, 0.12317328],
    #        'dairy': [0.11788269, 0.74391989, 0.00658083, 0.06437768, 0.06723891],
    #        'drinks': [0.11333659, 0.10649731, 0.61064973, 0.06350757, 0.10600879],
    #        'fruits': [0.20328382, 0.07036747, 0.07271306, 0.60711493, 0.04652072],
    #        'spices': [0.23045603, 0.1490228 , 0.13192182, 0.09934853, 0.38925081]}
    # # print(possible_locations)
    # # print(transition_probabilities)
    # new_location = random.choices(possible_locations, transition_probabilities['spices'])[0]
    # print(new_location)

cv2.destroyAllWindows()
