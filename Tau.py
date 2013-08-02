import sublime, sublime_plugin 
import json
import time
import os
import datetime
from math import floor, ceil








class TauHelper(sublime_plugin.WindowCommand):
	def __init__(self, *args):
		self.settings = sublime.load_settings('Tau.sublime-settings')
		self.path = sublime.packages_path() + '/Tau Time Tracker/'
		return None





	def write_current(self, json_object):
		json_file = open(self.path + self.settings.get('tmp_folder') + '/current.json', 'w')
		json.dump(json_object, json_file, False, True, True, True, None, 4)
		json_file.close()





	def write_log(self, date, json_object):
		json_file = open(self.path + self.settings.get('log_folder') + '/' + date + '.json', 'w')
		json.dump(json_object, json_file, False, True, True, True, None, 4)
		json_file.close()





	def get_tasks(self, date = None):
		if date is None:
			date = time.strftime("%Y-%m-%d")

		if os.path.exists(self.path + self.settings.get('log_folder') + '/' + date + '.json'):
			json_file = open(self.path + self.settings.get('log_folder') + '/' + date + '.json')
			tasks = json.load(json_file)
			json_file.close()
		else:
			tasks = []

		return tasks





	def start_task(self, task_name):
		json_object = {}
		json_object['task_name'] = task_name
		json_object['time'] = str(int(time.time()))

		self.write_current(json_object)

		time_str = time.strftime("%I:%M %p")
		sublime.status_message("* Starting task '%s' at %s" % (task_name, time_str))




	def get_log_days(self):
		retval = []
		today = time.strftime("%Y-%m-%d") + '.json'

		path = self.path + self.settings.get('log_folder') + '/'
		files = [ f for f in os.listdir(path) if f[0:1] != '.' ]
		files.sort()

		for f in files:
			if f is today:
				continue
	
			date = datetime.date(int(f[0:4]), int(f[5:7]), int(f[8:10]))

			formatted = date.strftime('%B, %d, %Y')
			retval.append([f, formatted])

		return retval




	def delete_logs(self):
		retval = []
		today = time.strftime("%Y-%m-%d") + '.json'

		path = self.path + self.settings.get('log_folder') + '/'
		files = [ f for f in os.listdir(path) if f[0:1] != '.' and f != today ]
		
		for f in files:
			os.remove(path + f)



	def start_existing_task(self, index):
		tasks = self.get_tasks()
		self.start_task(tasks[index]['task_name'])





	def has_current_task(self):
		if not os.path.exists(self.path + self.settings.get('tmp_folder') + '/current.json'):
			return False

		json_file = open(self.path + self.settings.get('tmp_folder') + '/current.json')
		current = json.load(json_file)
		json_file.close()

		if 'task_name' in current:
			return current['task_name']

		return False





	def stop_task(self):
		if not self.has_current_task():
			return

		tasks = self.get_tasks()
		date = time.strftime("%Y-%m-%d")

		json_file = open(self.path + self.settings.get('tmp_folder') + '/current.json')
		current = json.load(json_file)
		json_file.close()

		end_time = int(time.time())
		start_time = int(current['time'])
		
		task = {}
		task['task_time'] = str(int(ceil((end_time - start_time) / 60)))
		task['task_name'] = current['task_name']

		existing_task = False
		for item in tasks:
			if item['task_name'] == current['task_name']:
				item['task_time'] = str(int(item['task_time']) + int(task['task_time']))
				existing_task = True
				break

		time_str = time.strftime("%I:%M %p")
		total_minutes = int(task['task_time'])
		hours = floor(total_minutes / 60)
		minutes = total_minutes - (hours * 60)

		sublime.status_message("* Stopping task '%s' at %s (total duration: %01dh%02d)" % (task['task_name'], time_str, hours, minutes))

		if not existing_task:
			tasks.append(task)

		self.write_log(date, tasks)

		# empty current.json
		json_object = {}
		self.write_current(json_object)





# ------------------------------------------------------






class TauListTasks(TauHelper):
	def run(self):
		tasks = self.get_tasks()

		menu_items = []
		for item in tasks:
			total_minutes = int(item['task_time'])

			hours = floor(total_minutes / 60)
			minutes = total_minutes - (hours * 60)

			menu_items.append('%02dh%02d | %s' % (hours, minutes, item['task_name']))
			
		if len(menu_items) == 0:
			sublime.error_message('You haven\'t done anything today !')
		else:
			sublime.active_window().show_quick_panel(menu_items, self.on_done)


	def on_done(self, index):
		if index != -1:
			tn = self.has_current_task()
			if tn is not False:
				sublime.error_message('You must stop the current task (%s) before starting a new one.' % tn)
			else:
				self.start_existing_task(index)







class TauStartTask(TauHelper):
	def run(self):
		tn = self.has_current_task()
		if tn is not False:
			sublime.error_message('You must stop the current task (%s) before starting a new one.' % tn)
		else:
			 sublime.active_window().show_input_panel('Task name : ', '', self.on_done, None, None)


	def on_done(self, input):
		if len(input.strip()):
			self.start_task(input.strip())
		else:
			sublime.error_message('Enter the name of the task.')









class TauStopTask(TauHelper):
	def run(self):
		self.stop_task()


	def is_enabled(self):
		return self.has_current_task()








class TauListLogs(TauHelper):
	def run(self):
		self.days = self.get_log_days()
		if len(self.days) > 0:
			menu_items = ['-- Delete the logs']
			for day in self.days:
				menu_items.append(day[1])

			sublime.active_window().show_quick_panel(menu_items, self.on_selection)
		else:
			sublime.error_message('There are not logs for the previous days.')


	def on_selection(self, index):
		if index == 0:
			if sublime.ok_cancel_dialog("Do you really want to delete the tasks logs ?") == True:
				self.delete_logs()
		elif index > 0:
			date = self.days[index - 1][0]
			date = date[0:10]
			tasks = self.get_tasks(date)

			date = datetime.date(int(date[0:4]), int(date[5:7]), int(date[8:10]))
			formatted = date.strftime('%B, %d, %Y')

			window = sublime.active_window()
			views = window.views()
			view = window.new_file()
			view.set_name('Tau Time Tracker')
			view.set_scratch(True)
			edit = view.begin_edit()
			

			output = 'Day: %s\n\n' % formatted
			output += 'Tasks\n'
			output += '--------------------\n'
			for item in tasks:
				total_minutes = int(item['task_time'])

				hours = floor(total_minutes / 60)
				minutes = total_minutes - (hours * 60)

				output += '%02dh %02dm | %s\n' % (hours, minutes, item['task_name'])
		


			
			view.insert(edit, view.size(), output)
			view.end_edit(edit)

			window.focus_view(view)
