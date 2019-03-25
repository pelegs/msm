import sys
sys.path.append('library')
from libinkub import *
from datetime import datetime

# In Python3.6 this should be unnecessary
from collections import OrderedDict

# For updating status tab
import threading
import time

# For easy measurement calculation
import numpy as np

# For gui
try:
	import gi
	gi.require_version('Gtk', '3.0')
	from gi.repository import Gtk, GObject, GLib
	settings = Gtk.Settings.get_default()
	settings.props.gtk_button_images = True
except:
	raise SystemError('Gtk not availble!')
	sys.exit(1)

__version__ = '0.0.1'

###########
# Threads #
###########

class status_updating_thread(threading.Thread):
	""" STATUS UPDATING THREAD

		Updates the status tab of experimnets
	"""

	def __init__(self, status_tab):
		threading.Thread.__init__(self)
		self._stop_event = threading.Event()
		self.status_tab = status_tab
	
	def run(self):
		while not self.stopped():
			if not lid_open():
				GLib.idle_add(self.status_tab.update)
				time.sleep(1)

	def stop(self):
		self._stop_event.set()

	def stopped(self):
		return self._stop_event.is_set()

###########
# Windows #
###########

class window(Gtk.Window):
	""" GENERIC GTK WINDOW

		Has a width and a height as defined by the
		config file (size_x and size_y, respectively),
		and a gui which is a reference to the main gui.
	"""

	def __init__(self, gui):
		Gtk.Window.__init__(self)

		size_x = configs['SIZE_X']
		size_y = configs['SIZE_Y']
		
		self.gui = gui

		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_size_request(size_x, size_y)
		self.fullscreen()

	def close(self):
		self.destroy()

class pause_window(window):
	""" PAUSE WINDOW
	
		Opens when the pause button is pressed.
		Shows a pause message and displays elapsed
		pause time.
		Has a continue button to end the pause.
	"""

	def __init__(self, gui):
		window.__init__(self, gui)
		self.name = 'pause_window'

		# Cute worm + coffee picture		
		pause_img = Gtk.Image()
		pause_img.set_from_file(configs['PAUSE_IMG'])
		pause_img.set_margin_top(configs['MARGINS']['TOP'])
		pause_img.set_margin_bottom(configs['MARGINS']['BOTTOM'])

		# Timer that ticks and shows elapsed pause time
		# (updated by a special thread initiated by 'begin_pause')
		self.pause_time = Gtk.Label('00:00:00')
		#font = Pango.FontDescription('Purisa 20')
		#self.pause_time.modify_font(font)
		self.pause_time.set_margin_top(configs['MARGINS']['TOP'])
		self.pause_time.set_margin_bottom(configs['MARGINS']['BOTTOM'])

		# Continue button
		continue_icon = Gtk.Image()
		continue_icon.set_from_file(configs['CONTINUE_BUTTON_ICON'])
		continue_button = Gtk.Button()
		continue_button.connect('clicked', self.end_pause)
		continue_button.add(continue_icon)
		continue_button.set_margin_top(configs['MARGINS']['TOP'])
		continue_button.set_margin_bottom(configs['MARGINS']['BOTTOM'])
		continue_button.set_hexpand(False)
		continue_button.set_halign(Gtk.Align.CENTER)
		continue_button.set_vexpand(False)
		continue_button.set_valign(Gtk.Align.CENTER)
		continue_button.set_relief(Gtk.ReliefStyle.NONE)

		# VBox for image and timer
		left_box = Gtk.VBox()
		left_box.pack_start(pause_img, True, True, 0)
		left_box.pack_start(self.pause_time, True, True, 0)

		# VBox for continue button
		right_box = Gtk.VBox()
		right_box.pack_start(continue_button, True, True, 0)

		# Main box container for window
		box = Gtk.Box()
		box.pack_start(left_box,  True, True, 0)
		box.pack_start(right_box, True, True, 0)

		self.add(box)
		self.show_all()
		
		self.begin_pause()

	def begin_pause(self):
		self.pause_start_time = datetime.now()
		self.pause_thread = pause_thread(self, self.pause_start_time)
		self.pause_thread.start()

	def end_pause(self, widget):
		pause_end_time = datetime.now()
		pause_total_time = pause_end_time - self.pause_start_time
		self.pause_thread.stop()
		logger.info('pause time: {}'.format(pause_total_time))
		self.gui.close_pause_window(self.gui, data=pause_total_time)
	
	def update_time(self, new_time):
		self.pause_time.set_text(new_time)

class new_experiment_window(window):
	""" NEW EXPERIMENT WINDOW

		Allows the user to start a new experiment,
		using the cells that were chosen in the main view.
		
		Contains the following adjustable paramters for
		an experiment: user, number of cycles,
		light time (hours + minutes), dark time (hours + minutes),
		light level and temperature.

		The parameters are relayed to a dictionary when
		the user clicks "start" via the (self) function
		'start_button_clicked'.
	"""

	def __init__(self, gui):
		window.__init__(self, gui)
		self.name = 'new_experiment_window'

		# User selection
		#self.cb = Gtk.ComboBoxText()
		#for user in gui.users:
		#	self.cb.append_text(user)
		#self.cb.set_active(0)

		self.user_list = [key for key in gui.users]
		self.num_users = len(gui.users)
		self.user_select_index = 0
		self.selected_user = self.user_list[0]
		self.user_indicator = Gtk.Label(self.user_list[0])
		
		next_user_button = Gtk.Button()
		arrow_next = Gtk.Arrow(Gtk.ArrowType(3))
		next_user_button.add(arrow_next)
		next_user_button.connect('clicked', self.arrow_clicked, 'next')
		
		prev_user_button = Gtk.Button()
		arrow_prev = Gtk.Arrow(Gtk.ArrowType(2))
		prev_user_button.add(arrow_prev)
		prev_user_button.connect('clicked', self.arrow_clicked, 'prev')

		self.user_box = Gtk.HBox()
		self.user_box.pack_start(prev_user_button, True, True, 0)
		self.user_box.pack_start(self.user_indicator, True, True, 0)
		self.user_box.pack_start(next_user_button, True, True, 0)
		self.user_label = Gtk.Label('User:')

		# Number of cycles selection
		num_cycles_adj = Gtk.Adjustment(value=1,
										lower=1,
										upper=5000,
										step_incr=1)
		self.num_cycles = Gtk.SpinButton()
		self.num_cycles.set_adjustment(num_cycles_adj)
		num_cycles_label = Gtk.Label('Num cycles:')

		# Light and dark times
		num_light_hours_adj = Gtk.Adjustment(value=0,
											 lower=0,
											 upper=24,
											 step_incr=1)
		num_light_mins_adj = Gtk.Adjustment(value=0,
											lower=0,
											upper=60,
											step_incr=1)
		num_dark_hours_adj = Gtk.Adjustment(value=0,
											lower=0,
											upper=24,
											step_incr=1)
		num_dark_mins_adj = Gtk.Adjustment(value=0,
										   lower=0,
										   upper=60,
										   step_incr=1)
		self.num_light_hours = Gtk.SpinButton()
		self.num_light_mins = Gtk.SpinButton()
		self.num_dark_hours = Gtk.SpinButton()
		self.num_dark_mins = Gtk.SpinButton()
		self.num_light_hours.set_adjustment(num_light_hours_adj) 
		self.num_light_mins.set_adjustment(num_light_mins_adj)
		self.num_dark_hours.set_adjustment(num_dark_hours_adj)
		self.num_dark_mins.set_adjustment(num_dark_mins_adj) 
		light_label = Gtk.Label('Light time:')
		num_light_hours_label = Gtk.Label('Hours,')
		num_light_mins_label  = Gtk.Label('Minutes')
		dark_label = Gtk.Label('Dark time:')
		num_dark_hours_label  = Gtk.Label('Hours,')
		num_dark_mins_label   = Gtk.Label('Minutes')

		# Light level
		light_level_adj = Gtk.Adjustment(value=20,
										 lower=0,
										 upper=40,
										 step_incr=2)
		self.light_level = Gtk.SpinButton()
		self.light_level.set_adjustment(light_level_adj)
		light_level_label = Gtk.Label('Light level (mW):')

		# Temperature
		temperature_adj = Gtk.Adjustment(value=20,
										 lower=15,
										 upper=25,
										 step_incr=1)
		self.temperature = Gtk.SpinButton()
		self.temperature.set_adjustment(temperature_adj)
		temperature_label = Gtk.Label('Temperature:')
		temperature_units = Gtk.Label('Degrees Celsius')
		if get_num_running_experiments() == 0:
			self.set_temperature = True
			self.temperature.set_sensitive(True)
		else:
			self.set_temperature = False
			self.temperature.set_sensitive(False)

		# Buttons
		start_icon = Gtk.Image()
		start_icon.set_from_file(configs['START_ICON'])
		self.start_button = Gtk.Button()
		self.start_button.add(start_icon)
		self.start_button.connect('clicked', self.start_button_clicked)
		self.start_button.set_relief(Gtk.ReliefStyle.NONE)
	
		cancel_icon = Gtk.Image()
		cancel_icon.set_from_file(configs['CANCEL_ICON'])
		self.cancel_button = Gtk.Button()
		self.cancel_button.add(cancel_icon)
		self.cancel_button.connect('clicked', self.cancel_button_clicked)
		self.cancel_button.set_relief(Gtk.ReliefStyle.NONE)
		
		# Set margins for all widgets
		self.widgets = [self.user_label,
					   self.num_cycles, num_cycles_label,
					   self.num_light_hours, self.num_light_mins,
					   self.num_dark_hours, self.num_dark_mins,
					   num_light_hours_label, num_light_mins_label,
					   num_dark_hours_label, num_dark_mins_label,
					   self.light_level, light_level_label,
					   self.temperature, temperature_label, temperature_units,
					   self.start_button, self.cancel_button]

		for widget in self.widgets:
			widget.set_margin_top(configs['MARGINS']['TOP'])
			widget.set_margin_bottom(configs['MARGINS']['BOTTOM'])
			widget.set_margin_left(configs['MARGINS']['LEFT'])
			widget.set_margin_right(configs['MARGINS']['RIGHT'])

		# Putting all widgets on the grid
		grid = Gtk.Grid()

		grid.attach(self.user_label, 0, 0, 1, 1)
		grid.attach(self.user_box, 1, 0, 2, 1)
		
		grid.attach(num_cycles_label, 0, 1, 1, 1)
		grid.attach(self.num_cycles, 1, 1, 1, 1)
		
		grid.attach(light_label, 0, 2, 1, 1)
		grid.attach(self.num_light_hours, 1, 2, 1, 1)
		grid.attach(num_light_hours_label, 2, 2, 1, 1)
		grid.attach(self.num_light_mins, 3, 2, 1, 1)
		grid.attach(num_light_mins_label, 4, 2, 1, 1)
		
		grid.attach(dark_label, 0, 3, 1, 1)
		grid.attach(self.num_dark_hours, 1, 3, 1, 1)
		grid.attach(num_dark_hours_label, 2, 3, 1, 1)
		grid.attach(self.num_dark_mins, 3, 3, 1, 1)
		grid.attach(num_dark_mins_label, 4, 3, 1, 1)

		grid.attach(light_level_label, 0, 4, 1, 1)
		grid.attach(self.light_level, 1, 4, 1, 1)

		grid.attach(temperature_label, 0, 5, 1, 1)
		grid.attach(self.temperature, 1, 5, 1, 1)
		grid.attach(temperature_units, 2, 5, 1, 1)

		# Vertical box (for buttons)
		vbox = Gtk.VBox()
		vbox.pack_start(self.start_button, True, True, 0)
		vbox.pack_start(self.cancel_button, True, True, 0)

		# Horizontal box (grid a vbox)
		box = Gtk.Box()
		box.pack_start(grid, True, True, 0)
		box.pack_start(vbox, True, True, 0)

		self.add(box)
		self.show_all()

	def arrow_clicked(self, widget, direction='next'):
		if direction == 'next':
			self.user_select_index = (self.user_select_index + 1) % self.num_users
		elif direction == 'prev':
			self.user_select_index = (self.user_select_index - 1) % self.num_users
		
		self.selected_user = self.user_list[self.user_select_index]
		self.user_indicator.set_text(self.selected_user)

	def start_button_clicked(self, widget):
		# Grey-out widgets in window
		logger.info('Tab supposedly greyed-out')
		for widget in self.widgets:
			widget.set_sensitive(False)

		# Increment user's num of experiments
		user = self.selected_user
		configs['USERS'][user] += 1
		experiment_name = '{}-{}'.format(user, configs['USERS'][user])

		# Save widget values to a dictionary
		new_experiment_params = {'name':		experiment_name,
								 'num_cycles':		   int(self.num_cycles.get_value()),
								 'light_hours':		   int(self.num_light_hours.get_value()),
								 'light_mins':		   int(self.num_light_mins.get_value()),
								 'dark_hours':		   int(self.num_dark_hours.get_value()),
								 'dark_mins':		   int(self.num_dark_mins.get_value()),
								 'target_light_level': int(self.light_level.get_value()),
								 'temperature':		   -1}

		if self.set_temperature:
			new_experiment_params['temperature'] = int(self.temperature.get_value())
		
		self.gui.start_new_experiment(self.gui, parameters=new_experiment_params)

	def cancel_button_clicked(self, widget):
		self.start_new_experiment = False	
		self.destroy()
		logger.info('Cancel button clicked')

class stop_all_experiments_window(window):
	""" STOP ALL EXPERIMENTS WINDOW

		Displays a warning message and button
		to stop all experiments (i.e. in case
		of an emergency).
	"""

	def __init__(self, gui):
		window.__init__(self, gui)
		self.name = 'stop_all_experiments_window'

		stop_warning = Gtk.Image()
		stop_warning.set_from_file(configs['WARNING'])
		stop_warning.set_margin_bottom(configs['MARGINS']['BOTTOM'])
		
		back_icon = Gtk.Image()
		back_icon.set_from_file(configs['BACK_ICON'])
		back_button = Gtk.Button()
		back_button.add(back_icon)
		back_button.connect('clicked', self.back_button_clicked)
		back_button.set_relief(Gtk.ReliefStyle.NONE)
		back_button.set_margin_top(configs['MARGINS']['TOP'])
		back_button.set_margin_right(configs['MARGINS']['RIGHT'])

		stop_icon = Gtk.Image()
		stop_icon.set_from_file(configs['STOP_ICON_REV'])
		stop_button = Gtk.Button()
		stop_button.add(stop_icon)
		stop_button.connect('clicked', self.stop_button_clicked)
		stop_button.set_relief(Gtk.ReliefStyle.NONE)
		stop_button.set_margin_top(configs['MARGINS']['TOP'])
		stop_button.set_margin_left(configs['MARGINS']['LEFT'])
	
		# Buttons box on the bottom
		hbox = Gtk.Box()
		hbox.pack_start(back_button, True, True, 0)
		hbox.pack_start(stop_button, True, True, 0)

		# Main box
		box = Gtk.VBox()
		box.pack_start(stop_warning, True, True, 0)
		box.pack_start(hbox, True, True, 0)

		# Add all, display window
		self.add(box)
		self.show_all()

	def back_button_clicked(self, widget):
		logger.info('Back button pressed')
		self.close()
	
	def stop_button_clicked(self, widget):
		self.gui.stop_all_experiments(self.gui)
		self.close()
		
class stop_single_experiment_window(window):
	""" STOP SINGLE EXPERIMENT WINDOW

		Displayed to the user when the stop button
		in the experiment status bar is pressed.
	"""

	def __init__(self, gui, group):
		window.__init__(self, gui)
		self.name = 'stop_single_experiment_window'
		self.group = group		

		stop_warning = Gtk.Image()
		stop_warning.set_from_file(configs['WARNING_SINGLE'])
		stop_warning.set_margin_bottom(configs['MARGINS']['BOTTOM'])
		
		back_icon = Gtk.Image()
		back_icon.set_from_file(configs['BACK_ICON'])
		back_button = Gtk.Button()
		back_button.add(back_icon)
		back_button.connect('clicked', self.back_button_clicked)
		back_button.set_relief(Gtk.ReliefStyle.NONE)
		back_button.set_margin_top(configs['MARGINS']['TOP'])
		back_button.set_margin_right(configs['MARGINS']['RIGHT'])

		stop_icon = Gtk.Image()
		stop_icon.set_from_file(configs['STOP_ICON_REV'])
		stop_button = Gtk.Button()
		stop_button.add(stop_icon)
		stop_button.connect('clicked', self.stop_button_clicked)
		stop_button.set_relief(Gtk.ReliefStyle.NONE)
		stop_button.set_margin_top(configs['MARGINS']['TOP'])
		stop_button.set_margin_left(configs['MARGINS']['LEFT'])
	
		# Buttons box on the bottom
		hbox = Gtk.Box()
		hbox.pack_start(back_button, True, True, 0)
		hbox.pack_start(stop_button, True, True, 0)

		# Main box
		box = Gtk.VBox()
		box.pack_start(stop_warning, True, True, 0)
		box.pack_start(hbox, True, True, 0)

		# Add all, display window
		self.add(box)
		self.show_all()

	def back_button_clicked(self, widget):
		logger.info('Cancelled stopping single experiment')
		self.close()
	
	def stop_button_clicked(self, widget):
		# Stop experiment
		logger.info('Stopping single experiment: {}'.format(self.group.parameters['name']))
		self.gui.stop_single_experiment(self.gui, self.group)
		self.close()

class exit_program_window(window):
	""" EXIT PROGRAM WINDOW

		Prompts the user with "are you sure you want
		to exit the program".
	"""

	def __init__(self, gui):
		window.__init__(self, gui)
		self.name = 'exit_program_window'

		exit_prompt_img = Gtk.Image()
		exit_prompt_img.set_from_file(configs['EXIT_PROMPT'])
		exit_prompt_img.set_margin_bottom(configs['MARGINS']['BOTTOM'])
		
		back_icon = Gtk.Image()
		back_icon.set_from_file(configs['BACK_ICON_BLUE'])
		back_button = Gtk.Button()
		back_button.add(back_icon)
		back_button.connect('clicked', self.back_button_clicked)
		back_button.set_relief(Gtk.ReliefStyle.NONE)
		back_button.set_margin_top(configs['MARGINS']['TOP'])
		back_button.set_margin_right(configs['MARGINS']['RIGHT'])

		exit_icon = Gtk.Image()
		exit_icon.set_from_file(configs['EXIT_ICON_GREEN'])
		exit_button = Gtk.Button()
		exit_button.add(exit_icon)
		exit_button.connect('clicked', self.gui.gtk_main_quit)
		exit_button.set_relief(Gtk.ReliefStyle.NONE)
		exit_button.set_margin_top(configs['MARGINS']['TOP'])
		exit_button.set_margin_left(configs['MARGINS']['LEFT'])
	
		# Buttons box on the bottom
		hbox = Gtk.Box()
		hbox.pack_start(back_button, True, True, 0)
		hbox.pack_start(exit_button, True, True, 0)

		# Main box
		box = Gtk.VBox()
		box.pack_start(exit_prompt_img, True, True, 0)
		box.pack_start(hbox, True, True, 0)

		# Add all, display window
		self.add(box)
		self.show_all()

	def back_button_clicked(self, widget):
		logger.info('Cancelled exiting program')
		self.close()
	
class lid_open_window(window):
	""" LID OPEN WINDOW

		A full screen window announcing the lid is open.
		Will only close when lid is closed.
	"""

	def __init__(self, gui):
		window.__init__(self, gui)
		self.name = 'lid_open_window'
		
		img = Gtk.Image()
		img.set_from_file(configs['LID_OPEN_IMG'])

		box = Gtk.VBox()
		box.pack_start(img, True, True, 0)
		
		self.add(box)
		self.show_all()

class about_window(window):
	""" ABOUT WINDOW

		Shows about information
	"""

	def __init__(self, gui):
		window.__init__(self, gui)
		self.name = 'about_window'
		
		img = Gtk.Image()
		img.set_from_file(configs['ABOUT_IMG'])

		box = Gtk.VBox()
		box.pack_start(img, True, True, 0)
		
		back_icon = Gtk.Image()
		back_icon.set_from_file(configs['BACK_ICON'])
		back_button = Gtk.Button()
		back_button.connect('clicked', self.back_button_clicked)
		back_button.add(back_icon)
		box.pack_start(back_button, True, True, 0)

		self.add(box)
		self.show_all()
		
	def back_button_clicked(self, widget):
		self.close()

class preparing_experiment_window(window):
	""" PREPARING EXPERIMENT WINDOW

		A full screen window announcing the experiments
		are being prepared and the user should wait.
	"""

	def __init__(self, gui):
		window.__init__(self, gui)
		self.name = 'preparing_experiment_window'
		
		img = Gtk.Image()
		img.set_from_file(configs['EXP_PREP_IMG'])

		box = Gtk.VBox()
		box.pack_start(img, True, True, 0)
		
		self.add(box)
		self.show_all()

########
# Tabs #
########

class main_tab:
	""" MAIN VIEW (default tab)
		
		Displays cells + start-, pause- and stop-buttons.
	"""

	def __init__(self, gui, configs):
		self.gui = gui
		self.configs = configs

		# Create grid
		self.grid = Gtk.Grid()
		self.grid_pos_by_cell_index = {
		 0:  (0, 0), 
		 1:  (2, 0), 
		 2:  (4, 0), 
		 3:  (1, 1), 
		 4:  (3, 1), 
		 5:  (0, 2), 
		 6:  (2, 2), 
		 7:  (4, 2), 
		 8:  (1, 3), 
		 9:  (3, 3), 
		 10: (0, 4), 
		 11: (2, 4), 
		 12: (4, 4)
		}

		# Create icon objects for cells
		self.cell_icons = []
		for i in range(13):
			icon = Gtk.Image()
			icon.set_from_file(self.configs['CELL_BUTTON_ICONS'][FREE])
			self.cell_icons.append(icon)

		# Create 13 toggle buttons for choosing cells
		self.cell_buttons = [Gtk.ToggleButton() for i in range(13)]
		for i, button in enumerate(self.cell_buttons):
			# Set graphical variables
			button.set_margin_left(configs['MARGINS']['LEFT'])
			button.set_margin_right(configs['MARGINS']['RIGHT'])
			button.set_hexpand(False)
			button.set_halign(Gtk.Align.CENTER)
			button.set_vexpand(False)
			button.set_valign(Gtk.Align.CENTER)
			button.set_relief(Gtk.ReliefStyle.NONE)
	
			# Put icons on each button		
			button.add(self.cell_icons[i])
			button.set_size_request(85, 85)

			# Connect button with action: the gui's update_cell function
			button.connect('toggled', self.select_cell, i)
		
			# Position in grid	
			grid_pos = self.grid_pos_by_cell_index[i]
			self.grid.attach(button, grid_pos[0], grid_pos[1], 1, 1)

		# Create three action buttons (new, pause and stop all)
		# Start button
		self.new_icon = Gtk.Image()
		self.new_icon.set_from_file(self.configs['NEW_ICON'])
		self.new_button = Gtk.Button()
		self.new_button.add(self.new_icon)
		self.new_button.connect('clicked', self.gui.open_new_experiment_window)
		self.grid.attach(self.new_button, 5, 0, 1, 1)
		
		# Pause button
		self.pause_icon = Gtk.Image()
		self.pause_icon.set_from_file(self.configs['PAUSE_ICON'])
		self.pause_button = Gtk.Button()
		self.pause_button.add(self.pause_icon)
		self.pause_button.connect('clicked', self.gui.open_pause_window)
		self.grid.attach(self.pause_button, 5, 2, 1, 1)
		
		# Stop button
		self.stop_icon = Gtk.Image()
		self.stop_icon.set_from_file(self.configs['STOP_ICON'])
		self.stop_button = Gtk.Button()
		self.stop_button.add(self.stop_icon)
		self.stop_button.connect('clicked', self.gui.open_stop_all_experiments_window)
		self.grid.attach(self.stop_button, 5, 4, 1, 1)
	
		for button in [self.new_button, self.pause_button, self.stop_button]:	
			button.set_margin_left(configs['MARGINS']['LEFT'])
			button.set_margin_right(configs['MARGINS']['RIGHT'])
			button.set_hexpand(False)
			button.set_halign(Gtk.Align.CENTER)
			button.set_vexpand(False)
			button.set_valign(Gtk.Align.CENTER)
			button.set_relief(Gtk.ReliefStyle.NONE)
			button.set_size_request(150, 90)

	def select_cell(self, widget, index):
		if widget.get_sensitive():
			cell = self.gui.cells[index]
			selected_cells = self.gui.selected_cells
			if widget.get_active():
				cell.set_selected()
				selected_cells.add(index)
			else:
				cell.set_free()
				if index in self.gui.selected_cells:
					selected_cells.remove(index)
		self.gui.update_cell_icon(self.gui, index=index)

class actions_tab:
	""" ACTIONS TAB
		
		Currently has only Exit button (close program),
		might have others in the future (e.g. log).
	"""

	def __init__(self, gui):
		self.gui = gui
		
		about_icon = Gtk.Image()
		about_icon.set_from_file(configs['ABOUT_ICON'])
		self.about_button = Gtk.Button()
		self.about_button.connect('clicked', self.gui.about_button_clicked)
		self.about_button.add(about_icon)
		self.about_button.set_margin_left(configs['MARGINS']['RIGHT'])
		self.about_button.set_margin_right(configs['MARGINS']['LEFT'])
		self.about_button.set_hexpand(False)
		self.about_button.set_halign(Gtk.Align.CENTER)
		self.about_button.set_vexpand(False)
		self.about_button.set_valign(Gtk.Align.CENTER)
		self.about_button.set_relief(Gtk.ReliefStyle.NONE)
		self.about_button.set_size_request(160, 95)
		
		exit_icon = Gtk.Image()
		exit_icon.set_from_file(configs['EXIT_ICON_GREEN'])
		self.exit_button = Gtk.Button()
		self.exit_button.connect('clicked', self.gui.exit_button_clicked)
		self.exit_button.add(exit_icon)
		self.exit_button.set_margin_left(configs['MARGINS']['RIGHT'])
		self.exit_button.set_margin_right(configs['MARGINS']['LEFT'])
		self.exit_button.set_hexpand(False)
		self.exit_button.set_halign(Gtk.Align.CENTER)
		self.exit_button.set_vexpand(False)
		self.exit_button.set_valign(Gtk.Align.CENTER)
		self.exit_button.set_relief(Gtk.ReliefStyle.NONE)
		self.exit_button.set_size_request(160, 95)

		self.box = Gtk.VBox()
		self.box.pack_start(self.about_button, True, True, 0)
		self.box.pack_start(self.exit_button,  True, True, 0)

class status_tab:
	""" STATUS TAB

		Reports on the status of an experiment.
	"""

	def __init__(self, gui, menuitem, group):
		self.gui = gui
		self.menuitem = menuitem
		self.group = group
		self.name = self.group.parameters['name']
		self.group_cells = self.group.parameters['designated_cells_ids']
		self.grid = Gtk.Grid()
		self.name = self.group.parameters['name']
		self.start_datetime	= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.num_cycles = self.group.get_num_cycles()

		# For saving measurements
		self.num_measurements = 0
		
		# Logging
		self.log_file_name = 'logs/{}_{}.log'.format(self.group.parameters['name'], datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
		with open(self.log_file_name, 'a') as logfile:
			logfile.write("""# Log for experiment {}. Cells used: {}
							 # Data format: temperatures, humidities, pressures, air qualities, light levels, ir levels""".format(
						  self.group.parameters['name'],
						  ', '.join(map(str, self.group_cells))
						  ))
	
		# create tab layout and widgets
		# text labels
		self.labels = OrderedDict([
					  ('name',			 Gtk.Label('Name:')),
					  ('group_cells',	 Gtk.Label('Cells:')),
					  ('start_datetime', Gtk.Label('Start time:')),	
					  ('light_level',    Gtk.Label('Light level:')),	
					  ('current_cycle',  Gtk.Label('Cycle:')),	
					  ('progress',		 Gtk.Label('Cycle progress:')),	
					  ('temperature',	 Gtk.Label('Tempertature:')),	
					  ('humidity',		 Gtk.Label('Humidity:')),	
					  ('air_quality',	 Gtk.Label('Air quality:'))
					  ])
		for i, (key, label) in enumerate(self.labels.items()):
			label.set_margin_left(5)
			label.set_margin_right(5)
			label.set_vexpand(True)
			label.set_alignment(0, 0.5)
			self.grid.attach(label, 0, i, 1, 1)

		# values
		self.values = OrderedDict([
					  ('name',			 Gtk.Label(self.name + ' (id={})'.format(self.group.group_id))),
					  ('group_cells',	 Gtk.Label(', '.join(map(str, self.group_cells)))),
					  ('start_datetime', Gtk.Label(self.start_datetime)),
					  ('light_level',	 Gtk.Label('0')),	
					  ('current_cycle',	 Gtk.Label('x out of y')),	
					  ('elapsed_time',	 Gtk.Label('00:00:00')),	
					  ('remaining_time', Gtk.Label('00:00:00')),	
					  ('temperature',	 Gtk.Label('xx C')),	
					  ('humidity',		 Gtk.Label('xx%')),	
					  ('air_quality',	 Gtk.Label('xx%'))
					 ])
		
		self.values['name'].set_margin_left(5)
		self.values['name'].set_margin_right(5)
		self.values['name'].set_vexpand(True)
		self.values['light_level'].set_alignment(0, 0.5)
		self.grid.attach(self.values['name'], 1, 0, 1, 1)
		
		self.values['group_cells'].set_margin_left(5)
		self.values['group_cells'].set_margin_right(5)
		self.values['group_cells'].set_vexpand(True)
		self.values['light_level'].set_alignment(0, 0.5)
		self.grid.attach(self.values['group_cells'], 1, 1, 1, 1)
		
		self.values['start_datetime'].set_margin_left(5)
		self.values['start_datetime'].set_margin_right(5)
		self.values['start_datetime'].set_vexpand(True)
		self.values['light_level'].set_alignment(0, 0.5)
		self.grid.attach(self.values['start_datetime'], 1, 2, 1, 1)
		
		self.values['light_level'].set_margin_left(5)
		self.values['light_level'].set_margin_right(5)
		self.values['light_level'].set_vexpand(True)
		self.values['light_level'].set_alignment(0, 0.5)
		self.grid.attach(self.values['light_level'], 1, 3, 3, 1)
		
		self.values['current_cycle'].set_margin_left(5)
		self.values['current_cycle'].set_margin_right(5)
		self.values['current_cycle'].set_vexpand(True)
		self.values['light_level'].set_alignment(0, 0.5)
		self.grid.attach(self.values['current_cycle'], 1, 4, 1, 1)
		
		self.values['elapsed_time'].set_margin_left(5)
		self.values['elapsed_time'].set_margin_right(5)
		self.values['elapsed_time'].set_vexpand(True)
		self.values['light_level'].set_alignment(0, 0.5)
		self.grid.attach(self.values['elapsed_time'], 1, 5, 1, 1)
		
		self.values['remaining_time'].set_margin_left(5)
		self.values['remaining_time'].set_margin_right(5)
		self.values['remaining_time'].set_vexpand(True)
		self.values['light_level'].set_alignment(0, 0.5)
		self.grid.attach(self.values['remaining_time'], 4, 5, 1, 1)
		
		self.values['temperature'].set_margin_left(5)
		self.values['temperature'].set_margin_right(5)
		self.values['temperature'].set_vexpand(True)
		self.values['temperature'].set_alignment(0, 0.5)
		self.grid.attach(self.values['temperature'], 1, 6, 3, 1)
		
		self.values['humidity'].set_margin_left(5)
		self.values['humidity'].set_margin_right(5)
		self.values['humidity'].set_vexpand(True)
		self.values['humidity'].set_alignment(0, 0.5)
		self.grid.attach(self.values['humidity'], 1, 7, 3, 1)
		
		self.values['air_quality'].set_margin_left(5)
		self.values['air_quality'].set_margin_right(5)
		self.values['air_quality'].set_vexpand(True)
		self.values['air_quality'].set_alignment(0, 0.5)
		self.grid.attach(self.values['air_quality'], 1, 8, 3, 1)

		# Progress bar
		self.progress_bar = Gtk.ProgressBar()
		self.progress_bar.set_margin_left(5)
		self.progress_bar.set_margin_right(5)
		self.progress_bar.set_vexpand(True)
		self.progress_bar.show()
		self.grid.attach(self.progress_bar, 2, 5, 2, 1)

		# Finish experiment button
		self.finish_experiment_icon = Gtk.Image()
		self.finish_experiment_icon.set_from_file(configs['FINISH_ICON'])
		self.finish_experiment_button = Gtk.Button()
		self.finish_experiment_button.add(self.finish_experiment_icon)
		self.handler_id = self.finish_experiment_button.connect(
			'clicked',
			self.gui.open_stop_single_experiment_window,
			group
			)
		self.finish_experiment_button.set_margin_left(5)
		self.finish_experiment_button.set_margin_right(5)
		self.finish_experiment_button.set_vexpand(True)
		self.grid.attach(self.finish_experiment_button, 4, 1, 1, 1)

		# Start update thread
		self.update_thread = status_updating_thread(self)
		self.update_thread.start()
		
		# Attach to gui
		tab_name = Gtk.Label(self.name)
		self.gui.tabs.append_page(self.grid, tab_name)
		self.gui.tabs.show_all()

	def update(self):
		self.temperatures  = []
		self.humidities	   = []
		self.pressures     = []
		self.air_qualities = []
		self.light_levels  = []
		self.rgbs		   = []
		self.irs		   = []

		self.num_measurements += 1

		# Get sensor readings from cells in group:
		for cell in self.group.cells:
			cell_sensor_data = cell.get_sensor_data()
			self.temperatures.append(cell_sensor_data['temperature'])
			self.humidities.append(cell_sensor_data['humidity'])
			self.pressures.append(cell_sensor_data['pressure'])
			self.air_qualities.append(cell_sensor_data['air_quality'])
			self.light_levels.append(cell_sensor_data['light_level'])
			self.rgbs.append(cell_sensor_data['rgb'])
			self.irs.append(cell_sensor_data['ir'])

		# GUI stuff
		self.current_cycle_num = self.group.group_process.get_current_cycle_num()
		self.status_text = self.group.group_process.get_status()
		self.elapsed_time = self.group.group_process.get_elapsed_time()
		self.elapsed_time_text = str(timedelta(seconds=self.elapsed_time)).split('.')[0]
		self.remaining_time = self.group.group_process.get_remaining_time()
		self.remaining_time_text = str(timedelta(seconds=self.remaining_time)).split('.')[0]
		self.process_duration = self.group.group_process.get_process_duration()

		self.values['current_cycle'].set_text('{:04d} out of {:04d} ({})'.format(
			self.current_cycle_num,
			self.num_cycles,
			self.status_text))
		self.values['light_level'].set_text('{} (set: {:02d})'.format(
			','.join(['{:4.1f}'.format(x) for x in self.light_levels]),
			self.group.parameters['target_light_level']))
		self.values['elapsed_time'].set_text(self.elapsed_time_text)
		self.values['remaining_time'].set_text(self.remaining_time_text)
		self.progress_bar.set_fraction(self.elapsed_time / self.process_duration)
		self.values['temperature'].set_text('{}'.format(','.join(['{:4.1f}'.format(x) for x in self.temperatures])))
		self.values['humidity'].set_text('{}'.format(','.join(['{:4.1f}'.format(x) for x in self.humidities])))
		self.values['air_quality'].set_text('{}'.format(','.join(['{:4.1f}'.format(x) for x in self.air_qualities])))
	
		# log data
		data = '{} {} '.format(self.num_measurements, self.current_cycle_num)
		data += ('{} '.format(' '.join(['{:4.1f}'.format(x) for x in self.temperatures]))) 
		data += ('{} '.format(' '.join(['{:4.1f}'.format(x) for x in self.humidities]))) 
		data += ('{} '.format(' '.join(['{:4.1f}'.format(x) for x in self.pressures]))) 
		data += ('{} '.format(' '.join(['{:4.1f}'.format(x) for x in self.light_levels]))) 
		data += ('{} '.format(' '.join(['{}'.format(x) for x in self.rgbs]))) 
		data += ('{} '.format(' '.join(['{:4.1f}'.format(x) for x in self.irs]))) 
		data += ('\n')
		
		with open(self.log_file_name, 'a') as logfile:
			logfile.write(data)

	def set_status_finished(self):
		self.update_thread.stop()
	
		self.finish_experiment_icon.set_from_file(configs['CLOSE_TAB_ICON'])
		self.finish_experiment_button.set_sensitive(True)
		self.finish_experiment_button.disconnect(self.handler_id)
		self.finish_experiment_button.connect('clicked', self.close)
	
		self.status_text = ''
		self.elapsed_time = self.group.group_process.get_elapsed_time()
		self.elapsed_time_text = str(timedelta(seconds=self.elapsed_time)).split('.')[0]
		self.remaining_time_text = '--:--:--'

		self.values['current_cycle'].set_text('--')
		self.values['elapsed_time'].set_text(self.elapsed_time_text)
		self.values['remaining_time'].set_text(self.remaining_time_text)
		self.progress_bar.set_fraction(1.0)
		self.values['light_level'].set_text('--')
		self.values['temperature'].set_text('--')
		self.values['humidity'].set_text('--')
		self.values['air_quality'].set_text('--')

		# Gray out all info and widgets (except button)
		self.progress_bar.set_sensitive(False)
		self.values['current_cycle'].set_sensitive(False)
		self.values['elapsed_time'].set_sensitive(False)
		self.values['remaining_time'].set_sensitive(False)
		self.values['light_level'].set_sensitive(False)
		self.values['temperature'].set_sensitive(False)
		self.values['humidity'].set_sensitive(False)
		self.values['air_quality'].set_sensitive(False)

		# Make sure cell buttons are updated
		for id in self.group.parameters['designated_cells_ids']:
			self.gui.update_cell_icon(self.menuitem, id)

	def close(self, widget):
		self.grid.destroy()
		logger.info('Tab {} closed.'.format(self.group.parameters['name']))

