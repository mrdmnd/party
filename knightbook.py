''' A module designed to scrape student information from Menlo's Knightbook. '''
''' Produces a file "class_to_student_mapping.json" '''
''' Used as input for partitioner program. '''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import json

username = input("Okta Username: ")
password = input("Okta Password: ")

driver = webdriver.Chrome()
driver.get("http://kb.menloschool.org")
driver.implicitly_wait(3)

# Setup UN + PW login.
elem = driver.find_element_by_name("username")
elem.clear()
elem.send_keys(username)
elem = driver.find_element_by_name("password")
elem.clear()
elem.send_keys(password)
elem.send_keys(Keys.RETURN)
time.sleep(3)

# Setup text authentication
elem = driver.find_element_by_class_name("sms-request-button")
elem.click()
# Block for SMS to arrive.
sms_code = input("Code from text: ")
elem = driver.find_element_by_name("answer")
elem.send_keys(sms_code)
elem.send_keys(Keys.RETURN)
time.sleep(3)

# Get list of all classes. Iterate through these classes by filling in the selector.
class_to_student_map = {}

elem = driver.find_element_by_class_name("class-list-holder")
class_links = elem.find_elements_by_tag_name("a")[1:]
num_classes = len(class_links)

# For some reason, PE Tennis is unclickable?
blacklist = ["PE Tennis",]
for index, link in enumerate(class_links):
    print(str(index) + " / " + str(num_classes))
    # Click filter option
    driver.find_element_by_id("class-enrollment-selection").click()

    # data-value is unique "key" for class - we append class name to it for readability.
    key = link.get_attribute("data-value") + " - " + link.get_attribute("data-classname")
    for broken_class in blacklist:
        if (link.get_attribute("data-classname").contains(broken_class)):
            print("Skipping blacklisted class: " + key)
            continue

    print(key)
    try:
        link.click()
        time.sleep(2)
        # Get a list of all students that are not set to display: inline-block. These are the students in the class.
        container = driver.find_element_by_id("container")
        soup = BeautifulSoup(container.get_attribute("innerHTML"), 'html.parser')
        student_boxes = soup.find_all("div", {"class": "student-box"})
        students = [student_box.get('data-name') for student_box in student_boxes if student_box.get('style') != "display: none;"]
        print(students)
        class_to_student_map[key] = students
    except:
        print("Tried to click too soon, skipping this class.")
        continue

with open('class_to_student_mapping.json', 'w') as f:
    json.dump(class_to_student_map, f)
