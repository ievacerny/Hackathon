"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # Color mappings from string to RGB value
        self.colormap = {'red':[1.0, 0.0, 0.0],'green':[0.0, 1.0, 0.0],'blue':[0.0, 0.0, 1.0],'black':[0.0, 0.0, 0.0], 'white':[1.0, 1.0, 1.0]}
        
        #Display variables
        self.right_offset = 42
        self.top_offset = 20
        self.bottom_offset = 70
        self.left_offset = 80
        self.panel_height = 40
        self.signal_height = 30
        self.signal_color = 'black'
        self.origin_x = 80
        self.origin_y = 60
        self.grid_small_interval = 10
        self.grid_big_interval = 100
        #self.grid_big_value = self.grid_small_interval*(self.grid_big_interval/self.grid_small_interval)
        self.grid_big_value = 20

        #Device variables - TODO - use actual devices 
        self.devices = [["CLOCK", "clock1"], ["NAND", "nand1"], ["DTYPE","dtype1"]]
        self.monitor_devices = [True, True, True] 



    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

    def render(self, text):
        """Handle all drawing operations."""
        size = self.GetClientSize()

        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        #-----------------------------------------------------------------------

        # Draw a sample signal trace
        # GL.glColor4f(0.0, 0.0, 1.0, 1.0)  # signal trace is blue
        # GL.glBegin(GL.GL_LINE_STRIP)
        # for i in range(10):
        #     x = (i * 20) + 80
        #     x_next = (i * 20) + 100
        #     if i % 2 == 0:
        #         y = 75
        #     else:
        #         y = 100
        #     GL.glVertex2f(x, y)
        #     GL.glVertex2f(x_next, y)
        # GL.glEnd()


        #Draw main frame lines
        self.render_line_strip([[self.origin_x, self.origin_y],[size.width-self.right_offset, self.origin_y]],'black') #horizontal line
        self.render_line_strip([[self.origin_x, self.origin_y],[self.origin_x, size.height-self.top_offset]],'black') #vertical line

        #Draw grid markers
        for x in range(self.origin_x,size.width-self.right_offset+1,self.grid_small_interval):
            if (x-self.origin_x)%self.grid_big_interval == 0:
                self.render_line_strip([[x,self.origin_y],[x,self.origin_y-10]],'black') #draw a longer line for large intervals
                self.render_text(str(int(self.grid_big_value*(x-self.origin_x)/(self.grid_big_interval))),x-10,self.origin_y-25,'black') #also show value at large intervals
            else:
                self.render_line_strip([[x,self.origin_y],[x,self.origin_y-5]],'black')


        #Draw device output only if it is being monitored
        num_monitors = 0 #to keep track of number of devices that are being monitored/rendered 
        for index, monitor in enumerate(self.monitor_devices): 
            if monitor: #if device is being monitored
                device_to_monitor = self.devices[index] 
                self.render_device(num_monitors, device_to_monitor[0], device_to_monitor[1]) #first argument of render_device is the number of devices presently being monitored
                num_monitors += 1 

        #-----------------------------------------------------------------------

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, color):
        """
        Handle text drawing operations.
        mm2121: Modified to accept color as an argument in the form of a list of r, g and b values
        		Can also be a string such as 'red', 'white', etc.
        """
        if isinstance(color,str):
            color = self.colormap[color]

        GL.glColor4f(color[0], color[1], color[2], 1.0)
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def render_line_strip(self, vertices, color):
        if isinstance(color,str):
            color = self.colormap[color]

        GL.glColor4f(color[0], color[1], color[2], 1.0)
        for index in range(len(vertices)-1):
            vertex = vertices[index]
            next_vertex = vertices[index+1]
            x = vertex[0]
            y = vertex[1]
            x_next = next_vertex[0]
            y_next = next_vertex[1]
            GL.glBegin(GL.GL_LINE_STRIP)
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y_next)
        GL.glEnd()

    def render_rectangle(self, corner, height, width, color, opacity): 
        #corner: list of x and y coordinates of bottom left corner
        if isinstance(color,str):
            color = self.colormap[color]

        GL.glColor4f(color[0], color[1], color[2], opacity)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(corner[0], corner[1])
        GL.glVertex2f(corner[0]+width, corner[1])
        GL.glVertex2f(corner[0]+width, corner[1]+height)
        GL.glVertex2f(corner[0], corner[1]+height)
        GL.glEnd()

    def render_signal(self, corner_y, bits):
        size = self.GetClientSize()
        x_prev = self.origin_x 
        x_interval = self.grid_small_interval*10/self.grid_big_value
        x_max = size.width - self.left_offset - self.right_offset
        y_base = corner_y + 5
        y_prev = y_base

        for index, bit in enumerate(bits):
            if x_prev >= x_max:
                break
            y = y_base + bit*self.signal_height
            self.render_line_strip([[x_prev,y_prev],[x_prev,y]],'black')
            self.render_line_strip([[x_prev,y],[x_prev + x_interval,y]],'black')
            x_prev = x_prev + x_interval
            y_prev = y

    def render_device(self, num_monitored, device_type, device_name):
        #num_monitored: number of devices that have been monitored/rendered upto now 
        #device_type: CLOCK, NAND, DTYPE, etc. 

        corner_x = self.left_offset
        corner_y = self.bottom_offset + (self.panel_height+5)*(num_monitored)
        size = self.GetClientSize()

        if device_type == 'CLOCK':
            color = 'green'
        elif device_type == 'DTYPE':
            color = 'blue'
        else:
            color = 'red'

        self.render_rectangle([corner_x, corner_y], self.panel_height, size.width - corner_x - self.right_offset, color, 0.2) #draw colored panel behind signal
        self.render_text(device_name, 40, corner_y + 15, 'black') #render device name using render_text to the left of this panel
        self.render_signal(corner_y, [0,0,0,1,1,0,1,0])
        #TODO render signal
    




class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "100")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.add_monitor_name = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)
        self.add_monitor = wx.Button(self, wx.ID_ANY, "Add Monitor")
        self.remove_monitor_name = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)
        self.remove_monitor = wx.Button(self, wx.ID_ANY, "Remove Monitor")

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.add_monitor_name.Bind(wx.EVT_TEXT_ENTER, self.on_add_monitor_name)
        self.add_monitor.Bind(wx.EVT_BUTTON, self.on_add_monitor)
        self.remove_monitor_name.Bind(wx.EVT_TEXT_ENTER, self.on_remove_monitor_name)
        self.remove_monitor.Bind(wx.EVT_BUTTON, self.on_remove_monitor)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        side_sizer.Add(self.add_monitor_name, 1, wx.ALL, 5)
        side_sizer.Add(self.add_monitor, 1, wx.ALL, 5)
        side_sizer.Add(self.remove_monitor_name, 1, wx.ALL, 5)
        side_sizer.Add(self.remove_monitor, 1, wx.ALL, 5)

        self.SetSizeHints(300, 300)
        self.SetSizer(main_sizer)


    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        if spin_value > 0: #only update if nonzero value entered
            self.canvas.grid_big_value = spin_value/5 
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        if self.run_button.GetLabel()=="Run":
        	self.run_button.SetLabel("Pause")
        	#TODO actually pause the simulation:


        else:	
            self.run_button.SetLabel("Run")
        	# TODO actually run the simulation

        text = "Run button pressed."
        self.canvas.render(text)

    def on_add_monitor_name(self, event):
        text_box_value = self.add_monitor_name.GetValue()
        #maybe print out to command line?

    def on_add_monitor(self, event):
        monitor_name = self.add_monitor_name.GetValue()
        for index, val in enumerate(self.canvas.devices):
            if val[1] == monitor_name:
                self.canvas.monitor_devices[index] = True   
        #TODO - update monitor class
        #self.canvas.monitor_devices[-1] = True
        #print('Hello')

    def on_remove_monitor_name(self, event):
        text_box_value = self.remove_monitor_name.GetValue()
        #maybe print out to command line?

    def on_remove_monitor(self, event):
        monitor_name = self.remove_monitor_name.GetValue()
        for index, val in enumerate(self.canvas.devices):
            if val[1] == monitor_name:
                self.canvas.monitor_devices[index] = False
        #TODO - update monitor class
        #self.canvas.monitor_devices[-1] = False
        #print('Goodbye')

   
    #     """Handle the event when the user enters text."""
    #     text_box_value = self.text_box.GetValue()
    #     text = "".join(["New text box value: ", text_box_value])
    #     self.canvas.render(text)


