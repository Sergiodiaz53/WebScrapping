from requests import Session
from robobrowser import RoboBrowser
from pprint import pprint
from bs4 import BeautifulSoup
from time import sleep
import random
import json
import csv
import time
import gc

def main():
	# User information
	username = 'myusername'
	password = 'mypassword'
	url = 'myurl'

	# Create session and browser
	session = Session()
	browser = RoboBrowser(session=session,history=False)
	browser.open(url)

	#Log into server
	form = browser.get_form(action="authorization")
	form['authorization[name]'] = username
	form['authorization[password]'] = password
	browser.session.headers['Referer'] = url
	browser.submit_form(form)

	step = 0
	start_time = time.time()

	#Retrieve job info from X to Y (backwards)
	for x in range(1615590, 5383, -1):
		current_time = time.time()
		print("Retrieving job: ", step, "\t Time spent: ", round(current_time-start_time,2),  " seconds")

		#Prepare job URL
		url = myurl + str(x)

		try:
			#Open page, retrieve table with info and the submit script
			browser = RoboBrowser(session=session,history=False)
			browser.open(url)
			data = str(browser.select('table'))
			submit_script = browser.select('#job_text')[0].get_text(strip=True)

			soup = BeautifulSoup(data, 'html5lib')

			#Parse table information into Python dictionary
			retrievedDict = dict()
			for label in soup.select("tr"):
				if(label.select("td > strong")[0]):
					if(label.select("td")[1]):
						retrievedDict[label.select("td > strong")[0].get_text(strip=True)] = label.select("td")[1].get_text(strip=True)
					else:
						retrievedDict[label.select("td > strong")[0].get_text(strip=True)] = "NULL"

			retrievedDict["submit_script"] = submit_script

			#Dump job info in Json and CSV files
			with open('data.json', 'a') as output_json_file:
				json.dump(retrievedDict, output_json_file, sort_keys=True, indent=4)

			with open('data.csv', 'a') as output_csv_file:
				w = csv.writer(output_csv_file)
				if (step == 0): 
					w.writerow(retrievedDict.keys())
				w.writerow(retrievedDict.values())


		except(IndexError):
			print("ERROR: Index out of bounds exception (Missing job). Skipping.")
		except Exception as e:
			print("ERROR: There was a problem retriving a job.")
			print("Unexpected error: ", e)
			print("Skipping")

		
		#Free memory
		del browser
		gc.collect()

		#Wait random secs for next job
		sleep(round(random.uniform(0.6, 1.2), 2))
		step += 1

	end_time = time.time()

	print("Total time spent: ", round(end_time-start_time, 2), "with a total of", step, "jobs.")

if __name__ == "__main__":
	main()
