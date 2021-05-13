import time, types
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException, NoSuchElementException, NoSuchFrameException
from functools import partial

class Page:
    def __init__(self, browser, tab_key=None):
        if tab_key != None and tab_key not in browser.tabs.keys(): raise ValueError("tab_key not in self.tabs.keys().")
        self.browser = browser
        if not tab_key:
            self.tab_key = self.browser.current_tab_key
            self.tab_link = self.browser.tabs[self.tab_key]['link']
        else:
            self.tab_key = tab_key
            self.tab_link = self.browser.tabs[tab_key]['link']
        
    def explicit_wait(self,element_pointer,method,time_arg = 5):
        try:
            if (method == "xpath"):
                WebDriverWait(self.browser.chrome,time_arg).until(EC.presence_of_element_located( (By.XPATH, element_pointer)))
            elif (method=="css"):
                WebDriverWait(self.browser.chrome,time_arg).until(EC.presence_of_element_located( (By.CSS_SELECTOR, element_pointer)))
            else:    
                print("Method 'find_elements_on_page' - provide a valid method")
                return False
            return True
        except TimeoutException:
            print("Method 'explicit_wait' - timed out - element: "+element_pointer)
            return False 
        except NoSuchElementException:
            print("Method 'explicit_wait' - no such element found")
            return False     
        
    def __str__(self):
        return "hello from Page"
        
    def find_elements_on_page(self, multiple, _method, elements_pointer, time_arg=5):  #make time wait parameter optional  
        if self.explicit_wait(element_pointer=elements_pointer, method=_method, time_arg=time_arg):
            if multiple and _method == 'css':
                elements = self.browser.chrome.find_elements_by_css_selector(elements_pointer)
            elif not multiple and _method == 'css':
                elements = self.browser.chrome.find_element_by_css_selector(elements_pointer)
            elif multiple and _method == 'xpath':
                elements = self.browser.chrome.find_elements_by_xpath(elements_pointer)
            elif not multiple and _method == 'xpath':
                elements = self.browser.chrome.find_element_by_xpath(elements_pointer)
        else:
            print("find_elements_on_page(): explicit_wait() did not succeed.")
            elements = []               
        
        return elements
    '''
    def is_text_in_element(self, method, element_text, element_pointer):
        #checks if text is in element
        the_element = self.find_elements_on_page(False, method, element_pointer)
        return (element_text in the_element.text)
            
    def loop_over_elements(self, method, elements_pointer, loop_function, pagination = {}):
    #this method has not been tested

    #pagination parameter:
        #{} - no pagination 
        #dictionary - {"pages": number of first n pages to loop over, "elements_pointer": elements_pointer in css or xpath, "method": css or xpath, "start_page": 3 (ex.), "forward": True}
    #loop_function parameter 
        #same function could be performed on all elements, or different functions on different elements
        #["indexes_known", {"elements": [1,4,6], "function": click() or get_text() or etc.}, {"elements": [0,2,3,5], "function": click() or get_text()}]  this way - not useful
        #["indexes_unknown", {method_name: {parameter_name: parameter...}}, function if condition True, function if condition False] 
        
        #if loop_function["indexes_known"]:
        #        elements = self.find_elements_on_page(multiple=True, method, elements_pointer)
        #        for element in elements:
        #            if loop_function[1]: 
        #                loop_function[2]  
        #    if pagination:
        #        page = self.find_elements_on_page(multiple=True, pagination["method"], pagination["elements_pointer"])
        
        def loop_helper(elements): 
            if not loop_function["top_to_bottom"]:
                elements = elements[::-1]
            for element in elements: 
                if loop_function["top_to_bottom"]:
                    if method == "css":
                        path = elements_pointer+":nth-of-type("+str(elements.index(element)+1)+")"
                    elif method == "xpath":
                        path = "("+elements_pointer+")["+str(elements.index(element)+1)+"]"
                elif not loop_function["top_to_bottom"]:
                    if method == "css":
                        path = elements_pointer+":nth-of-type("+str(len(elements) - elements.index(element))+")"
                    elif method == "xpath":
                        path = "("+elements_pointer+")["+str(len(elements) - elements.index(element))+"]"                    
    
                if type(loop_function["function"]) is list: #loop_function["function"] is a single (e.g. one) method of Page, with arguments already supplied (all but path to element)
                    args = loop_function["function"][1:] + [path]
                    if loop_function["function"][0](self, *args): #"unpack" the arguments first (loop_function["function"][1:]), then add "path" var at the end
                        loop_function["if_true"]()
                    else:
                        #loop_function["if_false"]() 
                        break
                elif type(loop_function["function"]) is types.FunctionType:  #loop_function["function"] is a lambda expression/function
                    if loop_function["function"](element, elements): 
                        loop_function["if_true"](path)
                    else:
                        #loop_function["if_false"](path) 
                        break
                        
        if not loop_function["indexes_known"]:            
            if pagination: #if there is pagination (e.g. elements are on different pages)
                if pagination["type"] == "numbers":
                    pages = self.find_elements_on_page(True, pagination["method"], pagination["elements_pointer"])
                    for page_index in range(len(pages[:pagination["pages"]])):
                        if page_index > 0:
                            if pagination["forward"]: #going forward in pages
                                self.find_elements_on_page(True, pagination["method"], pagination["elements_pointer"])[pagination["start_page"]+page_index].click() 
                            else: #going backward in pages
                                self.find_elements_on_page(True, pagination["method"], pagination["elements_pointer"])[pagination["start_page"]-page_index].click() 
                            time.sleep(3) #can set it as a parameter    
                        elements = self.find_elements_on_page(True, method, elements_pointer)
                        loop_helper(elements) 
                elif pagination["type"] == "arrows":
                    for page_index in range(pagination["pages"]):
                        if page_index > 0:
                            if pagination["forward"]: #going forward
                                self.find_elements_on_page(False, pagination["method"], pagination["right_pointer"]).click() 
                            else: #going backward
                                self.find_elements_on_page(False, pagination["method"], pagination["left_pointer"]).click() 
                            time.sleep(3)  #can set it as a parameter    
                        elements = self.find_elements_on_page(True, method, elements_pointer) 
                        loop_helper(elements)                    
            else: #if there is no pagination (e.g. elements are on same page)
                elements = self.find_elements_on_page(True, method, elements_pointer) 
                loop_helper(elements)
    '''
                     