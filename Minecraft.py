from ursina.prefabs.first_person_controller import FirstPersonController # first person controller prefab
from ursina import* # import all ursina functions
import ursina, time # import ursina modules and time module

# instance of ursina application
app = Ursina()

# initialize variables
player_enabled = True # checks if player is enabled
p_key_held = False # checks if 'p' key is pressed
original_world = [] # list to hold original world blocks incase of resetting
world_size = 20 # size of world in x and y dimensions
world_depth = 5 # depth of world in z dimension

# load textures for different block types
grass_texture = load_texture('assets/grass_block2.png')
stone_texture = load_texture('assets/stone_block2.png')
wood_texture = load_texture('assets/wood_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')
sky_texture = load_texture('assets/skybox.png')
arm_texture = load_texture('assets/arm_texture2.png')
punch_sound = Audio('assets/punch_sound', loop=False, autoplay=False)
block_pick = 1 # initial block picking variable for the block type

# window setings
window.title = "Minecraft | Julien Okumu"
window.fps_counter.enabled = False
window.exit_button.visible = True

# function to show a popup message on the screen
def show_popup(text):
    global popup_text 
    popup_text = Text(text=text, origin=(0, 0), scale=2, color=color.black) # text entity for popup
    popup_text.x = -popup_text.width / 2 # center popup horizontally
    popup_text.y = -popup_text.height / 2 # center popup vertically

# function to hide popup message
def hide_popup():
    global popup_text
    destroy(popup_text) # destroy popup text entity

# function to reset game world
def reset_game():
    show_popup("Recreated World Blocks!") # show popup message

    # disable all current voxel entities in the scene
    for voxel in scene.entities:
        if isinstance(voxel, Voxel): # check if entity is a voxel
            voxel.disable() # disable the voxel

        
    # recreate the original world blocks from the stored original_world list
    for x, y, z, texture in original_world:
        voxel = Voxel(position=(x, y, z), texture=texture) # create a new voxel with the original texture at the specified position

    player.position = (12, 4, 12) # reset the players position
    invoke(hide_popup, delay=4) # hide popup after a delay of 4 seconds

# fucntion to toggle the visibility of the player
def toggle_player_visibility():
    global player_enabled
    player_enabled = not player_enabled # toggle the player_enabled state
    player.enabled = player_enabled # set players state based on the toggle

# update the function called every frame
def update():
    global block_pick 
    global p_key_held

    # check if player has fallen off the edge of the world
    if player.y < -10: # if player's y position is less than -10
        reset_game()

    # check if the 'r' key is held down to reset the game
    if held_keys['r']:
        reset_game()

    # check for player visibility toggle with the 'p' key
    if held_keys['p'] and not p_key_held: # if 'p' was pressed and not previously held
        toggle_player_visibility()
        p_key_held = True # set p_key_held to True to indicate the key is held down
    elif not held_keys['p'] and p_key_held: # if 'p' is not pressed and was previously held
        p_key_held = False # set p_key_held to False to indicate the key is released

    # check if left or right mouse button is held down to activate the hand
    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()

    # block selection controls
    if held_keys['1']: block_pick = 1
    if held_keys['2']: block_pick = 2
    if held_keys['3']: block_pick = 3
    if held_keys['4']: block_pick = 4
    if held_keys['5']: block_pick = 5

    # custom movement controls
    move_speed = 5 * time.dt # calculate movement speed based on delta time

    # calculate forward movemenr direction based on player's rotation
    forward_direction = player.forward * move_speed # get the forward direction vector scaled by move speed

    # move player based on arrow key
    if held_keys['up arrow']: 
        player.position += forward_direction
    if held_keys['down arrow']:
        player.positon -= forward_direction

    # jumping control
    if held_keys['space']:
        player.y += move_speed # move player upward


# voxel class definition for creating block entities
class Voxel(Button): # inherit from button class to make voxel interactive
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__( # parent class constructor
            parent=scene, # set parent to scene
            position=position, # position of voxel
            model='assets/block', # model for voxel
            origin_y=0.5, # origin point for voxel
            texture=texture, # texture for voxel
            color=color.hsv(0, 0, 1), # set color of voxel
            scale=0.5 # scale for voxel
        )
        self.default_color = self.color # store default color for mouse exit event

    def on_mouse_enter(self): # called when mouse enters the voxel
        self.color = color.hsv(19, 0.03, 0.7) # change color on mouse enter

    def on_mouse_exit(self): # called when mouse exits voxel
        self.color = self.default_color # reset color to default

    def input(self, key): # method to handle input events
        if key == 'escape':
            application.quit()

        if self.hovered: # if mouse is hovering over the voxel
            if key == 'right mouse down': # if the right mouse is pressed
                punch_sound.play() # play punch sound
                # create a new voxel based on selected block type
                if block_pick == 1: voxel = Voxel(position=self.position + mouse.normal, texture=grass_texture)
                if block_pick == 2: voxel = Voxel(position=self.position + mouse.normal, texture=stone_texture)
                if block_pick == 3: voxel = Voxel(position=self.position + mouse.normal, texture=brick_texture)
                if block_pick == 4: voxel = Voxel(position=self.position + mouse.normal, texture=dirt_texture)
                if block_pick == 5: voxel = Voxel(position=self.position + mouse.normal, texture=wood_texture)

            if key == 'left mouse down':
                punch_sound.play()
                destroy(self) # destroy current voxel

# non-interactive button class definition
class NonInteractiveButton(Button): 
    def __init__(self, **kwargs): # constructor with keyword arguments
        super().__init__(**kwargs) # parent class with provided arguments
        self.highlight_color = self.color
        self.collision = False # disable collision for this button

# table UI class definition for creating a UI table
class TableUI(Entity): # inherit from entity class
    def __init__(self):
        super().__init__(parent=camera.ui) # set parent to the camera's UI

        cell_size = 0.08 # size of each cell in the table UI
        spacing = 0.02 # spacing between cells

        self.cells = [] # initialize a list to store the cells of the table
        for i in range(9): # loop to create 9 cells
            if i <= 4: # for the first 5 cells
                cell = NonInteractiveButton(
                    parent=self, # set parent to this table UI
                    model='quad',
                    color=color.rgba(1, 1, 1, 0.9), # set color with some transparency
                    texture=["assets/grass3d.png", "assets/Stone3d.png", "assets/Brick3d.png", "assets/Dirt3d.png", "assets/plank3d.png"][i], # set texture based on index
                    border=0.02, # set border size
                    scale=(cell_size, cell_size), # set scale of cell
                    origin=(-0.5, 0), # set origin point for positioning
                    position=(-0.43 + i * (cell_size + spacing), -0.42) # calculate position of the cell
                )
                text_entity = Text(
                    parent=cell, # set the parent to the cell
                    text=str(i + 1), # set the text to the cell number
                    position=(0, -0.3) # position the text relative
                )
                self.cells.append(cell) # add the cell to the cells list

# sky class definition for creating a sky entity
class Sky(Entity): # inherit from entity class
    def __init__(self): # constructor for sky
        super().__init__(
            parent=scene,
            model='sphere',
            texture=sky_texture,
            scale=150, # scale the sky to cover the scene
            double_sided=True # enabled double-sided rendering for the sky
        )

# hand class
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui, # set parent to camera's UI
            model='assets/arm',
            texture=arm_texture,
            scale=0.2,
            rotation=Vec3(150, -10, 0), # set rotation of the hand
            position=Vec2(0.4, -0.6) # set position of the hand 
        )

    def activate(self): # method to set hand to active state
        self.position = Vec2(0.3, -0.5) # move hands position when active

    def passive(self): # method to set the hand to passive state
        self.position = Vec2(0.4, -0.6) # reset hands position when not active

# loop tp create the initial world of voxels
for z in range(world_size): # loop through z-axis
    for x in range(world_size): # loop through x-axis
        for y in range(world_depth): # loop through y-axis
            if y == 4: # if current y level is 4
                voxel = Voxel(position=(x, y, z), texture=grass_texture) # grass voxel
                original_world.append((x, y, z, grass_texture)) # store the voxels position and texture
            elif y == 0: # if current y level is 0
                voxel = Voxel(position=(x, y, z), texture=stone_texture) # create a stone voxel
                original_world.append((x, y, z, stone_texture))
            else: # for all other y levels
                voxel = Voxel(position=(x, y, z), texture=dirt_texture) # creata dirt voxel
                original_world.append((x, y, z, dirt_texture))

# create player with fps controller
player = FirstPersonController(position=(12, 15, 12))

# table UI
table = TableUI()

# sky entity
sky = Sky()

# hand entity for the player
hand = Hand()

window.fullscreen = False

app.run()