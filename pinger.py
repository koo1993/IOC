import os

file1 = open('./melting-cobalt/ips.txt', 'r')
Lines = file1.readlines()

countOn = 0
countOff = 0
# Strips the newline character
for line in Lines:
    print("ping", line)
    hostname = line
    response = os.system("ping -c 1 " + hostname)
    # and then check the response...
    if response == 0:
        countOn = countOn + 1
        print (hostname, 'is up!')
    else:
        countOff = countOff + 1
        print (hostname, 'is down!')


print("up: ", countOn, "down: ", countOff)