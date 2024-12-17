# Checksum tester for MPC

# Inputs to the controller need a leading and trailing whitespace
inputStr = " 01 01 "

# Outputs from the controller only need leading whitespace
outputStr = " 01 OK 00 DIGITEL MPC"

sumIn = 0
sumOut = 0

for char in inputStr:
    sumIn += ord(char)

for char in outputStr:
    sumOut += ord(char)

print('~{}{:02X}'.format(inputStr,sumIn%256))
print('~{} {:02X}'.format(outputStr,sumOut%256))
