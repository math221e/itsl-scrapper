#!/usr/bin/env python3
import requests
import os
import getpass
import pickle
import time
from bs4 import BeautifulSoup

url = "https://sdu.itslearning.com"

def clear():
	print("\033[2J\033[H")

def elip(text, lim = 35):
	if len(text) > lim:
		return (text[0:(lim//2)] + "..." + text[-((lim-3)//2)::])

	return text


def list_folder(sess, folderid):
	r = sess.get('https://sdu.itslearning.com/Folder/processfolder.aspx?FolderID=' + folderid)
	soup = BeautifulSoup(r.text, "html.parser")
	table = soup.find(id="ctl00_ContentPlaceHolder_ProcessFolderGrid_T")

	ths = table.find_all("th")
	trs = table.find_all("tr")

	print("\t", end="")

	for th in ths[:2]:
		print(th.text, end="\t")

	counter = 1
	folders = []

	for tr in trs:
		tds = tr.find_all("td")
		link = tr.find("a", class_="GridTitle")
		folderid = "0"

		if link is not None:
			folderid = link.get("href").split("=")[1]

		for td in tds[:2]:
			img = td.find("img")

			if img is None:
				print(elip(td.text), end="\t")
			else:
				if img.get("alt") == "Folder":
					print("[" + str(counter) + "]", end="")
					counter += 1
					folders.append([folderid, tds[1].text])

				print(end="\t")
				print(img.get("alt"), end="\t")
		print()

	return folders


def is_logged_in(sess):
	r = sess.get("https://sdu.itslearning.com/Person/ChangeDetails.aspx")
	soup = BeautifulSoup(r.text, "html.parser")
	title = soup.find("title")

	if title.text != "":
		return True

	return False

def login(sess):
	if os.path.exists("session_cache"):
		with open("session_cache", "rb") as f:
			sess.cookies.update(pickle.load(f))


	if is_logged_in(sess):
		return

	print("The login requires an itslearning account.")
	email = input("Email: ")
	password = getpass.getpass("Password: ")

	payload = {
		'ctl00$ContentPlaceHolder1$Username$input': email,
		'ctl00$ContentPlaceHolder1$Password$input': password
	}

	print("Logging in...")

	r = sess.get("https://sdu.itslearning.com/index.aspx")
	soup = BeautifulSoup(r.text, "html.parser")
	inputs = soup.find_all("input")

	for i in inputs:
		name = i.get("name")

		if name == "ctl00$ContentPlaceHolder1$Username$input" or name == "ctl00$ContentPlaceHolder1$Password$input":
			continue

		payload[name] = i.get("value")


	r = sess.post("https://sdu.itslearning.com/index.aspx", data=payload)

	if is_logged_in(sess) == False:
		print("Error logging in.")
		exit()

	with open("session_cache", "wb") as f:
		pickle.dump(sess.cookies, f)


def select_course(sess):
	r = sess.get("https://sdu.itslearning.com/TopMenu/TopMenu/GetCourses")

	courses = BeautifulSoup(r.text, "html.parser")
	courses = courses.find_all("li")

	print("Select a course: ")

	for index, course in enumerate(courses):
		print("[" + str(index+1) + "] " + course.get("data-title"))

	print("Enter course number: ", end="")
	x = input()

	r = sess.get("https://sdu.itslearning.com" + courses[int(x) - 1].find("a").get("href"))
	soup = BeautifulSoup(r.text, "html.parser")
	link = soup.find(id="link-resources").get("href")
	#r = sess.get(link)
	#soup = BeautifulSoup(r.text, "html.parser")
	return [link.split("=")[1], courses[int(x) - 1].get("data-title")]


def download_folder(sess, folderid, breadcrumb, recursive = False):
	path = "downloads/"

	for folder in breadcrumb:
		path += folder + "/"

		if not os.path.exists(path):
			os.makedirs(path)


	r = sess.get('https://sdu.itslearning.com/Folder/processfolder.aspx?FolderID=' + folderid)
	soup = BeautifulSoup(r.text, "html.parser")
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
		r = sess.get(url + href)
		soup = BeautifulSoup(r.text, "html.parser")
		iframe = soup.find(id="ctl00_ContentPlaceHolder_ExtensionIframe")

		if iframe is None:
			continue

		r = sess.get(iframe.get("src"))
		soup = BeautifulSoup(r.text, "html.parser")
		link = soup.find(id="ctl00_ctl00_MainFormContent_DownloadLinkForViewType")

		if link is None:
			continue

		href = link.get("href")
		r = sess.get("https://resource.itslearning.com" + href)
		print("Saving: ", path + filename)

		with open(path + filename, "wb") as f:
			f.write(r.content)


def print_breadcrumb(breadcrumb):
	print("Path: ", end="")

	for index, item in enumerate(breadcrumb):
		print(elip(item, 20), end="")

		if index + 1 < len(breadcrumb):
			print(" > ", end="")

	print()

def hr():
	print("-----------------------------")

if __name__ == "__main__":
	clear()

	if not os.path.exists("downloads"):
		os.makedirs("downloads")

	while True:
		with requests.Session() as sess:
			login(sess)
			clear()
			course = select_course(sess)
			folderids = [course[0]]
			breadcrumb = [course[1]]
			clear()

			x = ""

			while x != "q":
				clear()
				hr()
				print_breadcrumb(breadcrumb);
				hr()
				folders = list_folder(sess, folderids[-1])
				hr()
				x = input("(b)ack/(d)ownload/(r)ecursive download/(q)uit/[number]: ")

				if x == "b":
					if len(folderids) > 1:
						folderids.pop()
						breadcrumb.pop()
					else:
						break
				elif x == "d":
					clear()
					download_folder(sess, folderids[-1], breadcrumb)
					print("Finished.")
					x = input("Press any key...")
				elif x == "r":
					clear()
					download_folder(sess, folderids[-1], breadcrumb, True)
					print("Finished.")
					x = input("Press enter...")
				elif x == "q":
					exit()
				else:
					folderids.append(folders[int(x) - 1][0])
					breadcrumb.append(folders[int(x) - 1][1])
