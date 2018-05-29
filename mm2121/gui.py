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
import time
from math import *

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

    def __init__(self, parent):
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
        self.right_offset = 42 #offset for internal frame from right hand side edge of canvas 
        self.top_offset = 20
        self.bottom_offset = 70
        self.left_offset = 80 
        
        self.panel_height = 40 #height of the panel(translucent rectangle) behind a signal
        self.inter_panel_spacing = 5 #height of vertical spacing between panels
        
        self.signal_height = 30
        self.signal_color = 'black'
        self.signal_above_panel = 5 #height difference between bottom edge of panel and bottom of signal (when signal has zero value)
        
        self.origin_x = 80 #x coordinate of bottom-left corner
        self.origin_y = 60 #y coordinate of ...
        
        self.grid_small_interval = 10 #width of one small mark on the grid
        self.grid_big_interval = 100 #width of one big mark on the grid
        self.grid_big_value = 20 #number of cycles that correspond to one big mark on the grid (changed by wx 'Cycles' button)
        self.grid_hor_text_offset = 10 #how much to the left of the grid marker you draw the value text
        self.grid_vert_text_offset = 25 #how much below the grid line you draw the number to be shown
        self.x_axis_label_offset = 75
        self.y_axis_label_offset = 20

        #Devices, monitors
        self.devices_properties = [] #internal use

        #SYSINTEGRATION - after network execution in the parent (Gui), get the values of monitor outputs and store them locally for rendering (later)
        '''
        self.update_monitors(devices,monitors)
        '''

        #Device variables - TODO - use actual devices 
        self.devices_properties = [["CLOCK", "clock1", [0,2,1,-0.5,0,1,0,1,0,0.5,1,1,-0.5]], ["NAND", "nand1", [0,0.5,1,1,1,1]], ["DTYPE","dtype1.Q", [0,0,0,0.5,1,-0.5]]]
        self.monitor_devices = [True, True, True] #Temporary - eventually just update self.devices_properties
        
        #Simulation control
        self.simulation_mode = False
        self.simulation_timer = 0 #Keep track of time for simulations

        #Windows - decide which window to show 
        self.display_startup = True

        

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

        #print(time.clock())

        #if self.display_startup: #TODO different window before a file is loaded (proper application-style)
            #Display the basic startup screen
            #self.render_rectangle([30,30],100,200,'red',0.5)
        #else:
            #Draw main frame lines

        #TODO - enable startup window

        #Draw basic frame
        self.render_line_strip([[self.origin_x, self.origin_y], [size.width-self.right_offset, self.origin_y]], 'black') #horizontal line
        self.render_line_strip([[self.origin_x, self.origin_y], [self.origin_x, size.height-self.top_offset]], 'black') #vertical line
        self.render_text('Number of cycles', size.width - self.right_offset - self.x_axis_label_offset, 15, 'black')
        self.render_text('Name\n[Type]', self.y_axis_label_offset, size.height - self.top_offset - 10,'black')

        #Draw grid and markers
        for x in range(self.origin_x, size.width-self.right_offset+1, self.grid_small_interval): # +1 so we can draw a grid marker on the last point as well
            if (x-self.origin_x)%self.grid_big_interval == 0:
                self.render_line_strip([[x,self.origin_y], [x,self.origin_y-10]], 'black') #draw a longer line for large intervals
                self.render_text(str(self.grid_big_value*(x-self.origin_x)/(self.grid_big_interval)), x-self.grid_hor_text_offset, self.origin_y-self.grid_vert_text_offset, 'black') #also show value at large intervals
            else:
                self.render_line_strip([[x,self.origin_y], [x,self.origin_y-5]], 'black')

        #Draw device outputs
        for index, device in enumerate(self.devices_properties): #TODO with simple loop over self.devices
            #self.render_device(index, device[0], device[1], device[2], self.play_simulation) #first argument of render_device is the number of devices presently being monitored
            device_type = device[0]
            device_name = device[1]
            device_signal = device[2] #list that takes values in [0,0.5,-0.5,1,2]

            #corner => bottom-left corner 
            corner_x = self.left_offset
            corner_y = self.bottom_offset + (self.panel_height + self.inter_panel_spacing)*(index) #height depends on number of devices that have been rendered upto now, therefore need index value

            if device_type == 'CLOCK':
                color = 'green'
            elif device_type == 'DTYPE':
                color = 'blue'
            else:
                color = 'red'

            self.render_rectangle([corner_x, corner_y], self.panel_height, size.width - corner_x - self.right_offset, color, 0.2) #draw colored panel behind signal
            self.render_text(device_name, self.y_axis_label_offset, corner_y + 25, 'black') #render device name to the left of this panel
            self.render_text("[" + device_type + "]", self.y_axis_label_offset, corner_y + 10, 'black') #render device type below device_name
            #self.render_circle([(size.width + size.width - self.right_offset)/2, corner_y + self.panel_height/2], self.panel_height/4,'black',0.2)

            if self.simulation_mode: #TODO figure out how to get around non-uniform rendering in time
                if self.simulation_timer == 0:
                    self.simulation_timer = time.clock() #start (or re-start) the simulation clock

                time_elapsed = time.clock() - self.simulation_timer 

                if time_elapsed < 3*len(device_signal): #render signal according to how much time has elapsed
                    self.render_signal(corner_y, device_signal[0:int(time_elapsed//3+1)])
                else: #have reached end, so stop simulation and reset simulation variables
                    self.simulation_timer = 0
                    self.simulation_mode = False
            else:
                self.render_signal(corner_y, device_signal) #show full signal
            #self.render_circle([150,150], 50, 'red', 0.2)

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
        """
        #else:
        #    self.Refresh()  # triggers the paint event
        """

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
            vertex, next_vertex = vertices[index], vertices[index+1]
            GL.glBegin(GL.GL_LINE_STRIP)
            GL.glVertex2f(vertex[0], vertex[1])
            GL.glVertex2f(next_vertex[0], next_vertex[1])
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

    def render_circle(self, center, radius, color, opacity):
        if isinstance(color,str):
            color = self.colormap[color]

        GL.glColor4f(color[0], color[1], color[2], opacity)

        posx, posy = center[0], center[1]    
        sides = 100
        GL.glBegin(GL.GL_POLYGON)    
        for i in range(100):    
            cosine= radius * cos(i*2*pi/sides) + posx    
            sine  = radius * sin(i*2*pi/sides) + posy    
            GL.glVertex2f(cosine,sine)
        GL.glEnd()

    def render_signal(self, corner_y, bits): #corner_y is the y-coordinate of the bottom-left corner of the panel that the signal belongs to
        size = self.GetClientSize()
        x_prev = self.origin_x 
        x_interval = self.grid_small_interval*10/self.grid_big_value
        x_max = size.width - self.right_offset
        y_base = corner_y + self.signal_above_panel
        y_prev = y_base

        for index, bit in enumerate(bits):
            if x_prev + x_interval >= x_max: #signal about to go outside panel 
                break
            if bit in [-0.5,0.5]: #rising
                y_next = y_base + (bit + 0.5)*self.signal_height #if -0.5, y is going to be zero; if +0.5, y is going to be 1
                self.render_line_strip([[x_prev,y_prev],[x_prev + x_interval, y_next]], 'black')
            elif bit in [0,1]: 
                y_next = y_base + bit*self.signal_height
                if index != 0 and bits[index-1] in [0,1]: #transition directly from 0 to 1 or vice versa
                    self.render_line_strip([[x_prev, y_prev], [x_prev, y_next]], 'black') #ONLY if 0->1 directly allowed (No rising or falling edge) 
                    #self.render_line_strip([[x_prev, y_next], [x_prev + x_interval, y_next]], 'black')
                #else:
                self.render_line_strip([[x_prev, y_next], [x_prev + x_interval, y_next]], 'black') #continue signal for 1 cycle if in [1,0]
            else: #bit is None, so don't draw anything
                y_next = y_prev
            x_prev = x_prev + x_interval
            y_prev = y_next






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
        fileMenu.Append(wx.ID_OPEN, "&Open File")
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        #store external class instances as local attributes
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        #define initial number and maximum allowed number of cycles
        self.num_cycles = 100
        self.num_cycles_max = 1000

        ''' #SYSINTEGRATION
        #Network execution and signal recording
        self.devices.cold_startup()
        for _ in range(self.num_cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                #TODO: deal with this error by showing alert box (or some other way)
        '''

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self)
        #self.update_canvas_monitors()

        # Configure the widgets
        self.button_size = wx.Size(105,15)
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles", size=self.button_size)
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, value="", pos=wx.DefaultPosition,
                                size=self.button_size, style=wx.SP_ARROW_KEYS, min=0, 
                                max=self.num_cycles_max, initial=self.num_cycles, name="wxSpinCtrl")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run", size=self.button_size)


        #Monitor control:
        self.add_monitor_name = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER, size=self.button_size)
        self.add_monitor = wx.Button(self, wx.ID_ANY, "Add Monitor", size=self.button_size)
        self.remove_monitor_name = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER, size=self.button_size)
        self.remove_monitor = wx.Button(self, wx.ID_ANY, "Remove Monitor", size=self.button_size)

        #Connections control:
        self.add_connection_name = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER, size=self.button_size)
        self.add_connection = wx.Button(self, wx.ID_ANY, "Add Connection", size=self.button_size)
        self.remove_connection_name = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER, size=self.button_size)
        self.remove_connection = wx.Button(self, wx.ID_ANY, "Del. Connection", size=wx.Size(105,30))

        #Simulation control:
        self.play_simulation = wx.Button(self, wx.ID_ANY, "Play Simulation", size=self.button_size)


        # Bind events to widgets
        
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.add_monitor_name.Bind(wx.EVT_TEXT_ENTER, self.on_add_monitor_name)
        self.add_monitor.Bind(wx.EVT_BUTTON, self.on_add_monitor)
        self.remove_monitor_name.Bind(wx.EVT_TEXT_ENTER, self.on_remove_monitor_name)
        self.remove_monitor.Bind(wx.EVT_BUTTON, self.on_remove_monitor)
        self.add_connection_name.Bind(wx.EVT_TEXT_ENTER, self.on_add_connection_name)
        self.add_connection.Bind(wx.EVT_BUTTON, self.on_add_connection)
        self.remove_connection_name.Bind(wx.EVT_TEXT_ENTER, self.on_remove_connection_name)
        self.remove_connection.Bind(wx.EVT_BUTTON, self.on_remove_connection)
        self.play_simulation.Bind(wx.EVT_BUTTON, self.on_play_simulation)

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
        side_sizer.Add(self.add_connection_name, 1, wx.ALL, 5)
        side_sizer.Add(self.add_connection, 1, wx.ALL, 5)
        side_sizer.Add(self.remove_connection_name, 1, wx.ALL, 5)
        side_sizer.Add(self.remove_connection, 1, wx.ALL, 5)
        side_sizer.Add(self.play_simulation, 1, wx.ALL, 5)

        self.SetSizeHints(300, 300)
        self.SetSizer(main_sizer)

    '''
    #Supposed to handle resizing of buttons according to window and canvas sizes - doesn't work (crashes the UI)
    def on_resize(self, event):    
        canvas_size = self.canvas.GetClientSize()
        window_size = self.GetSize()
        new_size = wx.Size((window_size[0] - canvas_size[0]-10/2)/2,30)
        self.spin.SetSize(new_size)
        self.run_button.SetSize(new_size)
        self.add_monitor_name.SetSize(new_size)
        self.add_monitor.SetSize(new_size)
        self.remove_monitor_name.SetSize(new_size)
        self.remove_monitor.SetSize(new_size)
        self.add_connection_name.SetSize(new_size)
        self.add_connection.SetSize(new_size)
        self.remove_connection_name.SetSize(new_size)
        self.remove_connection.SetSize(new_size)
        self.play_simulation.SetSize(new_size)
    '''

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_FILE:
            open_file_dialog = wx.FileDialog(self, "Open", "", "", 
                                      "Python files (*.py)|*.py", 
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            open_file_dialog.ShowModal()
            print(open_file_dialog.GetPath())
            #path = open_file_dialog.GetPath()
            open_file_dialog.Destroy()
            #TODO enable file loading
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017","About Logsim", wx.ICON_INFORMATION | wx.OK)


    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        if spin_value > 0:
            self.canvas.grid_big_value = spin_value/5 #since there are 5 big subdivisions in the grid

            #TODO run the network again for the new number of cycles, update self.canvas's monitor attribute afterwards
            if spin_value > self.num_cycles:
                self.devices.cold_startup()
                for _ in range(self.num_cycles):
                    if self.network.execute_network():
                        self.monitors.record_signals()
                    else:
                        print("Error! Network oscillating.")
                self.update_canvas_monitors()
            self.num_cycles = spin_value #update num_cycles

        #text = "".join(["New spin control value: ", str(spin_value)])
        #self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        if self.run_button.GetLabel() == "Run":
            self.run_button.SetLabel("Pause")
            print(self.canvas.GetClientSize())
            print(self.GetSize())
        else:
            self.run_button.SetLabel("Run") # TODO actually run the simulation
        text = "Run button pressed."
        self.canvas.render(text)

    def on_add_monitor_name(self, event):
        text_box_value = self.add_monitor_name.GetValue()
        #maybe print out to command line?

    def on_remove_monitor_name(self, event):
        text_box_value = self.remove_monitor_name.GetValue()
        #maybe print out to command line?

    def on_add_monitor(self, event):
        device_name = self.add_monitor_name.GetValue()
        if device_name == "":
            print('Must enter a device name to add monitor')
        else:
            name_exists = self.names.query(device_name) 
            if name_exists is None:
                print('Name does not exist')
            else:
                [device_id,output_id] = self.devices.get_signal_ids(device_name)
                self.monitors.make_monitor(device_id, output_id, 0)
                device_type = self.devices.get_device(device_id).device_kind
                #re-execute network and monitor signals for this device 
                self.devices.cold_startup()
                for _ in range(self.num_cycles):
                    if self.network.execute_network():
                        self.monitors.record_signals()
                    else:
                        print("Error! Network oscillating.")
                signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
                device_signal = self.convert_signal(self.devices,signal_list)
                self.canvas.devices_properties.append([device_type, device_name, device_signal]) #add data to canvas

        '''
        #TODO - check if device name exists and add to monitors, track new signal (execute network), etc.
        '''
        #add_monitor(self,devices,monitors,device_id,output_id): #function in MyGLCanvas - DONT FORGET TO PASS DEVICES AS ARG.

    def on_remove_monitor(self, event):
        #TODO - update monitors
        #remove_monitor(self,devices,device_id,output_id):
        monitor_name = self.remove_monitor_name.GetValue()
        if monitor_name == "":
            print('Must enter a device name to remove monitor')
        else:
            for index, device in enumerate(self.canvas.devices_properties):#TODO check against names class variable and add it to canvas.devices if 
                if device[1] == monitor_name: #check if device is in fact currently being monitored
                    self.canvas.devices_properties.pop(index) #remove from canvas monitor
                    [device_id,output_id] = self.devices.get_signal_ids(monitor_name) 
                    self.monitors.remove_monitor(device_id, output_id) #remove from local monitor instance
                    return
            #searched through canvas monitors, name not found...
            print('Device with such name is not being monitored')
       

        #self.canvas.monitor_devices[-1] = False
        #print('Goodbye')

    def on_add_connection_name(self, event):
        print('Add connection text entered')#TODO add functionality for these - integration with connections

    def on_add_connection(self, event):
        print('Add connection')

    def on_remove_connection_name(self, event):
        print('Remove connection text entered')

    def on_remove_connection(self, event):
        print('Remove connection')

    def on_play_simulation(self, event):
        #TODO - render the signals one cycle at a time, every 2s
        self.canvas.simulation_mode = True
        print('Pressed play simulation')

    #     """Handle the event when the user enters text."""
    #     text_box_value = self.text_box.GetValue()
    #     text = "".join(["New text box value: ", text_box_value])
    #     self.canvas.render(text)

    def update_canvas_monitors(self): #list out monitored devices and their properties from scratch
        self.canvas.devices_properties.clear()
        for device_id, output_id in self.monitors.monitors_dictionary:
            device_name = self.devices.get_signal_name(device_id, output_id)
            device_type = self.devices.get_device(device_id).device_kind
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            device_signal = self.convert_signal(signal_list)
            self.canvas.devices_properties.append([device_type, device_name, device_signal])

    def convert_signal(self, signal_list):
        device_signal = []
        for signal in signal_list:
            if signal == self.devices.HIGH:
                device_signal.append(1)
            elif signal == self.devices.LOW:
                device_signal.append(0)
            elif signal == self.devices.RISING:
                device_signal.append(0.5)
            elif signal == self.devices.FALLING:
                device_signal.append(-0.5)
            elif signal == self.devices.BLANK:
                device_signal.append(2)
            else: #report an error 
                device_signal.append(2)
                print('Error - corrupt signal value')
        return device_signal
        
