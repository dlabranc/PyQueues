import time
print('Ciao sono il tuo script Python')

time.sleep(5)

with open('terminato.txt', 'w') as f:
    f.write('Ho finito di eseguire')

print('Ho finito di eseguire')
