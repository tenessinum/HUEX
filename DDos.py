import requests as r
import random
import time

static_path = 'http://192.168.1.149:8000'

data = r.get(static_path + '/static/roads.json')

count = len(data.json()['points'])

print(count)

while True:
    number1 = 0
    number2 = 0
    while number1 == number2:
        number1 = random.randint(0, count-1)
        number2 = random.randint(0, count-1)

    print ('Request', number1, number2)
    try:
        path = static_path + '/ask_taxi?o=' + str(number1) + '&t=' + str(number2)
        data = r.get(path)

        print(data.json()['m'])

        if data.json()['m'] == 'ok':
            time.sleep(5)
    except:
        pass

