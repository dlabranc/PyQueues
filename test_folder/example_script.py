import time
print('Ciao sono il tuo script Python')

time.sleep(10)
with open('resource0.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        print(line.strip())

with open('resource_folder/resource1.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        print(line.strip())

with open('resource_folder/sub_folder/resource2.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        print(line.strip())

with open('terminato.txt', 'w') as f:
    f.write('Ho finito di eseguire')


print('Ho finito di eseguire')
