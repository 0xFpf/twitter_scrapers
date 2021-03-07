import tkinter
from tkinter import filedialog, Text, simpledialog, messagebox
import threading
import time
from sys import exit
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
import pandas
import os

#add these two lines for macOs, save the chromedriver in the parent of this file's folder, if the folder is on desktop put chromedriver on the desktop:
#DRIVER_PATH = os.path.abspath('..')+'/chromedriver'
#driver = webdriver.Chrome(DRIVER_PATH)

chromedriver_autoinstaller.install()
base_url= "https://www.twitter.com/login"
tweetdata=[]

#gathers data within tweet
def transform_tweet(card):
    try:
        username = card.find_element_by_xpath('.//span').text
    except NoSuchElementException:
        return
    try:
        handle   = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except NoSuchElementException:
        return
    try:
        link     = card.find_element_by_xpath('.//div[2]/div[1]/div/div/div[1]/a').get_attribute('href')
    except NoSuchElementException:
        return
    try:
        date     = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except NoSuchElementException:
        return
    comment      = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    in_reply_of  = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    tweetcontent = comment+''+in_reply_of 

    tweet = (username, handle, link, date, tweetcontent)
    print(tweet[2])
    return tweet

#main
def extract(email, password):
    driver= webdriver.Chrome("chromedriver.exe")
    driver.get(base_url)
    driver.implicitly_wait(5)
    
    #attempts login
    try:
        driver.find_element_by_xpath('//input[@name="session[username_or_email]"]').send_keys(email)# alt: //*[@id="react-root"]/div/div/div[2]/main/div/div/div[1]/form/div/div[1]/label/div/div[2]/div/input').send_keys(email)
    except ElementNotInteractableException:
        messagebox.showwarning("Error", "Error with Selenium, try again")
        driver.close()
        startScript.config(state='normal')
        exit()
    driver.find_element_by_xpath('//input[@name="session[password]"]').send_keys(password)          # alt: //*[@id="react-root"]/div/div/div[2]/main/div/div/div[1]/form/div/div[2]/label/div/div[2]/div/input
    driver.find_element_by_xpath('//div[@data-testid="LoginForm_Login_Button"]').click()            # alt: //*[@id="react-root"]/div/div/div[2]/main/div/div/div[1]/form/div/div[3]/div
    driver.implicitly_wait(5)
    time.sleep(2)
    try:
        driver.find_element_by_xpath('//a[@aria-label="Profile"]').click()                          # alt: //*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[5] or href="/i/bookmarks"
    except NoSuchElementException:
        messagebox.showwarning("Error", "Error with Twitter, try again using username")
        driver.close()
        startScript.config(state='normal')
        exit()
    time.sleep(2)

    # get all tweets on the page
    tweet_ids = set()
    last_position = driver.execute_script("return window.pageYOffset;")
    scrolling = True

    #scrolls & loads more tweets
    while scrolling:
        page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
        for card in page_cards[-15:]:
            tweet = transform_tweet(card)
            if tweet:
                tweet_id = tweet[2]
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    tweetdata.append(tweet)
                
        scroll_attempt = 0
        while True:
            # check scroll position
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            curr_position = driver.execute_script("return window.pageYOffset;")
            if last_position == curr_position:
                scroll_attempt += 1
                
                # end of scroll region
                if scroll_attempt >= 3:
                    scrolling = False
                    break
                else:
                    time.sleep(2) # attempt another scroll
            else:
                last_position = curr_position
                break

    # close the web driver
    driver.close()
    datafile = pandas.DataFrame(tweetdata)
    datafile.to_csv('ProfileTweets.csv')

    messagebox.showinfo("Confirmation Message","Finished, check the program folder for the csv file")
    startScript.config(state='normal')



def startThread():
    
    email=emailEntry.get()
    password=passwordEntry.get()
    
    startScript.config(state='disabled')
    
    #starts a separate thread for main so app can be quit
    threading.Thread(target=extract, args=(email, password), daemon=True).start()


def endThread():
    exit()

#GUI
root = tkinter.Tk()
root.title("Twitter Profile Scraper")

canvas = tkinter.Canvas(root, height=(216), width=(384), bg="#26292c")
canvas.pack()

frame= tkinter.Frame(root, bg="#26292c")
frame.place(relx=.1, rely=.1, relwidth=.8, relheight=.8)

#Input box
emailEntry=tkinter.Entry(frame, bg='#c5c7c4')
emailEntry.place(relx=.4, rely=.10, relwidth=.75, relheight=.15)

passwordEntry=tkinter.Entry(frame, bg='#c5c7c4')
passwordEntry.place(relx=.4, rely=.40, relwidth=.75, relheight=.15)

#Labels
emailL = tkinter.Label(frame, text="Email/User", padx=1, pady=1, fg="white", bg="#26292c")
emailL.place(relx=0, rely=.10, relwidth=.25, relheight=.15)

passwordL = tkinter.Label(frame, text="Password", padx=1, pady=1, fg="white", bg="#26292c")
passwordL.place(relx=0, rely=.40, relwidth=.25, relheight=.15)

#Buttons
startScript=tkinter.Button(frame, text="Activate Scraper", padx=10, pady=5, fg="white", bg="#52595d", command= startThread) 
startScript.place(relx=.05, rely=.8, relwidth=.4, relheight=.2)

endScript=tkinter.Button(frame, text="Quit Scraper", padx=10, pady=5, fg="white", bg="#52595d", command= endThread)
endScript.place(relx=.55, rely=.8, relwidth=.4, relheight=.2)

root.mainloop()
