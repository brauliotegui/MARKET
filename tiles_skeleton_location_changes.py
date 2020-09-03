
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


background = np.zeros((700, 1000, 3), np.uint8)  # not sure what this does
tiles = cv2.imread('tiles.png')                 # calls the empty supermarket image (which has to be in the same folder as the script)

# takes the position and thereby one of the different images from  the tiles.png


customer_image = tiles[-2*TILE_SIZE:-1*TILE_SIZE,:1*TILE_SIZE]  # this one gives a ghost

possible_locations = ['dairy', 'drinks', 'fruits', 'spices']

tmap = TiledMap(MARKET, tiles)

c = Customer(tmap,customer_image, 15,10,'spices')

 # a simple way of increasing the number of (identical looking) customers, to include only one, the shorter version of bunch is used
#bunch = [Customer(tmap, customer_image, 15, 10)]
#bunch = [Customer(tmap, customer_image, 15-np.random.randint(3), 10np.random.randint(3)) for c in range(10)]

# infinite loop to refresh the frame with supermarket and customers on
while True:
    frame = background.copy()
    tmap.draw(frame)

    #c.draw(frame)
    c.change_location()
    # for c in bunch:
    #    c.draw(frame)

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


# sniplets that might  be useful for implementing movement based on locations and transition probabilites, far from working
# Location_class filling with customers
#
# #Option 1:
#         if self.new_state == 'spices':
#             newx = self.spices[np.random.randint(ailse_start,aisle_end)]
#             newy = self.spices[np.random.randint(ailse_start,aisle_end)]
