import time
import webbrowser

total_breaks = 3
break_count = 0

print("This program started at " + time.ctime())
while(break_count<total_breaks):
    time.sleep(20)
    webbrowser.open("http://www.youtube.com/")
    break_count = break_count + 1
