from html.parser import HTMLParser
from urllib import parse
from anytree import Node, RenderTree, ContRoundStyle
import threading
import io
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import Counter
import json
from random import randrange
from anytree.exporter import DotExporter

# An activity can be executed in a separate thread of control.
# To specify the activity, we should override to _init_() and run()
class OutputThread(threading.Thread):
   def __init__(self, threadID, name, data):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.data = data
   def run(self):
      print_html_to_file(self.name, self.data)


# Save the html codes of each webpage as text files
# and save the unigram features file
def print_html_to_file(name, data):
    html_path = "html_files_" + str(global_version)
    unigram_extraction_path = "unigram_files_" + str(global_version)

    with io.open(html_path+"/"+name+".html", "w", encoding="utf-8") as f:
        f.write(data)

    with io.open(unigram_extraction_path+"/"+ name + "_unigram.txt", "w", encoding="utf-8") as f:
        unigram_data = unigram_extraction(data)
        f.write(unigram_data)


# initialize the directories at the beginning of the execution
# one directory is for html files
# and the other is for unigram features files
def initialize_directories():
    html_path = "html_files_"+str(global_version)
    unigram_extraction_path = "unigram_files_"+str(global_version)

    try:
        os.mkdir(html_path)
        os.mkdir(unigram_extraction_path)
    except OSError as e:
        print("Creation of the directory %s failed" % str(e))


# Extracts the text data for each webpage,
# counts the frequency of each character and saves the feature extraction results
# in a text file
def unigram_extraction(data):
    soup = BeautifulSoup(data, features="html.parser")
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    row = list(text)
    unigram_text = json.dumps(Counter(row))
    return  unigram_text

class LinkParser(HTMLParser):
    # This function is used to find every link on the page
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    newUrl = parse.urljoin(self.baseUrl, value)
                    self.links = self.links + [newUrl]

    # This function is used to get links that our spider() function will call
    def get_links(self, url):
        self.links = []
        self.baseUrl = url
        response = urlopen(url)
        html_bytes = response.read()
        html_string = html_bytes.decode("utf-8")
        self.feed(html_string)
        return html_string, self.links


    def get_url_content(self, url):
        response = urlopen(url)
        # to store the html as bytes
        html_bytes = response.read()
        # decode function for our bytes variable to get a single string
        html_string = html_bytes.decode("utf-8")
        return html_string


# Web Crawler using IDFS.
# It takes as parameters a root node and max depth
def iterative_deepening_search(for_root, with_max_depth):
    global visited
    for i in range(with_max_depth+1):
        for_root.children = []
        visited = []
        visited.append(for_root.name)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        print("Traversal with depth limit = [", i ,"]")
        webcrawl(for_root, i)
        # print(RenderTree(for_root, style=DoubleStyle()).by_attr())
        print("\n✔✔~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~✔✔\n\n\n\n")


# Webcrawler function takes as param the root and the actual depth level to iterate
visited = []
def webcrawl(with_root, with_limit):
    global visited
    if with_limit >= 0:
        print("inside website ", with_root.name)
        try:
            parser = LinkParser()
            data = ""
            if with_limit > 0:
                # Extracts the html page content of the actual root and all the links related to this root
                data, links = parser.get_links(with_root.name)

                # For simplicity and speed, we are expanding the first X websites
                # for a given link, here X = 10

                for link in links[1:10]:
                    # This control avoids the iteration on same(duplicate)links by improving the execution time.
                    if not link in visited:
                        visited.append(link)
                        child = Node(link, with_root)
                        webcrawl(child, with_limit - 1)
            else:
                # Extracts the html page content of the root because the depth limit is zero.
                data = parser.get_url_content(with_root.name)

            name = parse_file_name(with_root.name)
            # Our activity is performed in multithreading to increase the performance.
            thread1 = OutputThread(randrange(1000), name, data)
            # starts a thread by calling the run method
            thread1.start()
        except:
            pass


# Replace forbidden filename characters in Windows
def parse_file_name(name):
    return name.split("://")[1]\
        .replace("<", "-")\
        .replace(">", "-")\
        .replace(":", "-")\
        .replace("/", "-")\
        .replace("\\", "-")\
        .replace("|", "-")\
        .replace("?", "-")\
        .replace("*", "-")


# Version control number, used in creating the output directories.
# Each execution will have its output in directories called
# html_files_X and unigram_files_X, where X is the execution count
def read_current_version():
    version = 0
    with open('version.txt') as f:
        for line in f:
            version = int(line)
    return version


# After each execution the version is incremented and updated sequentially
def update_version():
    global global_version
    global_version += 1
    write_file = open("version.txt", "w")
    write_file.write(str(global_version))
    write_file.close()


#######################################################
#                     Main Function                   #
#######################################################

# version control initialize
global_version = read_current_version()
initialize_directories()

# Read the URL from the user
url = input("Please enter the root URL: ")
root = Node(url+"/")

# Read the max allowed depth

max_depth = input("Please enter the max depth: ")
iterative_deepening_search(root, int(max_depth))

#RenderTree provides a tree structure with visual effects.
# For each root lists all children are printed
# See https://anytree.readthedocs.io/ for more details
print("Tree for the last and final level:")
print(RenderTree(root).by_attr('name'))


# Exporting the tree as a dot image
# in order to convert it to a png at a later stage
# See https://anytree.readthedocs.io/ for more details
DotExporter(root).to_dotfile("output.dot")

#update version number
update_version()