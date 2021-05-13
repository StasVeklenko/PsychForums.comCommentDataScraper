# PsychForums.comCommentDataScraper
This is the script I wrote for a client when freelancing on Upwork.com. He actually needed comments from Psychforums.com and several other websites similar to it.

This script searches for word "vegetarian" (2 other words were "Omega 3" and "ketogenic") on https://www.psychforums.com/bipolar/ forum (it uses the search box in the middle to search only the Bipolar Disorder forum, not the search box on the left for the whole forum) and copies every comment that is shown in search results into a "Psychforums vegetarian.doc" file. I have uploaded the resulting doc file. The file can be updated easily to scraoe for all 3 keywords at once. 

A few extra things required for psychforums_script.py to make sure it works besides installing the libraries imported in the script:
1) Download chromedriver.exe from https://chromedriver.chromium.org/ and put it somewhere. 
2) Create a my-paths.pth file in local/global site-packages folder and add to it the full path to chromedriver.exe (without "chromedriver.exe" at the end - i.e. full folder path), or just update the .pth with this path if it (.pth file) already exists. This will update PATH env var with chromedriver.exe path. 
3) Browser and Page classes are imported from Browser.py and Page.py in Projects/CustomClasses/, so if you want to import from somewhere else change "import ..." lines in the script accordingly and/or update PATH as in 2).     
