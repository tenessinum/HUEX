import requests as r
import random
import time

data = r.get('http://192.168.1.149:8000/static/roads.json')

count = len(data.json()['points'])

print(count)

while True:
    number1 = 0
    number2 = 0
    while number1 == number2:
        number1 = random.randint(0, count-1)
        number2 = random.randint(0, count-1)

    print ('Request', number1, number2)

    path = 'http://192.168.1.149:8000/ask_taxi?o=' + str(number1) + '&t=' + str(number2)
    data = r.get(path)

    print(data.json()['m'])
    time.sleep(3)
