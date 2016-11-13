#!/usr/bin/env python3

import speech_recognition as sr
from bs4 import BeautifulSoup
import requests, time, re, json, os, subprocess, urllib.request, zipfile, webbrowser
from datetime import datetime

# this is called from the background thread
def callback(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        recognized = recognizer.recognize_google(audio)
        if 'cs61a instructions' in recognized:
            if len(incomplete_assignments):
                webbrowser.open("http://cs61a.org/"+incomplete_assignments[0]['link'])
        elif 'cs61a' in recognized:

            if len(incomplete_assignments):
                try:
                    print(cs61a_folder+incomplete_assignments[0]['link']+incomplete_assignments[0]['link'][incomplete_assignments[0]['link'].index('/')+1:-1]+'.py')
                    os.startfile(cs61a_folder+incomplete_assignments[0]['link']+incomplete_assignments[0]['link'][incomplete_assignments[0]['link'].index('/')+1:-1]+'.py')
                except OSError:
                    try:
                        os.startfile(cs61a_folder+incomplete_assignments[0]['link']+incomplete_assignments[0]['link'][incomplete_assignments[0]['link'].index('/')+1:-1]+'.scm')
                    except Exception as e:
                        print("Error"+e)
            else:
                webbrowser.open("http://cs61a.org")

        else:
            print("that doesnt matter")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

def start_listening():
    r = sr.Recognizer()
    m = sr.Microphone()
    with m as source:
        r.adjust_for_ambient_noise(source) # we only need to calibrate once, before we start listening
        print("Start")

    # start listening in the background (note that we don't have to do this inside a `with` statement)
    stop_listening = r.listen_in_background(m, callback)
    # `stop_listening` is now a function that, when called, stops background listening


def get_assignments():
    try:
        page = requests.get('http://cs61a.org')
        tree = BeautifulSoup(page.text, 'html.parser')
        data  = tree.find_all("script")[-1].string
        p = re.compile('var assignments = (.*?);')
        m = p.search(data)
        assignments = json.loads(m.groups()[0])
        return assignments
    except:
        print("Internet not Found")
        return []

def find_current_assignments(assignments):
    today = datetime.now()
    current = []
    for a in assignments:
        release_date = datetime.strptime(a['release'], "%m/%d/%y")
        due_date = datetime.strptime(a['due'], "%m/%d/%y")
        if today >= release_date and today <= due_date:
            current.append(a)
    return current

def get_immediate_subdirectories(dir):
    return [dI for dI in os.listdir(dir) if os.path.isdir(os.path.join(dir,dI))]

def reinit():
    global assignments, current_assignments, incomplete_assignments
    assignments = get_assignments()
    current_assignments = find_current_assignments(assignments)
    incomplete_assignments = check_assignment_completion(cs61a_folder, current_assignments)


def check_assignment_completion(folder, current_assignments):
    incomplete_assignments = []
    for assignment in current_assignments:
        print(assignment)
        if os.path.isdir(folder+assignment['link']):
            if 'hw' in assignment['link']:
                for dir in get_immediate_subdirectories(folder+assignment['link']):
                    os.chdir(folder+assignment['link']+dir)
                    try:
                        #output = subprocess.check_output("python ok")
                        cmd = subprocess.Popen('python ok', stdout=subprocess.PIPE)
                        output, cmd_err = cmd.communicate()
                        output = str(output)
                    except:
                        output = "f"
                        print("hello")
                    if "No cases failed" not in str(output) and "There are still locked tests!" not in output:
                        incomplete_assignments.append(assignment)
            else:
                os.chdir(folder+assignment['link'])
                try:
                    cmd = subprocess.Popen('python ok', stdout=subprocess.PIPE)
                    output, cmd_err = cmd.communicate()
                    output = str(output)
                except:
                    output = "f"

                if "No cases failed" not in str(output) or "There are still locked tests!" in str(output):
                    incomplete_assignments.append(assignment)
                else:
                    print(assignment)               
        else:
            file = urllib.request.URLopener()
            file.retrieve("http://cs61a.org/"+assignment['link'][:-1]+assignment['link'][assignment['link'].index('/'):-1]+'.zip', folder+assignment['link'][:-1]+'.zip')
            zipfile.ZipFile(folder+assignment['link'][:-1]+'.zip').extractall(folder+assignment['link'][:assignment['link'].index('/')])
            os.remove(folder+assignment['link'][:-1]+'.zip')
            incomplete_assignments.append(assignment)
    return incomplete_assignments



if __name__ == "__main__":
    cs61a_folder = "C:/Users/Kartikye Mittal/OneDrive/Documents/cs61a/"
    assignments = get_assignments()
    current_assignments = find_current_assignments(assignments)
    incomplete_assignments = check_assignment_completion(cs61a_folder, current_assignments)
    print("Incomplete Assignments")
    print(incomplete_assignments)

    start_listening()

    # do some other computation for 5 seconds, then stop listening and keep doing other computations
    while True: time.sleep(0.1)