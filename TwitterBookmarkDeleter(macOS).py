import tkinter
from tkinter import filedialog, Text, simpledialog, messagebox
import threading
import time
import chromedriver_autoinstaller
from sys import exit
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
import pandas
import os


chromedriver_autoinstaller.install()

base_url= "https://www.twitter.com/login"
tweetdata=[]

#gathers data within tweet
def transform_tweet(card):
    try:
        card.find_element_by_xpath('//div[@aria-label="Share Tweet"]').click()
    except NoSuchElementException:
        messagebox.showwarning("Error", "Error with Twitter #12, still working the kinks out")
    print("success 1")
    return


#main
def extract(email, password):
    DRIVER_PATH = os.path.abspath(path_var)+'/chromedriver'
    driver = webdriver.Chrome(DRIVER_PATH)
    driver.get(base_url)
    driver.implicitly_wait(5)
    time.sleep(1)
    global counter
    counter=0
    
    #attempts login
    try:
        driver.find_element_by_xpath('//input[@name="session[username_or_email]"]').send_keys(email) # alt: //*[@id="react-root"]/div/div/div[2]/main/div/div/div[1]/form/div/div[1]/label/div/div[2]/div/input').send_keys(email)
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
        driver.find_element_by_xpath('//a[@aria-label="Bookmarks"]').click()                        # alt: //*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[5] or href="/i/bookmarks"
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

    #scrolls & loads more tweet
    attempt=0
    while scrolling:
        print("a")
        attempt+=1
        page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
        for card in page_cards[-15:]:
            time.sleep(.5)
            try:
                card.find_element_by_xpath('//div[@aria-label="Share Tweet"]').click()
            except:
                print("exception1")
                pass
            try:
                time.sleep(.5)
                driver.find_element_by_xpath('.//span[contains(text(), "Remove Tweet from Bookmarks")]').click()
                counter+=1
                CountLN.config(text=counter)
                print("count:",counter)
                print("success 2")
                pass
            except:
                print("exception2")
                pass
            print("cycle")
        
        if attempt >= 20:
            scrolling = False
            break
        else:
            time.sleep(.2) # attempt again
                
        

    # close the web driver
    driver.close()

    messagebox.showinfo("Confirmation Message","Finished deleting bookmarks")
    startScript.config(state='normal')


# FPF_CONSULTANCY
def startThread():
    path_var=pathEntry.get()            #IMPORTANT FOR MACS
    email=emailEntry.get()
    password=passwordEntry.get()
    
    startScript.config(state='disabled')
    
    #starts a separate thread for main so app can be quit
    threading.Thread(target=extract, args=(email, password), daemon=True).start()


def endThread():
    exit()


#GUI
root = tkinter.Tk()
root.title("Twitter Bookmarks Deleter")

canvas = tkinter.Canvas(root, height=(300), width=(384), bg="#26292c")
canvas.pack()

frame= tkinter.Frame(root, bg="#26292c")
frame.place(relx=.1, rely=.1, relwidth=.8, relheight=.8)

#Input box
pathEntry=tkinter.Entry(frame, bg='#c5c7c4')
pathEntry.place(relx=.4, rely=0, relwidth=.75, relheight=.15)

emailEntry=tkinter.Entry(frame, bg='#c5c7c4')
emailEntry.place(relx=.4, rely=.20, relwidth=.75, relheight=.15)

passwordEntry=tkinter.Entry(frame, bg='#c5c7c4')
passwordEntry.place(relx=.4, rely=.40, relwidth=.75, relheight=.15)

#Labels
pathL = tkinter.Label(frame, text="Driver Path", padx=1, pady=1, fg="white", bg="#26292c")
pathL.place(relx=0, rely=0, relwidth=.25, relheight=.15)

emailL = tkinter.Label(frame, text="Email/User", padx=1, pady=1, fg="white", bg="#26292c")
emailL.place(relx=0, rely=.20, relwidth=.25, relheight=.15)

passwordL = tkinter.Label(frame, text="Password", padx=1, pady=1, fg="white", bg="#26292c")
passwordL.place(relx=0, rely=.40, relwidth=.25, relheight=.15)

CountL = tkinter.Label(frame, text="# of deleted bookmarks: ", padx=1, pady=1, fg="white", bg="#26292c")
CountL.place(relx=0, rely=.60, relwidth=.5, relheight=.15)

CountLN = tkinter.Label(frame, text="#", padx=1, pady=1, fg="white", bg="#26292c")
CountLN.place(relx=.6, rely=.60, relwidth=.25, relheight=.15)

#Buttons
startScript=tkinter.Button(frame, text="Activate Scraper", padx=10, pady=5, fg="white", bg="#52595d", command= startThread) 
startScript.place(relx=.05, rely=.8, relwidth=.4, relheight=.2)

endScript=tkinter.Button(frame, text="Quit Scraper", padx=10, pady=5, fg="white", bg="#52595d", command= endThread)
endScript.place(relx=.55, rely=.8, relwidth=.4, relheight=.2)

root.mainloop()
