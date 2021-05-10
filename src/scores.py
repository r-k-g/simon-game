from fltk import *

class Score:
    """Sinple data structure to represent a single score."""

    def __init__(self, value=0, name='N/A', date='N/A'):
        """Initialize an instance."""

        self.value = value
        self.name = name
        self.date = date
     
    def __repr__(self):
        """For debugging."""
        return f'Score([{self.value}, {self.name}, {self.date}])'


class Scorewin(Fl_Double_Window):
    """Popup type window to display all scores from SimonGame."""

    def __init__(self, parentwin, score, w=450, h=340, title='Scores'):
        """Initialize an instance.
        
        "parentwin" arg is a reference to a SimonGame window.

        "score" arg is a 2-based index of the score to highlight upon opening,
        but can also be None to not highlight any score. 
        """

        super().__init__(w, h, title)
        
        # Make this a popup window, must be closed before interacting below
        self.set_modal()

        self.parentwin = parentwin

        labelbox = Fl_Box(20, 7, 78, 20, 'All scores:')
        labelbox.align(FL_ALIGN_LEFT|FL_ALIGN_INSIDE)
        labelbox.box(FL_FLAT_BOX)

        # Use format characters to change text & bg colour + make bold
        self.columnnames = '@B8@C7@b@.SCORE\t@B8@C7@b@.NAME\t@B8@C7@b@.DATE'
        
        widths = (70, 110, 100, 0)
        self.score_brows = Col_Resize_Browser(20, 30, w-40, h-70)
        self.score_brows.callback(self.brows_cb)
        # Required for Col_Resize_Browser, maybe not pythonic but it's not really my logic
        self.score_brows.widths = list(widths[:-1])
        
        # Create columns
        self.score_brows.column_widths(widths)
        self.add_scores()
        
        # Select score and move on screen if specified
        if score is not None:
            self.score_brows.value(score)
            self.score_brows.middleline(score)
        
        # Set up context menu
        popup_items = (
            ('Remove Score    ', FL_Delete, self.remove_score),
            (None, 0)
        )
        self.context_menu = Fl_Menu_Button(20, 30, 1, 1)
        self.context_menu.type(Fl_Menu_Button.POPUP3)
        self.context_menu.copy(popup_items)
            
        self.close_but = Fl_Return_Button(w-90, h-32, 70, 24, 'Close')
        self.close_but.callback(self.exit_cb)

        self.reset_but = Fl_Button(w-200, h-32, 100, 24, '&Reset Scores')
        self.reset_but.callback(self.reset_cb)

        self.end()
        self.show()
    
    def add_scores(self):
        """Clear then load scores from parentwin into score browser."""

        self.score_brows.clear()

        self.score_brows.add(self.columnnames)
        for s in self.parentwin.scores:
            # \t indicates columns
            self.score_brows.add(f'{s.value}\t{s.name}\t{s.date}')

    def reset_cb(self, wid):
        """Reset all scores."""

        self.parentwin.scores = [Score(),]
        self.parentwin.save_scores()
        self.add_scores()
    
    def remove_score(self, wid):
        """Attempt to delete a selected score but warn user if it's a decent score."""

        # Get individual items of score
        list_s = self.score_brows.text(self.score_brows.value()).split()
        points, date, name = int(list_s[0]), ' '.join(list_s[-2:]), ' '.join(list_s[1 : -2])
        
        if points > 2: # Warn user if it's a decent score
            message = f'Are you sure you want to delete {name}\'s score of {points} from {date}?'
            choice = fl_choice(message, 'No', 'Yes', None)
        else:
            choice = 1
        
        if choice:
                # Browser index is essentially 2 based because of column titles.
                del self.parentwin.scores[self.score_brows.value() - 2]
                self.score_brows.remove(self.score_brows.value())
                
    def brows_cb(self, wid):
        """Activate popup menu if conditions are correct."""

        if Fl.event_button() == FL_RIGHT_MOUSE:
            # Reactivate items if valid click
            if self.score_brows.value():
                self.context_menu.find_item('Remove Score    ').activate()
            
            else: # Deactivate items if right clicked not on item
                self.context_menu.find_item('Remove Score    ').deactivate()
            self.context_menu.popup()
    
    def exit_cb(self, widget):
        """Close the window."""
        self.hide()


class Col_Resize_Browser(Fl_Hold_Browser):
    """Fl_Hold_Browser with resizing columns.
    
    Logic and most of implementation translated into python from:
        http://seriss.com/people/erco/fltk/#Fl_Resize_Browser

    Differences include Fl_Hold_Browser selecting behavior and top-bottom
    wrapping with arrow keys.

    """

    def __init__(self, x, y, w, h, label=None):
        """Initialize an instance.
        
        All class-specific attributes are not arguments, which I'm
        not sure how I feel about. I guess it prevents super long lines
        when creating instances.
        """

        super().__init__(x, y, w, h, label)
        
        self.colsepcolor = FL_BLACK
        self.showcolsep = True
        self.last_curs = FL_CURSOR_DEFAULT
        self.drag_col = -1
        self.widths = list()
        self.nowidths = list()

        # For wrapping with arrow keys
        self._lastvalue = 0

    def change_cursor(self, newcursor):
        """Change cursor if not already set to specified value."""

        if newcursor == self.last_curs:
            return
        
        self.window().cursor(newcursor)
        
        self.last_curs = newcursor
    
    def bbox(self):
        """Get the inside dimensions of browser not including scorll bars.
        
        Assumes a width of 1 px for the box.
        """

        vert_visible = self.getScrollbar().visible()
        hori_visible = self.getHScrollbar().visible()

        if vert_visible or hori_visible:
            sb_size = Fl.scrollbar_size()

        x = self.x() + 1
        y = self.y() + 1

        w = self.w() - 2 - sb_size if vert_visible else self.w() - 2
        h = self.h() - 2 - sb_size if hori_visible else self.h() - 2

        return x, y, w, h

    def col_near_mouse(self):
        """Return the column the mouse is near or -1 if none."""
        
        x, y, w, h = self.bbox()
        
        # Not inside browser area (eg. on a scrollbar)
        if not Fl.event_inside(x, y, w, h):
            return -1
        
        mousex = Fl.event_x() + self.hposition()
        colx = self.x()
        
        for t in range(len(self.widths) - 1):
            colx += self.widths[t]
            
            diff = mousex - colx
            
            # Return column number if mouse nearby
            if -4 <= diff <= 4:
                return t
        
        return -1
    
    def recalc_hscroll(self):
        """Sync horizontal scrollbar as columns are dragged."""

        vertpos = self.position()
        select = self.value()

        # Changing textsize() triggers recalc of scrollbars
        size = self.textsize()
        self.textsize(size + 1)
        self.textsize(size)

        # It also resets some other stuff so need to set these again
        self.position(vertpos)
        self.value(select)
    
    def handle(self, event):
        """Extend Fl_Browser.handle to manage events for column resizing."""

        # Not entirely sure what the point of this is, if you wanted 
        # this you could just not use this class, but it's in the 
        # original Col_Resize_Browser
        if not self.showcolsep:
            return super().handle(event)
        
        if event == FL_MOVE:
            if self.col_near_mouse() == -1:
                self.change_cursor(FL_CURSOR_DEFAULT)
            else:
                self.change_cursor(FL_CURSOR_WE)
        
        elif event == FL_PUSH:
            col = self.col_near_mouse()
            
            # Start dragging if clicked on resizer
            if col >= 0: 
                self.drag_col = col
                return 1 # Eclipse Fl_Browser handle, don't select item
            
            super().handle(event)
            
            # If clicked on column titles, deselect
            if self.value() == 1:
                self.select(1, 0)
            
            self.do_callback()
            return 1
        
        elif event == FL_DRAG:
            if self.drag_col != -1:
                # Sum up column widths to determine position
                mousex = Fl.event_x() + self.hposition()
                newwidth = mousex - self.x()
                
                for t in range(len(self.widths) - 1):
                    if t >= self.drag_col:
                        break
                    
                    newwidth -= self.widths[t]
                
                if newwidth > 0:
                    self.widths[self.drag_col] = newwidth
                    # Apply new widths and redraw
                    self.column_widths(tuple(self.widths + [0]))
                    self.recalc_hscroll()
                    self.redraw()

                return 1
            
            super().handle(event)

            # If drag selecting onto column titles, deselect
            if self.value() == 1:
                self.select(1, 0)
            return 1

        
        elif event == FL_RELEASE:
            # Exit drag mode
            self.drag_col = -1
            self.change_cursor(FL_CURSOR_DEFAULT)
            return 1

            """Strange thing in original code here:
            if ( e == FL_RELEASE ) return 1;        // eclipse event
                ret = 1;
                break;
            
            But my code seems to be working fine.
            """

        elif event == FL_KEYDOWN:
            if Fl.event_key() == FL_Up and self._lastvalue == 2:
                self.value(self.size())
                self.bottomline(self.value())
                self.do_callback()
                return 1

            elif Fl.event_key() == FL_Down and self._lastvalue == self.size():
                self.value(2)
                self.do_callback()
                return 1
        
        self._lastvalue = self.value()
        
        return super().handle(event)
    
    def draw(self):
        """Extend Fl_Browser.draw to draw column separators."""

        super().draw()
        
        if self.showcolsep:
            # Draw column separators

            colx = self.x() - self.hposition()
            
            # Don't draw over scrollbars
            x, y, w, h = self.bbox()
            
            fl_color(self.colsepcolor)
            
            for t in range(len(self.widths) - 1):
                colx += self.widths[t]
                
                # Only draw if within browser
                if x < colx < (x + w):
                    fl_line(colx, y, colx, y+h-1)
