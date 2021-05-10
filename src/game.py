from datetime import datetime
import pickle
from random import randint

from fltk import *

from assets import *
from buttons import But_Group, GameButton, StartButton
from scores import Scorewin, Score



class SimonGame(Fl_Double_Window):
    """An approximate digital recreaction of the 1978 game "Simon" by Milton Bradley.
    
    Games can theoretically go on infinitely, and the scores are saved.

    """

    def __init__(self, w, h, title='Simon'):
        """Initialize an instance.
        
        Width (w) and height (h) arguments should not be less than 180 and
        210 respectively.

        """

        super().__init__(w, h, title)

        # Load scores or create file if necessary
        try:
            with open('.scores.pickle', 'rb') as f:
                self.scores = pickle.load(f)
              
        except FileNotFoundError:
            self.scores = [Score(),]
            self.save_scores()

        self.color(FL_BLACK)
        self.lastsize = (self.w(), self.h())
        
        # For keeping track of the sequence, and what the player has entered
        self.sequence = list()
        self.player_seq = list()
        
        # Initial timing for autoplayed notes in sequence, reset in self.stop()
        self.duration = 0.42
        self.interval = 0.08

        self.begin()
        
        menuitems = (
            ('Game', 0, 0, 0, FL_SUBMENU),
                ('New Game', FL_F + 1, self.new_game),
                ('Stop Game', FL_CTRL + ord('x'), self.stop_game, 0, FL_MENU_DIVIDER),
                ('Scores...', FL_CTRL + ord('s'), self.view_scores),
                (None, 0)
        )
        
        # Position menu slightly off screen to only show bottom edge of box
        self.menubar = Fl_Menu_Bar(-1, -1, w+2, 31)
        self.menubar.box(FL_BORDER_BOX)
        self.menubar.color(FL_WHITE)
        self.menubar.copy(menuitems)

        # A bit of math to figure out initial positioning of game in window
        # Minimum distance between group and win edges is 40
        dim = min(w, h - 30) - 80
        x = (w//2) - (dim//2)
        y = 30 + ((h - 30)//2) - (dim//2)

        self.but_group = But_Group(x, y, dim, dim, self)
        self.but_group.begin()
        
        # Figure out position of start button in center
        center_x = round(40 + (w//2 - 40) * 0.625)
        center_y = round(70 + ((h-30)//2 - 40) * 0.625)
        center_w = round(((w//2 - 40) * 0.375) * 2)
        self.start_but = StartButton(center_x, center_y, center_w, center_w, self)

        self.gamebuttons = list()

        # Create main buttons for gameplay
        corners = [(0, 0), (1, 0), (0, 1), (1, 1)]
        for i in range(4):
            corner = corners[i]

            # do this outside of gamebutton args to avoid crazy long line
            b_x = 40 + (w//2 - 40) * corner[0]
            b_y = 70 + ((h-30)//2 - 40) * corner[1]
            b_w = w//2 - 40
            b_h = (h-30)//2 - 40

            # Corner for figuring out position vs corner passed for detecting clicks are opposites
            self.gamebuttons.append(GameButton(b_x, b_y, b_w, b_h, corners[::-1][i], (w//2 - 40) * 0.4, i, self))

        self.but_group.end()
        
        self.end()
        self.resizable(self.but_group)
        
        # Buttons are deactivated untill user starts game
        self.deactivate_buts()

    def new_game(self, wid, data=None):
        """Reset current game if active and start a new one."""
        
        self.stop_game(0)

        # Slight delay for improved UX
        Fl.add_timeout(0.3, self.play_seq)
        
    def stop_game(self, wid, data=None):
        """Stop current game if active and reset."""
        
        # Stop game
        self.all_off()
        self.remove_timeouts()
        self.deactivate_buts()

        # Reset variables
        self.sequence.clear()
        self.player_seq.clear()
        
        self.duration = 0.46
        self.interval = 0.108
    
    def gameover(self, timeout=False):
        """Stop the game and display score windows."""

        # -1 to not include failed level
        points = max(len(self.sequence) - 1, 0)

        self.stop_game(0)
        
        if timeout:
            self.play_error_sound()

        # Remove default blank score if it's there
        for s in self.scores.copy():
            if s.date == 'N/A':
                self.scores.remove(s)

        # Add new score to list of scores
        name = fl_input(f'GAME OVER - SCORE {points}\nEnter your name:', 'Anonymous')
        date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        if name is not None:
            score = Score(points, name or 'Anonymous', date)
            self.scores.append(score)
            self.scores.sort(key=lambda s: s.value, reverse=True)

            self.view_scores(0, self.scores.index(score) + 2)
        
        # User pressed cancel or escaped/closed, give them a chance to save score
        else:
            # Don't ask for confirmation if it's a low score
            if points > 2:
                choice = fl_choice(f'Are you sure you want to throw out your score of {points}?',
                                     'Yes', 'No', None)

                if not choice or choice is None: # Clicked yes or closed/escaped
                    # Add back that default score
                    self.scores.append(Score())
                    self.view_scores(0)
                
                else: # Clicked no, save score
                    name = fl_input('LAST CHANCE!\nEnter your name:', 'Anonymous')
                    score = Score(points, name or 'Anonymous', date)
                    self.scores.append(score)
                    self.scores.sort(key=lambda s: s.value, reverse=True)

                    self.view_scores(0, self.scores.index(score) + 2)
            
            else:
                self.view_scores(0)
        
    def play_error_sound(self, stop=False):
        """Play the error sound for a set amount of time, then stop it.
        
        Use to play sound when the game ends from a timeout, so that there
        is still a audible loss.
        """

        if stop:
            WA_SOUND.stop()
        else:
            WA_SOUND.play(-1)
            Fl.add_timeout(1.3, self.play_error_sound, True)
        
    def play_seq(self):
        """Add a random button to the sequence and play it.
        
        Once the sequence has played, begin the players turn.
        """
        
        self.deactivate_buts()
        
        # Add one random button number to sequence
        self.sequence.append(randint(0, 3))

        # Speed up playback by set amounts at set points in the game
        if len(self.sequence) == 6:
            self.duration = 0.36
            self.interval = 0.108
        elif len(self.sequence) == 14:
            self.duration = 0.26
            self.interval = 0.108
        
        # Add timeouts for the whole sequence at once
        for b in range(len(self.sequence)):
            # Time until next button is duration + interval so that 
            # there is a gap between playing buttons
            total_time = (self.duration * b) + (self.interval * b)
            Fl.add_timeout(total_time, self.gamebuttons[self.sequence[b]].auto_click, self.duration)
        
        # Schedule starting the players turn for when the sequence is done
        self.player_seq.clear()
        seq_time = (self.duration * len(self.sequence)) + (self.interval * len(self.sequence))
        Fl.add_timeout(seq_time, self.activate_buts)

        # Start a countdown so that doing nothing after the turn starts ends game
        Fl.add_timeout(seq_time + 5, self.gameover, True)
   
    def player_ans(self, ans):
        """Receive a button click and check validity, respond accordingly."""

        # Received a click, don't end game because of timeout
        Fl.remove_timeout(self.gameover)
            
        # Check validity of click
        if self.is_correct(ans):
            self.player_seq.append(ans)
            
            # Sequence completed, play next sequence
            if len(self.player_seq) == len(self.sequence): 
                
                self.deactivate_buts()

                # Brief delay before playing sequence because it sounds nicer
                Fl.add_timeout(0.5, self.play_seq)
            
            else:
                # Start another 5 second time limit to click next button
                Fl.add_timeout(5, self.gameover, True)
        
        else: # End the game if it's not part of the sequence
            self.gameover()

    def is_correct(self, ans):
        """Check for valid answer without adding to player sequence.
        
        Don't add to the sequence so that this can be called multiple times
        per button, and detect wrong answers before a button is released.
        """
        
        seq = self.player_seq.copy()
        seq.append(ans)
        return seq[-1] == self.sequence[len(seq) - 1]
        
    def remove_timeouts(self):
        """Stop most active timeouts.
        
        Some of these probably don't need to be stopped but I was getting
        errors so I figured it doesn't hurt.
        """

        Fl.remove_timeout(self.play_seq)
        Fl.remove_timeout(self.gameover)
        Fl.remove_timeout(self.activate_buts)
        for b in self.gamebuttons:
            Fl.remove_timeout(b.auto_click)

    def view_scores(self, wid, score=None):
        """Create popup window with all previous scores.
        
        Optional score argument specifies an item to select upon creating
        the browser. 1 based but essentially 2 based because the first
        item is the column headers.
        """
        s_win = Scorewin(self, score)

    def save_scores(self):
        """Save score list to a file."""

        with open('.scores.pickle', 'wb') as f:
            pickle.dump(self.scores, f)

    def update_imgs(self):
        """Update resizing of all images according to window size."""

        for b in self.gamebuttons:
            b.update_img()
        self.start_but.update_img()

    def deactivate_buts(self):
        """Deactivate all four game buttons."""

        for b in self.gamebuttons:
            b.deactivate()
    
    def activate_buts(self):
        """Activate all four game buttons."""

        for b in self.gamebuttons:
            b.activate()
    
    def all_off(self):
        """Turn off all the buttons, stopping light and sound."""

        for b in self.gamebuttons:
            b.but_off()

    def hide(self):
        """Extend Fl_Window hide to save score before closing."""
        
        self.save_scores()
        super().hide()