commit ad5d8207c36d6c848f1ef21a68517e675803d90f
Author: und1f <bash88@gmail.com>
Date:   Mon Apr 8 19:43:26 2013 -0400

    initial commit

diff --git a/Default.sublime-keymap b/Default.sublime-keymap
new file mode 100644
index 0000000..929c441
--- /dev/null
+++ b/Default.sublime-keymap
@@ -0,0 +1,14 @@
+[
+	{
+		"keys": ["ctrl+shift+1"],
+		"command": "tau_list_tasks"
+	},
+	{
+		"keys": ["ctrl+shift+2"],
+		"command": "tau_start_task"
+	},
+	{
+		"keys": ["ctrl+shift+3"],
+		"command": "tau_stop_task"
+	}
+]
diff --git a/Main.sublime-menu b/Main.sublime-menu
new file mode 100644
index 0000000..7904cf5
--- /dev/null
+++ b/Main.sublime-menu
@@ -0,0 +1,31 @@
+[
+	{
+		"caption": "Tools",
+		"mnemonic": "t",
+		"id": "tools",
+		"children":
+		[
+			{
+				"caption": "Tau Time Tracker",
+				"mnemonic": "t",
+				"id": "tau",
+				"children":
+				[
+					{
+						"command": "tau_list_tasks", 
+						"caption": "List tasks"
+					},
+					{
+						"command": "tau_start_task", 
+						"caption": "Start a new task"
+					},
+					{
+						"command": "tau_stop_task", 
+						"caption": "Stop the current task"
+					}
+				]
+			}
+		]
+	}
+]
+
diff --git a/README.md b/README.md
new file mode 100644
index 0000000..bdc7ae0
--- /dev/null
+++ b/README.md
@@ -0,0 +1,20 @@
+# Sublime Text 2 Tau Time Tracker Plugin
+
+A simple plugin to track your time.
+
+## Install
+
+Use the [Sublime Package Manager](http://wbond.net/sublime_packages/package_control) to install.
+
+## Keybindings
+
+* Ctrl + Shift + 1: List the tasks (You can add time to a task by clicking on it)
+* Ctrl + Shift + 2: Start a new task
+* Ctrl + Shift + 3: Stop the current task
+
+You can only view the current day's tasks.  
+Everything is logged in the logs folder.
+
+# License
+
+Tau Time Tracker is licensed under the MIT License.
\ No newline at end of file
diff --git a/Tau.py b/Tau.py
new file mode 100644
index 0000000..ee8203a
--- /dev/null
+++ b/Tau.py
@@ -0,0 +1,177 @@
+import sublime, sublime_plugin 
+import json
+import time
+import os
+from math import floor, ceil
+
+
+
+
+
+
+
+
+class TauHelper(sublime_plugin.WindowCommand):
+	def __init__(self, *args):
+		self.settings = sublime.load_settings('Tau.sublime-settings')
+		self.path = os.path.dirname(os.path.abspath(__file__)) + '/'
+		return None
+
+
+	def get_tasks(self):
+		date = time.strftime("%Y-%m-%d")
+
+		if os.path.exists(self.path + self.settings.get('log_folder') + '/' + date + '.json'):
+			json_file = open(self.path + self.settings.get('log_folder') + '/' + date + '.json')
+			tasks = json.load(json_file)
+			json_file.close()
+		else:
+			tasks = []
+
+		return tasks
+
+
+	def start_task(self, task_name):
+		json_object = {}
+		json_object['task_name'] = task_name
+		json_object['time'] = str(int(time.time()))
+
+		json_file = open(self.path + self.settings.get('tmp_folder') + '/current.json', 'w')
+		json.dump(json_object, json_file)
+		json_file.close()
+
+
+	def start_existing_task(self, index):
+		tasks = self.get_tasks()
+		self.record_task(tasks[index]['task_name'])
+
+
+
+	def has_current_task(self):
+		json_file = open(self.path + self.settings.get('tmp_folder') + '/current.json')
+		current = json.load(json_file)
+		json_file.close()
+
+		if 'task_name' in current:
+			return current['task_name']
+
+		return False
+
+
+
+	def stop_task(self):
+		if not self.has_current_task():
+			return
+
+
+		tasks = self.get_tasks()
+		date = time.strftime("%Y-%m-%d")
+
+		json_file = open(self.path + self.settings.get('tmp_folder') + '/current.json')
+		current = json.load(json_file)
+		json_file.close()
+
+
+		end_time = int(time.time())
+		start_time = int(current['time'])
+		
+		task = {}
+		task['task_time'] = str(int(ceil((end_time - start_time) / 60)))
+		task['task_name'] = current['task_name']
+
+
+		existing_task = False
+		for item in tasks:
+			if item['task_name'] == current['task_name']:
+				item['task_time'] = str(int(item['task_time']) + int(task['task_time']))
+				existing_task = True
+				break
+
+
+		if not existing_task:
+			tasks.append(task)
+
+
+		json_file = open(self.path + self.settings.get('log_folder') + '/' + date + '.json', 'w')
+		json.dump(tasks, json_file)
+		json_file.close()
+
+		# empty current.json
+		json_object = {}
+		json_file = open(self.path + self.settings.get('tmp_folder') + '/current.json', 'w')
+		json.dump(json_object, json_file)
+		json_file.close()
+
+
+
+
+
+
+# ------------------------------------------------------
+
+
+
+
+
+
+
+class TauListTasks(TauHelper):
+	def run(self):
+		tasks = self.get_tasks()
+
+		menu_items = []
+		for item in tasks:
+			total_minutes = int(item['task_time'])
+
+			hours = floor(total_minutes / 60)
+			minutes = total_minutes - (hours * 60)
+
+			menu_items.append('%01dh%02d | %s' % (hours, minutes, item['task_name']))
+			
+		if len(menu_items) == 0:
+			sublime.error_message('You haven\'t done anything today !')
+		else:
+			sublime.active_window().show_quick_panel(menu_items, self.on_done)
+
+
+	def on_done(self, index):
+		if index != -1:
+			tn = self.has_current_task()
+			if tn is not False:
+				sublime.error_message('You must stop the current task (%s) before starting a new one.' % tn)
+			else:
+				self.start_existing_task(index)
+
+
+
+
+
+
+
+class TauStartTask(TauHelper):
+	def run(self):
+		tn = self.has_current_task()
+		if tn is not False:
+			sublime.error_message('You must stop the current task (%s) before starting a new one.' % tn)
+		else:
+			 sublime.active_window().show_input_panel('Task name : ', '', self.on_done, self.on_change, self.on_cancel)
+
+	def on_done(self, input):
+		if len(input.strip()):
+			self.start_task(input.strip())
+		else:
+			sublime.error_message('Enter the name of the task.')
+
+	def on_change(self, input):
+		pass
+
+	def on_cancel(self):
+		pass
+
+
+
+
+
+class TauStopTask(TauHelper):
+	def run(self):
+		self.stop_task()
diff --git a/Tau.pyc b/Tau.pyc
new file mode 100644
index 0000000..6bd8bbd
Binary files /dev/null and b/Tau.pyc differ
diff --git a/Tau.sublime-settings b/Tau.sublime-settings
new file mode 100644
index 0000000..759e419
--- /dev/null
+++ b/Tau.sublime-settings
@@ -0,0 +1,4 @@
+{
+	"log_folder": "./logs",
+	"tmp_folder": "./tmp"
+}
diff --git a/tmp/current.json b/tmp/current.json
new file mode 100644
index 0000000..9e26dfe
--- /dev/null
+++ b/tmp/current.json
@@ -0,0 +1 @@
+{}
\ No newline at end of file
