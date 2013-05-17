import sublime, sublime_plugin 
import json
import time
import os
from math import floor, ceil








class TauHelper(sublime_plugin.WindowCommand):
	def __init__(self, *args):
		self.settings = sublime.load_settings('Tau.sublime-settings')
		self.path = sublime.packages_path() + '/Tau Time Tracker/'
		return None




	def get_tasks(self):
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

		json_file = open(self.path + self.settings.get('tmp_folder') + '/current.json', 'w')
		json.dump(json_object, json_file)
		json_file.close()

		time_str = time.strftime("%I:%M %p")
		sublime.status_message("* Starting task '%s' at %s" % (task_name, time_str))




	def start_existing_task(self, index):
		tasks = self.get_tasks()
		self.record_task(tasks[index]['task_name'])




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


		json_file = open(self.path + self.settings.get('log_folder') + '/' + date + '.json', 'w')
		json.dump(tasks, json_file)
		json_file.close()

		# empty current.json
		json_object = {}
		json_file = open(self.path + self.settings.get('tmp_folder') + '/current.json', 'w')
		json.dump(json_object, json_file)
		json_file.close()






# ------------------------------------------------------







class TauListTasks(TauHelper):
	def run(self):
		tasks = self.get_tasks()

		menu_items = []
		for item in tasks:
			total_minutes = int(item['task_time'])

			hours = floor(total_minutes / 60)
			minutes = total_minutes - (hours * 60)

			menu_items.append('%01dh%02d | %s' % (hours, minutes, item['task_name']))
			
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
			 sublime.active_window().show_input_panel('Task name : ', '', self.on_done, self.on_change, self.on_cancel)

	def on_done(self, input):
		if len(input.strip()):
			self.start_task(input.strip())
		else:
			sublime.error_message('Enter the name of the task.')

	def on_change(self, input):
		pass

	def on_cancel(self):
		pass





class TauStopTask(TauHelper):
	def run(self):
		self.stop_task()
