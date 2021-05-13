import os, time, random #urllib.request
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException, NoSuchElementException, NoSuchFrameException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

class Browser:
        def __init__(self,page_load_timeout=90,script_timeout=90,starting_page="https://www.google.com/", sleep_time=5, phantom = False, adblock = True):
                if adblock: #to get rid of ads
                        options = Options()
                        # options = webdriver.ChromeOptions()
                        # options.add_argument("--no-startup-window")
                        options.add_argument('load-extension=C:/Users/HP10/Desktop/Personal/Job materials/Jobs/Upwork/AdBlock')
                        if phantom:
                                self.chrome = webdriver.PhantomJS(chrome_options = options) #inherit from webdriver.PhantomJS
                        else:
                                self.chrome = webdriver.Chrome(chrome_options = options) #inherit from webdriver.Chrome
                        self.chrome.create_options()
                        print("adblock is running")
                self.chrome.set_page_load_timeout(page_load_timeout)
                self.chrome.set_script_timeout(script_timeout)
                self.chrome.get(starting_page)
                self.tabs = {} #dictionary of currently opened tabs
                self.current_tab_key = '' #key for currently opened tab
                for tab_handle in self.chrome.window_handles:
                        self.chrome.switch_to.window(tab_handle)
                        self.add_tab_to_tabs(self.chrome.current_url, tab_handle, False)
                self.close_tab("settings_1", switch_to_tab_key="getadblock.com_1") #in case a settings tab is opened which happens sometimes
                if adblock:
                        time.sleep(10)
                        self.close_tab("getadblock.com_1", switch_to_tab_key=(set(self.tabs.keys()) - {"getadblock.com_1"}).pop()) #have to provide the only key left in the dictionary
                time.sleep(sleep_time)

        def switch_to_tab(self, tab_key):
                if tab_key not in self.tabs.keys(): raise ValueError("tab_key not in self.tabs.keys().")
                if tab_key != self.current_tab_key:
                        self.chrome.switch_to.window(self.tabs[tab_key]['handle'])
                        self.current_tab_key = tab_key
                else:
                        print("This tab is already selected.")

        def go_to_link(self, target_link, tab_key, page_load_time = 5,element_load=dict()):   #element_load - ?
                if tab_key not in self.tabs.keys(): raise ValueError("tab_key not in self.tabs.keys().")
                if (tab_key != self.current_tab_key): self.chrome.switch_to_tab(tab_key)

                self.chrome.get(target_link)
                
                if (element_load == {}):
                        time.sleep(page_load_time)
                        self.modify_tabkey_value(tab_key, target_link, switch_to_tab=True) #switch_to_tab=TRUE in order to update self.current_tab_key
                        # #could cause issues when the link redirects to another website
                else:
                        try:
                                WebDriverWait(self.chrome,element_load["time"]).until(EC.presence_of_element_located( (By.XPATH, element_load["element_xpath"])))
                                self.modify_tabkey_value(tab_key, target_link, switch_to_tab=True) #switch_to_tab=TRUE in order to update self.current_tab_key
                        except TimeoutException:
                                self.chrome.get(self.tabs[tab_key]['link']) #back to original link
                                print("Timed out while waiting for element to show up - method go_to_link()")
                        except NoSuchElementException:
                                self.chrome.get(self.tabs[tab_key]['link'])  #back to original link
                                print("Element was not found - method go_to_link()")
                        except KeyError:
                                self.chrome.get(self.tabs[tab_key]['link'])  #back to original link
                                print(element_load)
                                print("this is element_load dictionary")
                                print("Dictionary keys are not found, correct them - method go_to_link()")
        
        def open_new_tab(self, tab_link="http://www.google.com", switch_to_new_tab=True):
                self.chrome.execute_script('''window.open("'''+tab_link+'''", "_blank");''')
                time.sleep(5) #wait for page to open
                self.add_tab_to_tabs(tab_link, self.chrome.window_handles[-1], switch_to_new_tab) #last element in a list because the newly opened tab will always be last
                
        def close_tab(self,close_tab_key,switch_to_tab_key = None):
                #switch_to_tab_key provides a tab to switch to in case we want to close current tab; if None is passed it means we want self.current_tab_key
                if switch_to_tab_key == None: switch_to_tab_key = self.current_tab_key
                if (close_tab_key and switch_to_tab_key) in self.tabs:
                        if close_tab_key == switch_to_tab_key: #only 1 tab should be opened
                                if len(self.tabs.keys()) == 1:
                                        self.chrome.close() #close the only tab left
                                        self.tabs.pop(close_tab_key)
                                        self.current_tab_key = ""
                                        print('No tabs opened.')
                                else: #can't switch to a tab that was just closed
                                        raise ValueError('Provide appropriate (not close_tab_key) switch_to_tab_key.')
                        else: #more than 1 tab opened overall
                                if close_tab_key != self.current_tab_key: self.switch_to_tab(close_tab_key)
                                self.chrome.close() #don't know which tab browser will switch to after calling close(), so we will use switch_to 2 lines below
                                self.tabs.pop(close_tab_key)
                                self.switch_to_tab(switch_to_tab_key)
                else:
                        raise NoSuchWindowError("Tab not found, either close_tab_key or switch_to_tab_key.")
         
        def add_tab_to_tabs(self, tab_link, tab_handle, switch_to_tab=True): #adds tab to list of tabs and optionally switch to a newly made tab; tab_link made of current_window_handle
                new_key = tab_link.split("://")[1].split("/")[0]
                if (new_key in [key.split('_')[0] for key in self.tabs.keys()]): #if tab(s) with this website already exist(s), create new_key: key+"_(i+1)"
                        new_key += "_" + str(max([int(key.split('_')[1]) for key in self.tabs.keys() if (key.split("_")[0] == new_key)])+1)
                else: #if tabs with this website don't exist yet
                        new_key += "_1"
                self.tabs[new_key] = {}
                self.tabs[new_key]['link'] = tab_link
                self.tabs[new_key]['handle'] = tab_handle
                if switch_to_tab: self.switch_to_tab(new_key)

        #check that remove tab from tabs and add tab to tabs work correctly one after another
        def modify_tabkey_value(self, tab_key, tab_link, switch_to_tab=True): #modifies the value in self.tabs[tab_key] since a new link was followed on this tab
                self.tabs.pop(tab_key)
                self.add_tab_to_tabs(tab_link, switch_to_tab) #want to switch to the tab in order for self.current_tab_key to be updated

        def refresh(self):
                self.chrome.refresh()

    
