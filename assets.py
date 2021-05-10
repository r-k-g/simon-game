import os

from fltk import *
from pygame import mixer


# Don't seem to need this in pygame 2
# mixer.pre_init(44100, -16, 1, 1024)
mixer.init()

# Used with os.path.join for cross platform paths
ASSETPATH = 'Assets'

# Load the sounds
BUT_SOUNDS = [mixer.Sound(os.path.join(ASSETPATH, f'sound{i}.wav')) for i in range(1, 5)]
WA_SOUND = mixer.Sound(os.path.join(ASSETPATH, 'WA.wav'))

# Load the images
OFF_IMGS = [Fl_PNG_Image(os.path.join(ASSETPATH, f'{i}_hover_off.png')) for i in range(4)]
ON_IMGS = [Fl_PNG_Image(os.path.join(ASSETPATH, f'{i}_hover_on.png')) for i in range(4)]

CENTER_IMG = Fl_PNG_Image(os.path.join(ASSETPATH, f'center.png'))
DOWN_CENTER_IMG = Fl_PNG_Image(os.path.join(ASSETPATH, f'down_center.png'))