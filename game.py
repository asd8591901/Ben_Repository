"""用python设计一个小游戏"""


import random

counts=3
answer=random.randint(1,10)
while counts>0:
    temp=input("猜一个数字，猜中有奖")
    guess=int(temp)

    if guess==answer:
        print("答对了，你是我心里面的一条蛔虫")
        break
    else:
        if guess<answer:
            print("答错啦～数字小了")
        else:
            print("答错啦～数字大了")
        counts=counts-1
        
print("游戏结束～")
