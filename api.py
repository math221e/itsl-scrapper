from bs4 import BeautifulSoup
from models import Course, Plan, TopicItem, Topic, Link
import json

class API:
	def __init__(self, sess):
		self.sess = sess

		self.urls = {
			"overview": "https://sdu.itslearning.com/Course/course.aspx?CourseId=",
			"plans": "https://sdu.itslearning.com/Planner/Planner.aspx?CourseID=",
			"resources": "https://sdu.itslearning.com/Folder/processfolder.aspx?FolderID=",
			"all_courses": "https://sdu.itslearning.com/Course/AllCourses.aspx",
			"menu_courses": "https://sdu.itslearning.com/TopMenu/TopMenu/GetCourses",
			"person_details": "https://sdu.itslearning.com/Person/ChangeDetails.aspx",
			"login": "https://sdu.itslearning.com/index.aspx",
			# LocationID is course_id
			"content_area": "https://sdu.itslearning.com/ContentArea/ContentArea.aspx?LocationType=1&LocationID=",
			# Topic is REST endpoint
			"topic": "https://sdu.itslearning.com/RestApi/planner/plan/multiple/forTopic"
		}

		self.ids = {
			"": "link-resources"
		}


	def get_soup(self, url):
		request = self.sess.get(url)
		soup = BeautifulSoup(request.text, "html.parser")

		return soup


	def is_logged_in(self):
		soup = self.get_soup(self.urls["person_details"])
		title = soup.find("title")

		if title.text != "":
			return True

		return False


	def login(self, email, password):
		payload = {}
		soup = self.get_soup(self.urls["login"])
		inputs = soup.find_all("input")

		for i in inputs:
			name = i.get("name")
			payload[name] = i.get("value")


		payload["ctl00$ContentPlaceHolder1$Username$input"] = email
		payload["ctl00$ContentPlaceHolder1$Password$input"] = password

		r = self.sess.post(self.urls["login"], data=payload)

		return self.is_logged_in()


	def get_plans(self, course):
		soup = self.get_soup(self.urls["plans"] + course.course_id)
		topics = soup.find_all(class_="itsl-topic")
		topic_titles = []
		topic_ids = []

		for topic in topics:
			topic_titles.append(topic.find(class_="itsl-topic-title").text.strip())
			topic_ids.append(topic.get("data-topic-id"))


		payload = {
			"isSearching": False,
			"searchText": "",
			"pageNumber": 1,
			"pageSize": 25,
			"sort":"Order:asc",
			"filter": "",
			"chunkNumber": 0,
			"chunkSize": 15,
			"courseId": course.course_id,
			"topicId": "",
			"start": "",
			"end": "",
			"childId": "0",
			"dashboardHierarchyId": "0",
			"dashboardName": "",
			"currentDisplayMode": "0"
		}

		topics = []

		for topic_id, topic_title in zip(topic_ids, topic_titles):
			payload["topicId"] = topic_id

			response = self.sess.post(self.urls["topic"], json=payload)
			data = json.loads(response.text)
			grid = data["gridData"]
			soup = BeautifulSoup(grid, "html.parser")
			rows = soup.find_all(class_="gridrow")
			topic_items = []

			for row in rows:
				title = row.find(class_="itsl-plan-title-label").text
				date = row.find(class_="itsl-plan-date").text
				description = row.find(class_="itsl-planner-htmltext-viewer").text
				links = row.find_all(class_="itsl-plan-elements-item-link")
				links_url = [ link.get("href") for link in links ]
				links_text = [ link.find("span").text for link in links ]
				
				if "Student guides" in title:
					continue


				links = [ Link(text=text, url=url) for (text, url) in zip(links_text, links_url) ]

				topic_items.append(TopicItem(title=title, description=description, links=links))
			

			topic = Topic(title=topic_title, topic_items=topic_items)
			topics.append(topic)

		plans = Plan(topics=topics)

		return plans

	def get_courses(self):
		soup = self.get_soup(self.urls["menu_courses"])
		items = soup.find_all("li")
		courses = []

		for item in items:
			title = item.get("data-title")
			course_id = item.find("a").get("href").split("=")[1]

			courses.append(Course(title=title, course_id=course_id))


		return courses


	def get_root_folder_id(self, course):
		soup = self.get_soup(self.urls["content_area"] + course.course_id)
		href = soup.find(id="link-resources").get("href")
		folder_id = href.split("=")[1]

		return folder_id


	def get_resources(self, course, folderid = None, recursive = False):
		# Needs to be rewritten
		path = "downloads/"

		if folderid == None:
			folderid = self.get_root_folder_id(course)

		for folder in breadcrumb:
			path += folder + "/"

			if not os.path.exists(path):
				os.makedirs(path)


		soup = self.get_soup("https://sdu.itslearning.com/Folder/processfolder.aspx?FolderID=" + folderid)
		table = soup.find(id="ctl00_ContentPlaceHolder_ProcessFolderGrid_T")
		trs = table.find_all("tr")

		for tr in trs:
			tds = tr.find_all("td")
			link = tr.find("a", class_="GridTitle")
			folderid = "0"

			if link is None:
				continue

			img = tds[0].find("img")

			if img is None:
				continue

			if img.get("alt") == "Folder" and recursive == True:
				breadcrumb.append(link.text)
				download_folder(sess, link.get("href").split("=")[1], breadcrumb, True)
				breadcrumb.pop()


			href = link.get("href")
			filename = link.text
			soup = self.get_soup(url + href)
			iframe = soup.find(id="ctl00_ContentPlaceHolder_ExtensionIframe")

			if iframe is None:
				continue

			soup = self.get_soup(iframe.get("src"))
			link = soup.find(id="ctl00_ctl00_MainFormContent_DownloadLinkForViewType")

			if link is None:
				continue

			href = link.get("href")
			r = sess.get("https://resource.itslearning.com" + href)
			print(href)
			print("Saving: ", path + filename)

			with open(path + filename, "wb") as f:
				f.write(r.content)
			