from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import chromedriver_autoinstaller

import random
import json
import time
import re
import os
from datetime import date
################## IMPORT MODULES ##################
from database import *

def optionsConfiguration():
    global options
    # Adding argument to disable the AutomationControlled flag 
    options.add_argument("--disable-blink-features=AutomationControlled") 
     
    # Exclude the collection of enable-automation switches 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
     
    # Turn-off userAutomationExtension 
    options.add_experimental_option("useAutomationExtension", False)
     
    # Changing the property of the navigator value for webdriver to undefined 
    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
    options.add_argument('--disable-notifications')
    # js.executeScript("window.onbeforeunload = function() {};");
    # Define default profiles folder

    # options.add_argument(r"user-data-dir=/Users/mitsonkyjecrois/Library/Application Support/Google/Chrome/Profile 1")
    # # Define profile folder, profile number

    options.add_argument(r"user-data-dir=/home/jorge/.config/google-chrome/")
    # Define profile folder, profile number
    options.add_argument(r"profile-directory=Profile 2")
    # launch chrome navigator
    
#########################################################################################
#                                                                                       #
#                SECTION FOR SAVE AND LOAD CHECK POINTS                                 #
#                                                                                       #
#########################################################################################
def saveCheckPoint(filename, dictionary):
    json_object = json.dumps(dictionary, indent=4)
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def loadCheckPoint(filename):
    # Opening JSON file
    with open(filename, 'r') as openfile:        
        json_object = json.load(openfile)
    return json_object

#########################################################################################
#                                                                                       #
#                                   MAIN FUNCTINS                                       #
#                                                                                       #
#########################################################################################
def giveClickRecents(filterword = 'Recents'):
    buttonfilter = driver.find_element(By.CLASS_NAME, '-mb-px.flex.place-content-evenly.space-x-4')

    listbuttons = buttonfilter.find_elements(By.CSS_SELECTOR,'a')

    for button in listbuttons:

        if filterword in button.text:
            button.click()

def getConversationBlock():
    class_conversation = 'ml-1.message-list--avatar.avatar'
    conversations = driver.find_elements(By.CLASS_NAME, class_conversation)
    return conversations

def getNameRight():
    try:
        bodyside = driver.find_element(By.CLASS_NAME, 'message-body--aside')
        nameright = bodyside.find_element(By.CLASS_NAME, 'avatar_img').text
        return nameright
    except:
        return ""

def waitNewContactName(nameleft, nameright):
    while nameleft != nameright:
        nameright = getNameRight()
        time.sleep(0.2)

def getAllMessages():
    global listMSGObject
    flagloop = True    
    while flagloop:        
        try:
            listMSGObject = driver.find_elements(By.CLASS_NAME, 'messages-single.--own-message')
            if len(listMSGObject)!= 0:
                flagloop = False
            time.sleep(0.5)
        except:
            time.sleep(1)

def getPendinIndexMessageList():
    global listMSGSentText, msgdontsentindexs, listMSGObject
    msgdontsentindexs = []
    listMSGSentText = []

    msgEmpty = True    
    print("getPendinIndexMessageList: ")
    while msgEmpty:        
        # getAllMessages()
        msgEmpty = False
        for msgnumber, message in enumerate(listMSGObject):

            # GET THE ID NUMBER OF MESSAGES FAILED
            if 'Unsuccessful' in message.text:                
                msgdontsentindexs.append(msgnumber)               

            # ELSE BUILD A LIST WITH THE MESSAGES SENT SUCCESSFULLY
            else:
                msg = message.find_element(By.CLASS_NAME, 'message-bubble').text
                listMSGSentText.append(cleanMessage(msg))

            # TO MAKE SURE THAT THE MESSAGE IS NOT EMPTY, IF FIND ANY EMPTY MESSAGE IT REPEAT THE PROCESS.
            if len(message.text) == 0:
                msgEmpty = True
        time.sleep(1)

    msgdontsentindexs_copy = msgdontsentindexs.copy()
    
    flagduplicated = False    
    for i, KEY in enumerate(msgdontsentindexs):        
        txt = listMSGObject[KEY].find_element(By.CLASS_NAME, 'message-bubble').text    
        messagetext = cleanMessage(txt)        
        
        if messagetext in listMSGSentText:
            flagduplicated = True
            msgdontsentindexs_copy.remove(KEY)    
            
    if len(msgdontsentindexs_copy) == 0 and flagduplicated:
        print("-MSG- SENT PREVIOSLY--")
        input("Type any key to continue: ")
        
    elif len(msgdontsentindexs_copy) == 0:
        print("--NOT ISSUES--",end='-')
        
    return msgdontsentindexs_copy
    
def trySendAgain(timewait= 1):
    global listMSGObject, msgdontsentindexs, listMSGSentText 
    message = listMSGObject[msgdontsentindexs[0]]
    buttontryagain = message.find_element(By.CLASS_NAME, 'fa.fa-sm.fa-redo.pointer')
    buttontryagain.click()
    time.sleep(timewait)

def getemail():
    email = driver.find_element(By.CLASS_NAME, "multiple-to-email")
    return email.text

def checkDNSError(time_sleep = 0.3, max_try = 4):
    global dbase
    count = 0
    while_flag_DNS_error = True
    while while_flag_DNS_error:
        try:
            error_DNS_active = driver.find_element(By.ID, 'alertModal___BV_modal_body_')
            send_message_button = error_DNS_active.find_element(By.XPATH, value='//*[@id="alertModal___BV_modal_body_"]/div/div[2]/button')
            send_message_button.click()
            errorDNS_activeFlag = True
            while_flag_DNS_error = False
            print("--Cannot send message as DND is active--", end='-')
            email = getemail()
            dictsent = {'name':nameleft, 'phone':'*', 'date':current_date ,'email': email,
             'state':'DND active', 'time':current_date}
            insertNewIssue(dbase, dictsent)
        except:
            time.sleep(time_sleep)
            if count == max_try:
                errorDNS_activeFlag = False
                while_flag_DNS_error = False
        count +=1
    return errorDNS_activeFlag

def updateMsgState(time_sleep = 0.3, max_try = 10):
    count = 0
    while_flag_update = True
    
    while while_flag_update:
        
        try:
            # GET LIST OF ALL MESSAGE SENT INCLUDING FALLING MESSAGES
            getAllMessages()                
            # BUILD A LIST WITH THE INDEX OF FAIL MESSAGE AND A LIST WITH  THE MESSAGE SENT SUCCESSFULLY                
            msgdontsentindexs = getPendinIndexMessageList()
            while_flag_update = False
        except:            
            time.sleep(time_sleep)
            count+=1
            if count ==max_try:
                while_flag_update = False
    return msgdontsentindexs

def loopSendMessages(maxtry = 30):
    
    global msgdontsentindexs, listMSGSentText, listMSGObject, KEY, nameleft
    global dbase, current_date
    count = 0
    trysentEnable = True

    while len(msgdontsentindexs)!= 0:
            
            if trysentEnable:            
                trySendAgain()# CLICK EN EACH MESSAGE THAT FAIL BEFORE.                
                
                print("--SENDING AGAIN--", end='')
                trysentEnable = False
                
                flag_dns_error = checkDNSError(time_sleep = 0.3, max_try = 8)
                if flag_dns_error:
                    msgdontsentindexs = []
                    email = getemail()
                    dictsent = {'name':nameleft, 'phone':'*', 'date':current_date ,'email': email,
                     'state':'SENT', 'time':current_date}
                    insertNewIssue(dbase, dictsent)
                    break                

            # ONLY START PROCCESS IF COUNT VALUE IS MINOR TO MAXTRY
            if count < maxtry:
                msgdontsentindexs = updateMsgState(time_sleep = 0.3, max_try = 10)
                # ENABLE TRYSENT AGAIN
                trysentEnable = True                
            # ELSE SAVE IN A FILE JSON ISSUES MESSAGES
            else:
                email = getemail()
                dictfails = {'name':nameleft, 'phone':'*', 'date':current_date ,'email': email,
                 'state':'FAIL', 'time':current_date}
                insertNewIssue(dbase, dictfails)
                print("--- MAX COUNT REACHED, STOPED ---")
                saveCheckPoint('messagesfail.json', dictfails)
                msgdontsentindexs = []
            count += 1
            print("count: ", count,end='-')
#################################################################
#                       SECTION CLEAN TEXT                      #
#################################################################

def cleanMessage(msg):    
    msg = msg.lower().replace('Message Details','')
    msg = re.sub(r'[^\w\s]', '', msg)    
    msg = re.sub('[^A-Za-z0-9]+', '', msg)
    msg = ' '.join((msg.split()))
    return msg

#################################################################
#                   SECTION FOR SENT OTHER MESSAGE              #
#################################################################
def sentNewMessage():
    textarea = driver.find_element(By.NAME, 'editor')
    textarea.clear()
    textarea.send_keys('text 1 proof')
    
def clickSent():
    sendbutton = driver.find_element(By.ID, 'buttonGroupSpanSms')
    print(sendbutton.text)

def loadRecents():
    global name
    giveClickRecents()

    name2 = getNameRight()
    count  = 0
    while name == name2 or name2 == "" :
        name2 = getNameRight()
        time.sleep(0.5)
        print("#", end = ' ')    
        count +=1
        if count == 5:
            name2 = '***'
    time.sleep(1)

def getTotalConversation():
    blockconversation = driver.find_element(By.CLASS_NAME, 'hl_conversations--messages-list-v2.relative.border-r.border-gray-200')
    totalconversation = blockconversation.find_element(By.CLASS_NAME, "flex.items-center.h-5")
    totalResults = int(re.search(r'\d+',totalconversation.text).group(0))
    return int(totalResults//20)

def clickLoadMore(numbload = 10):
    loadmore = True
    batch = 0
    while loadmore:
        try:
            for n in range(0, numbload):
                loadmore = driver.find_element(By.XPATH,"//*[text()='Load More']")
                loadmore.click()
                time.sleep(1.5)
                batch +=1
                if batch ==10:
                    batch = 0
                    userinput = input("Type 'y' to continue loading conversations or other key to stop ")
                    if userinput!='y':
                        loadmore = False
                        break
            loadmore = False
        except:
            time.sleep(0.5)
    time.sleep(1)

def pauseFunction(flag_pause):
    while flag_pause:
        time.sleep(0.2)

# def stopFunction(flag_stop):
#     if flag_stop:
#         break
#########################################################################################
#                             MAIN                                                      #
#########################################################################################
def main(flag_pause, flag_stop):
    global KEY, name

    loadRecents()
    # clickLoadMore(numbload = getTotalConversation())
    clickLoadMore(numbload = 3)
    # while flagActivation:
    conversations = getConversationBlock()
    print(len(conversations))

    for KEY, conversation in enumerate(conversations):
        print("Client name: ", KEY, conversation.text)
        pauseFunction(flag_pause)
        # stopFunction(flag_stop)
        if flag_stop:
            break
        ################################################################
        #                   CLICK ON NEW CONVERSATION                  #    
        ################################################################
        conversation.click()
        ###############################################################
        #   SECTION TO LOAD CONTACT NAME FROM LEFT AND RIGHT SIDE     #    
        ###############################################################
        
        nameright = getNameRight()
        nameleft = conversation.text
        #####################################################     
        #   SECTION TO WAIT UNTIL LOAD NEW CONVERSATION     #    
        #####################################################
        waitNewContactName(nameleft, nameright)

        ##################################################### 
        #                                                   #
        #       SECTION TO CHECK PENDING MESSAGES           #
        #                                                   #
        #####################################################
        # INITIALIZATION
        msgdontsentindexs = []  # INDEX OF MESSAGE WITH ISSUES (GLOBAL VARIABLES)
        listMSGSentText = []        # MESSAGE SENT PREVIOUSLY (GLOBAL VARIABLES)
        # count = 0

        getAllMessages() # GET A LIST OF MY OWN MESSAGES.
        getPendinIndexMessageList()
        loopSendMessages(maxtry = 20)
#########################################################################################
#                          GLOBAL VARIABLES                                             #
#########################################################################################

def launchNavigator():
    global options, driver, name
    options = webdriver.ChromeOptions()
    optionsConfiguration()
    driver = webdriver.Chrome(options=options)
    driver.get('https://app.rmhgo.com/v2/location/OgPuXhkvOkbRC0zerxQP/conversations/conversations/xxj8duklLmHcPja93udc')

    name = ""
    while name =="":
        name = getNameRight()
        time.sleep(0.5)
        print("#", end = ' ')
    time.sleep(1)
# input('Confirm to continue: ')

msgdontsentindexs = []
listMSGSentText = []
listMSGObject = []
count = 0
dictFallSend = {}
nameleft = ''
nameright = ''
current_date = date.today().strftime("%d/%m/%Y")
# if __name__ == "__main__":
#     main()

def processControl(t, _stop):
    global KEY, name, current_convers_index, conversations,nameleft, nameright, msgdontsentindexs, listMSGSentText, listMSGObject
    global last_conversation, dbase
    # while flagActivation:    
    if t == 0:
        print("Loading Conversations")
        conversations = getConversationBlock()
        current_convers_index = 0
        dbase = createConection()        
        if os.path.isfile('check_points/lastconversation.json'):
            last_conversation = loadCheckPoint('check_points/lastconversation.json')['index'] + 1
        
        # t+=1
    # LOOP OVER CONVERSATIONS 

    else:
        nsteps = 10        
        current_convers_index = (t-1)//nsteps + last_conversation        
        if (t-1)%nsteps == 1:
            print("last_conversation: ", last_conversation)
            print("current_convers_index #######", current_convers_index, "#######")
            conversations[current_convers_index].click()
        if (t-1)%nsteps == 2:
            nameright = getNameRight()
        if (t-1)%nsteps == 3:
            nameleft = conversations[current_convers_index].text
        if (t-1)%nsteps == 4:
            waitNewContactName(nameleft, nameright)
        if (t-1)%nsteps == 5:
            msgdontsentindexs = []  # INDEX OF MESSAGE WITH ISSUES (GLOBAL VARIABLES)
        if (t-1)%nsteps == 6:
            listMSGSentText = []        # MESSAGE SENT PREVIOUSLY (GLOBAL VARIABLES)
        # count = 0
        if (t-1)%nsteps == 7:            
            getAllMessages() # GET A LIST OF MY OWN MESSAGES.            
        if (t-1)%nsteps == 8:
            msgdontsentindexs = getPendinIndexMessageList()
            print("msgdontsentindexs: ", msgdontsentindexs)
        if (t-1)%nsteps == 9:
            print("Begin loop send messages again ")
            loopSendMessages(maxtry = 20)
            saveCheckPoint('check_points/lastconversation.json', {"index":current_convers_index})
        if current_convers_index == len(conversations)-1:        
            print("All conversations Checked: ")            
            t = -1
            closeConection(dbase)
            _stop = True
    return t + 1, _stop




