from fltk import *

from assets import *

class GameButton(Fl_Button):
    """A subclass of Fl_Button customized specifically to be the main
    buttons in the game Simon.
    
    Main differences include custom hit detection, hardcoded images
    and interactions with SimonGame window.

    """

    def __init__(self, x, y, w, h, center, in_radius, number, parentwin):
        """Initialize an instance.
        
        It is assumed that size passed is a square, and both dimensions
        are the same as the radius of the circle in the image. 

        "in_radius" argument refers to the space in the center of the circle
        that should not register clicks.

        "number" argument is the number of the button among
        the group (0-3 left-right, top-bottom).
        """

        super().__init__(x, y, w, h)
        
        # For determining valid clicks
        self.center = center
        self.radius = w
        
        self.in_radius = in_radius
        self.in_ratio = self.in_radius / w
        
        self.OFF_IMG = OFF_IMGS[number]
        self.ON_IMG = ON_IMGS[number]
        self.cur_img = self.OFF_IMG

        self.sound = BUT_SOUNDS[number]
        
        self.parentwin = parentwin
        
        self.number = number
        
        self.on = False

        self.box(FL_NO_BOX)
        self.clear_visible_focus()
    
    def handle(self, event):
        """Extend Fl_Button handle to add custom circle-based hit detection."""

        ret = super().handle(event)
        
        x, y, = Fl.event_x(), Fl.event_y()

        if event is FL_PUSH and Fl.event_button1():
            x, y, = Fl.event_x(), Fl.event_y()

            if not self.point_inside(x, y):
                return 0
            
            self.manual_click()
            ret = 1
            
        elif event == FL_RELEASE and self.on:
            self.but_off(manual=True)
            ret = 1

        return ret
    
    def point_inside(self, x, y):
        """Return if a given point is inside the valid button area."""

        c_x, c_y = self.getcorner() 

        # Good ol pythagorean theorem to get distance between inside corner and click
        dist = (((c_x - x) **2) + ((c_y - y) **2)) **0.5

        return self.in_radius < dist < self.radius

    def getcorner(self):
        """Return the x and y of the corner that is in the center of the circle."""

        x = self.x() + (self.w() * self.center[0])
        y = self.y() + (self.h() * self.center[1])
        return x, y 

    def draw(self):
        """Extend Fl_Button draw to resize image."""
        self.update_img()
        super().draw()

    def update_img(self):
        """Resize current image to button dimensions, and adjust variables
        for hit detection accordingly."""

        self.image(self.cur_img.copy(self.w(), self.h()))
        self.radius = self.w()
        self.in_radius = self.w() * self.in_ratio
        self.redraw()

    def auto_click(self, duration):
        """Hold down as if clicked for duration seconds."""

        self.on = True
        self.cur_img = self.ON_IMG
        self.update_img()
        
        self.sound.stop()

        self.sound.play(-1)

        # Stop click after duration seconds
        Fl.remove_timeout(self.but_off)
        Fl.add_timeout(duration, self.but_off)

    def but_off(self, manual=False):
        """Turn the button off.
        
        Manual is whether scheduled or from user releasing mouse.
        """

        self.on = False

        self.cur_img = self.OFF_IMG
        self.update_img()
        
        # Stop the current sound
        if WA_SOUND.get_num_channels():
            WA_SOUND.fadeout(45)
        else:
            self.sound.fadeout(45)
        
        # Send the click to answer checking if the user did it
        if manual:
            self.parentwin.player_ans(self.number)

    def manual_click(self):
        """Turn the button on, changing the image and starting the sound."""

        self.on = True
        self.cur_img = self.ON_IMG

        # Don't send answer to checking, but play error sound if it's wrong
        if self.parentwin.is_correct(self.number):
            self.sound.play(-1)
        else:
            WA_SOUND.play(-1)
            
        self.update_img()


class But_Group(Fl_Group):
    """A subclass of Fl_Group to contain game buttons and ensure proper resizing.
    
    When the widget is drawn, it is resized to stay a centered square
    of maximum size for the window.

    """

    def __init__(self, x, y, w, h, parent):
        """Initialize an instance.
        
        "parent" argument is a reference to the SimonGame window.
        """
        
        super().__init__(x, y, w, h)
        self.parentwin = parent
    
    def draw(self):
        """Extend Fl_Group.draw to resize correctly."""

        self.handle_resize()
        super().draw()
        
    def handle_resize(self):
        """Resize and reposition according to window size."""

        w, h = self.parentwin.w(), self.parentwin.h()
        if (w, h) != self.parentwin.lastsize: # Dimensions changed
            
            # Find the smallest dimension, that's the contraint
            # Then -80 to account for 40 px margins on each side
            dim = min(w, h - 30) - 80

            x = (w//2) - (dim//2)
            y = 30 + ((h - 30)//2) - (dim//2)
            
            self.resize(x, y, dim, dim)

        self.parentwin.lastsize = (w, h)


class StartButton(Fl_Button):
    """Specific button in the center to start a game of Simon."""

    def __init__(self, x, y, w, h, parentwin):
        """Initialize an instance.
        
        "parentwin" arg is a reference to a SimonGame window.
        """

        super().__init__(x, y, w, h)

        self.img = CENTER_IMG
        self.downimg = DOWN_CENTER_IMG
        self.cur_img = self.img

        self.parentwin = parentwin

        self.box(FL_NO_BOX)
        self.clear_visible_focus()

    def update_img(self):
        """Change image to current size.
        
        Width and height will always be proportional.
        """

        self.image(self.cur_img.copy(self.w(), self.h()))
    
    def draw(self):
        """Extend Fl_Button.draw to resize image."""

        self.update_img()
        super().draw()
    
    def handle(self, event):
        """Extend Fl_Button.handle to change image with mouse state.

        Also starts game.
        """

        ret = super().handle(event)

        if event is FL_PUSH:
            self.cur_img = self.downimg
            self.update_img()

        if event is FL_RELEASE:
            self.cur_img = self.img
            self.update_img()

            if Fl.event_inside(self):
                self.parentwin.new_game(0)
        
        return ret