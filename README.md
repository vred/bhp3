# Black Hat Python for python version 3.6 (bhp3) 
This repository updates Black Hat Python code originally by Justin Seitz as available on https://www.nostarch.com/download/BHP-Code.zip to support Python 3.6 (as of Python 3.6.1). This is a work-in-progress, so not all chapters' examples are covered, yet. As of 3 July 2017, Chapter 2 examples are completed.

### Last update:
**20170704**

Happy Independence Day! Ch. 3 ICMP Sniffer added.

### Major Python 2 to Python 3 changes
Some of the changes are as methodic as print only strictly working parenthetically. 
Other major changes include nuances such as the new, strict requirement for socket methods, such as send, requiring type ***bytes*** instead of ***string***. 

Here are examples. 

Trivially, print statements that originally appeared as the following are no longer acceptable:
```python 
print "Hello world"
```
Instead, the following parenthetical method is strictly used for Python 3:
```python
print("Hello world")
```

As a less trivial example, consider the following case with a predefined client socket:
```python
	client_socket.send("Hello world.") 
```
Instead, the following bytes type is utilized as required by Python 3:

```python
	client_socket.send(str.encode("Hello world."))
```

These are only some of the kinds of changes added. Most changes are accompanied by succinct comments, which are furthermore distinguished with the word "NOTE" added before the change description to allow easy searching. 

### Contact or Feedback

Feel free to address any additional feedback to [**@ValARed**](https://twitter.com/valared) or on this GitHub page. Thank you! 
