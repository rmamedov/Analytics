#Программа получает html с сайта и что-то с ним делает

#Импортируем библиотеку urllib и метод из нее .request
import urllib.request
from bs4 import BeautifulSoup
#спрашиваем какой сайт открыть
print ('Введи ебалу:')
r = input()
#открываем сайт
a = urllib.request.urlopen("http://"+r)
#считываем html который открылся в переменной  'a' и записываем его в переменную html
html = a.read()

#структурируем текст полученный из переменной html.
soup = BeautifulSoup(html, "lxml")

#print(soup)
z = soup.title
n = soup.img
d = soup.find('div', 'content')
print (z)
print (n)
print(d)
#print('ну, и ебала которую ты ввел:', r)
