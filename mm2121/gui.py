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

    render(self): Handles all drawing operations.

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
        self.min_zoom = 0.9
        self.max_zoom = 2.5

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # Color mappings from string to RGB value
        self.colormap = {'red':[1.0, 0.0, 0.0],'green':[0.0, 1.0, 0.0],'blue':[0.0, 0.0, 1.0], 'yellow':[1.0, 1.0, 0.0], 'black':[0.0, 0.0, 0.0], 'white':[1.0, 1.0, 1.0]}
        
        #Display variables
        self.right_offset = 42 #offset for internal frame from right hand edge of canvas 
        self.top_offset = 20
        self.bottom_offset = 70
        #left_offset same as origin_x
        
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
        self.x_axis_label_offset = 125
        self.y_axis_label_offset = 10 

        #Devices, monitors
        self.devices_monitored = [] #internal use - is a list of lists of the form [device_type,device_name,device_signal]. 
                                     #Is set upon initialisation of Gui class instance


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
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        

    def render(self):
        """Handle all drawing operations."""
        size = self.GetClientSize()

        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        #Draw basic frame
        self.render_line_strip([[self.origin_x, self.origin_y], [size.width - self.right_offset, self.origin_y]], 'black') #bottom horizontal line
        self.render_text('Number of cycles', size.width - self.right_offset - self.x_axis_label_offset, 15, 'black')

        max_devices_fit = (size.height - self.top_offset - self.bottom_offset)//(self.inter_panel_spacing + self.panel_height) #max number of devices that will fit in un-resized window
        num_devices_now = len(self.devices_monitored)

        if num_devices_now > max_devices_fit:
            max_height_panels = self.bottom_offset + (self.panel_height + self.inter_panel_spacing)*num_devices_now
            self.render_line_strip([[self.origin_x, self.origin_y], [self.origin_x, max_height_panels]], 'black') #left vertical line
            self.render_line_strip([[size.width - self.right_offset, max_height_panels], [size.width - self.right_offset, self.origin_y]], 'black') #right vertical line
            self.render_text('Name\n[Type]', self.y_axis_label_offset, max_height_panels + 30,'black')
        else:
            self.render_line_strip([[self.origin_x, self.origin_y], [self.origin_x, size.height - self.top_offset]], 'black') #left vertical line
            self.render_line_strip([[size.width - self.right_offset, size.height-self.top_offset], [size.width-self.right_offset, self.origin_y]], 'black') #right vertical line
            self.render_text('Name\n[Type]', self.y_axis_label_offset, size.height - self.top_offset - 10,'black')

        #Adjust small and big intervals to occupy window area
        big_interval = int((size.width - self.right_offset - self.origin_x) / 5)
        self.grid_small_interval = int(big_interval / 10)
        self.grid_big_interval = 10*self.grid_small_interval

        if self.grid_small_interval <= 0:
            self.grid_small_interval = 1
            self.grid_big_interval = 10

        #Draw grid and markers
        for x in range(self.origin_x, size.width - self.right_offset + 1, self.grid_small_interval): # +1 so we can draw a grid marker on the last point as well
            if (x - self.origin_x) % self.grid_big_interval == 0:
                self.render_line_strip([[x,self.origin_y], [x,self.origin_y - 10]], 'black') #draw a longer line for large intervals
                self.render_text(str(self.grid_big_value*(x - self.origin_x) / (self.grid_big_interval)), 
                                 x - self.grid_hor_text_offset, self.origin_y - self.grid_vert_text_offset, 'black') #also show value at large intervals
            else:
                self.render_line_strip([[x,self.origin_y], [x,self.origin_y - 5]], 'black')

        #Draw device outputs
        for index, device in enumerate(self.devices_monitored): #TODO with simple loop over self.devices

            device_type = device[0]
            device_name = device[1]
            device_signal = device[2] #list that takes values in [0,0.5,-0.5,1,2]

            #corner => bottom-left corner 
            corner_x = self.origin_x
            corner_y = self.bottom_offset + (self.panel_height + self.inter_panel_spacing)*(index) #height depends on number of devices that have been rendered upto now, therefore need index value

            if device_type == 'CLOCK':
                color = 'green'
            elif device_type == 'DTYPE':
                color = 'blue'
            elif device_type == 'SWITCH':
                color = 'yellow'
            else:
                color = 'red'

            self.render_rectangle([corner_x, corner_y], self.panel_height, size.width - corner_x - self.right_offset, color, 0.2) #draw colored panel behind signal

            self.render_text(device_name, self.y_axis_label_offset, corner_y + 25, 'black') #render device name to the left of this panel
            self.render_text("[" + device_type + "]", self.y_axis_label_offset, corner_y + 10, 'black') #render device type below device_name
            self.render_signal(corner_y, device_signal)

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

        self.render()

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
            
            if self.zoom > self.max_zoom:
                self.zoom = self.max_zoom
            if self.zoom < self.min_zoom:
                self.zoom = self.min_zoom
            
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])

        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))

            if self.zoom > self.max_zoom:
                self.zoom = self.max_zoom
            if self.zoom < self.min_zoom:
                self.zoom = self.min_zoom

            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
    
        if text:
            self.render()
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
        font = GLUT.GLUT_BITMAP_8_BY_13

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
            if bit in [-0.5, 0.5]: #rising
                y_next = y_base + (bit + 0.5)*self.signal_height #if -0.5, y is going to be zero; if +0.5, y is going to be 1
                self.render_line_strip([[x_prev, y_prev],[x_prev + x_interval, y_next]], 'black')
            elif bit in [0,1]: 
                y_next = y_base + bit*self.signal_height
                if index != 0 and bits[index - 1] in [0,1]: #transition directly from 0 to 1 or vice versa
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
        self.num_cycles = 200
        self.num_cycles_max = 10000
        
        self.run_network(True, self.num_cycles)
        self.canvas = MyGLCanvas(self) # Canvas for drawing signals
        self.canvas.grid_big_value = self.num_cycles/5 #big value attribute of canvas depends on initial number of cycles
        self.update_canvas_monitors()

        # Configure the widgets
        self.button_size = wx.Size(105,30)
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles", size=self.button_size)
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, value="", pos=wx.DefaultPosition,
                                size=wx.Size(120,30), style=wx.SP_ARROW_KEYS, min=1, 
                                max=self.num_cycles_max, initial=self.num_cycles, name="wxSpinCtrl")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run", size=self.button_size)
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue", size=self.button_size)

        #Monitor control:
        self.add_monitor_name = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER, size=self.button_size)
        self.add_monitor = wx.Button(self, wx.ID_ANY, "+ Monitor", size=self.button_size)
        self.remove_monitor_name = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER, size=self.button_size)
        self.remove_monitor = wx.Button(self, wx.ID_ANY, "- Monitor", size=self.button_size)

        self.set_switch_name = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER, size=self.button_size)
        self.set_switch = wx.Button(self, wx.ID_ANY, "Set Switch", size=self.button_size)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.add_monitor_name.Bind(wx.EVT_TEXT_ENTER, self.on_add_monitor_name)
        self.add_monitor.Bind(wx.EVT_BUTTON, self.on_add_monitor)
        self.remove_monitor_name.Bind(wx.EVT_TEXT_ENTER, self.on_remove_monitor_name)
        self.remove_monitor.Bind(wx.EVT_BUTTON, self.on_remove_monitor)
        self.set_switch_name.Bind(wx.EVT_TEXT_ENTER, self.on_set_switch_name)
        self.set_switch.Bind(wx.EVT_BUTTON, self.on_set_switch)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 5)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        side_sizer.Add(self.continue_button, 1, wx.ALL, 5)
        side_sizer.Add(self.add_monitor_name, 1, wx.ALL, 5)
        side_sizer.Add(self.add_monitor, 1, wx.ALL, 5)
        side_sizer.Add(self.remove_monitor_name, 1, wx.ALL, 5)
        side_sizer.Add(self.remove_monitor, 1, wx.ALL, 5)
        side_sizer.Add(self.set_switch_name, 1, wx.ALL, 5)
        side_sizer.Add(self.set_switch, 1, wx.ALL, 5)

        self.SetSizeHints(300, 300)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        elif Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017","About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        spin_value = self.spin.GetValue()
        self.canvas.grid_big_value = spin_value / 5 #since there are 5 big subdivisions in the grid
        if spin_value > self.num_cycles: #re-start whole simulation upto new number of cycles
            self.monitors.reset_monitors()
            self.run_network(True, spin_value)
            self.update_canvas_monitors()
        self.num_cycles = spin_value #update num_cycles
        self.canvas.render()

            #print(self.canvas.devices_monitored[0][2]) #DEBUG

    def on_continue_button(self, event):
        spin_value = self.spin.GetValue()
        if spin_value + self.num_cycles <= self.num_cycles_max:
            self.canvas.grid_big_value = (self.num_cycles + spin_value)/5 #add these cycles to the present number of cycles
            self.run_network(False, spin_value) #don't restart clocks and dtypes
            self.update_canvas_monitors() 
            self.num_cycles = self.num_cycles + spin_value #update num_cycles
            self.canvas.render()
        else:
            print('Cannot run for more than a total of ' + str(self.num_cycles_max) + ' cycles')

    def on_add_monitor_name(self, event):
        self.on_add_monitor(None)

    def on_remove_monitor_name(self, event):
        self.on_remove_monitor(None)

    def on_add_monitor(self, event): 
        device_name = self.add_monitor_name.GetValue()
        if device_name:
            name_exists = self.names.query(device_name.split('.')[0]) #if device is multiple output, only query using name
            if name_exists is not None:
                [monitored_list, non_monitored_list] = self.monitors.get_signal_names()
                if device_name in monitored_list:
                    print('Error - Device is already being monitored')
                elif device_name in non_monitored_list: #add device to monitors
                    [device_id,output_id] = self.devices.get_signal_ids(device_name) 
                    self.monitors.make_monitor(device_id, output_id, 0) 
                    self.monitors.reset_monitors()
                    self.run_network(True, self.num_cycles)
                    self.update_canvas_monitors()
                    self.canvas.render()
                return    
            print('Error - Device with such name does not exist')

    def on_remove_monitor(self, event):
        monitor_name = self.remove_monitor_name.GetValue()
        if monitor_name:
            for index, device in enumerate(self.canvas.devices_monitored): 
                if device[1] == monitor_name: #check if device is currently being monitored
                    self.canvas.devices_monitored.pop(index) #remove from canvas monitors
                    [device_id,output_id] = self.devices.get_signal_ids(monitor_name) 
                    self.monitors.remove_monitor(device_id, output_id) #remove from local monitor instance
                    self.canvas.render()
                    return
            print('Error - Device with such name is not being monitored') #searched through canvas monitors, name not found...

    def on_set_switch_name(self, event):
        self.on_set_switch(None) #run when user presses Enter

    def on_set_switch(self, event):
        input_list = self.set_switch_name.GetValue()
        if input_list:
            input_list = input_list.split('=')
            switch_name = input_list[0]
            if switch_name:
                if len(input_list) == 2:
                        if input_list[1] in ['0','1']:
                            switch_state = int(input_list[1])
                            name_exists = self.names.query(switch_name)
                            if name_exists is None:
                                print('Error - Switch name does not exist')
                            else:
                                [device_id,output_id] = self.devices.get_signal_ids(switch_name) 
                                if self.devices.get_device(device_id).device_kind != self.devices.SWITCH:
                                    print('Error - Input device is not a switch')
                                else:
                                    if self.devices.set_switch(device_id,switch_state):
                                        self.monitors.reset_monitors()
                                        self.run_network(True, self.num_cycles)
                                        self.update_canvas_monitors()
                                        self.canvas.render()
                                        print('Switch set successfully')
                                    else:
                                        print('Error - Failed to set switch')
                        else:
                            print('Error - Invalid switch value. Enter 0 or 1 after "="')
                else:
                    print('Error - must assign value to switch e.g. "sw1=0"')
            else:
                print('Invalid switch name')

    def run_network(self, restart, num_cycles):
        if restart:
            self.devices.cold_startup()
        for _ in range(num_cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error - Network oscillating.")

    def update_canvas_monitors(self): #list out monitored devices and their properties from scratch
        self.canvas.devices_monitored.clear()
        for device_id, output_id in self.monitors.monitors_dictionary:
            device_name = self.devices.get_signal_name(device_id, output_id)
            device_type = self.translate_device_kind(self.devices.get_device(device_id).device_kind)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            device_signal = self.translate_signal(signal_list)
            self.canvas.devices_monitored.append([device_type, device_name, device_signal])

    def translate_signal(self, signal_list): #convert from format in devices class to custom gui format (see below)
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
    
    def translate_device_kind(self, device_kind): #convert from devices class constants to strings for display
        if device_kind == self.devices.SWITCH:
            return 'SWITCH'
        elif device_kind == self.devices.CLOCK:
            return 'CLOCK'
        elif device_kind == self.devices.XOR:
            return 'XOR'
        elif device_kind == self.devices.AND:
            return 'AND'
        elif device_kind == self.devices.NAND:
            return 'NAND'
        elif device_kind == self.devices.OR:
            return 'OR'
        elif device_kind == self.devices.NOR:
            return 'NOR'
        elif device_kind == self.devices.D_TYPE:
            return 'DTYPE'
        else:
            print('Error - BAD DEVICE found')
            return 'BAD DEVICE'