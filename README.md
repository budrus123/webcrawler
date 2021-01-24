# Web Crawler

CONTENTS OF THIS FILE
---------------------

 * Introduction
 * Installation

INTRODUCTION
------------
A python **webcrawler** that uses **iterative deepening search** to crawl into a given URL until a certain depth has been met. 
In addition, this project uses **threads to do unigram extraction** at each webpage. Each webpage content is analayzed and the frequency of each character is determined in order to determine if webpage is spam or not.

The output of the project is a **tree-like structure** of the webcrawler as well as an **HTML file directory** with all the webpages and a **unigram files directory** with all the unigram info.
INSTALLATION
------------

```sh
$ python webcrawler.py
```



