import api
import requests
import getpass
import os
import pickle

class Application:
	def __init__(self, args):
		self.sess = requests.Session()
		self.api = api.API(self.sess)
		self.args = args

		if os.path.exists("session_cache"):
			with open("session_cache", "rb") as f:
				self.sess.cookies.update(pickle.load(f))


	def clear(self):
		print("\033[2J\033[H")


	def login_prompt(self):
		while not self.api.is_logged_in():
			print("The login requires an itslearning account.")
			email = input("Email: ")
			password = getpass.getpass("Password: ")

			if not self.api.login(email, password):
				print("Error: try again.")


		with open("session_cache", "wb") as f:
			pickle.dump(self.sess.cookies, f)


	def list_courses(self):
		self.courses = self.api.get_courses()

		for i, course in enumerate(self.courses):
			print(f"[{i}] {course.title}")


	def select_course(self, index):
		self.selected_course = self.courses[index]


	def list_resources(self):
		print(self.api.get_root_folder_id(self.selected_course))
		#courses = self.api.get_resources(self.course)

		#for course in courses:
		#	print(course.title)


	def list_plans(self):
		plans = self.api.get_plans(self.selected_course)
		for i, topic in enumerate(plans.topics):
			print(f"[{i}] {topic.title}")

		return
			# for topic_item in topic:
			# 	print("------------------------------------")
			# 	print(topic_item.title)
			# 	print(topic_item.description.strip())
			# 	print(topic_item.links[0])


	def save_file(self, path, href):
		r = sess.get("https://resource.itslearning.com" + href)

		with open(path, "wb") as f:
			f.write(r.content)