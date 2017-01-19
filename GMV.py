from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, Text, String, MetaData, ForeignKey
from sqlalchemy import text

#e = create_engine('postgresql://postgres:postgres@192.168.21.30:5454/postgres', echo=True)
b = create_engine('postgresql://postgres:postgres@db.uaprom:5432/uaprom') #Коннекшн к базе uaprom (она же stable). Задается как string, потому берется в ''. postgresql:// - это тип БД, там может быть так же
#и mysql и любая другая база. postgres:postgres - логин:пароль (ну, у нас максимальная секьюрность на dev ресурсах, потому login postgres  и пароль postgres. db.uaprom:5432 - адрес базы и порт, в адресе может быть
#Например, ip адрес. /uaprom - это название базы. К примеру, в базе Бигля (которая для аналитики_ название базы тупо postgres. Потому и выглядит коннекшн как 'postgresql://postgres:postgres@192.168.21.30:5454/postgres'
#Включение логирования  - это echo=True. Если что-то не работает, то нужно дописать это в конец строки с подключением и станет понятно что именно не работает.

date_from = '2017-01-01'
date_to = '2017-01-16'

#Это переменные, которые мы используем для того, что бы указывать дату для выполнения запроса. Можно указать один день или дату со временем, соблюдая формат который умеет база данных "2016-09-13 10:03:01.275196"
#Не забываем что база использует американский формат дат, потому первым идет месяц, а потом число
#Дальше мы будем выполнять запрос к базе. Создаем переменную (а), дальше пишем название коннекшена (это у нас переменная b) ставим точку и вызываем функцию "execute". Собственно, она и делает запрос. как аргумент
#в скобках передаем как string сам sql запрос.
a = b.execute('''
select
--    date_trunc('day', o.date_created) as "date", -- если нужна разбивка по дате
--  count(distinct o.id) as total_orders, -- общее количество заказов

-- это - для подсчёта, исключая отменённые заказы (ниже строка and o.status!=4 должна быть активной)
    sum((shopping_cart_item.product_price * coalesce(cur.crncy_rate, 1)) - (shopping_cart.discount_amount * coalesce(cur.crncy_rate, 1)))as gmv, -- GMV с учётом скидок
    sum((shopping_cart_item.product_price * coalesce(cur.crncy_rate, 1)) - (shopping_cart.discount_amount * coalesce(cur.crncy_rate, 1)))/count(distinct o.id) as av_check -- средний чек

-- это - для подсчёта, включая отменённые заказы (ниже строка and o.status!=4 должна быть закоментированной)
--    sum((shopping_cart_item.product_price * coalesce(cur.crncy_rate, 1)))as gmv_without_discount,
--    sum((shopping_cart_item.product_price * coalesce(cur.crncy_rate, 1)))/count(distinct o.id) as gmv_max

from
    shopping_cart
    join shopping_cart_item on shopping_cart.id = shopping_cart_item.cart_id
    join "order" as o on shopping_cart_item.cart_id = o.cart_id
left join (    select
                d.id as crncy_id,
                d.value as dict_value,
                cr.crncy_rate
            from
                (select
                    json_object_keys(convert_from(rates, 'utf-8')::json) as crncy_name,
                    btrim((convert_from(rates, 'utf-8')::json -> json_object_keys(convert_from(rates, 'utf-8')::json) ->> '__value__'), '"')::float crncy_rate
                from
                    currencies_rates) as cr
                join dictionary as d on d.value = cr.crncy_name
            where
                d.type = 4) as cur on shopping_cart_item.product_price_currency_id = cur.crncy_id


where

-- здесь задаётся нужный период даты
    o.date_created >= date'{date_from}'
    and o.date_created < date'{date_to}'


    and o.status!=4 -- отменённые
    and o.source=16 -- биглёвые заказы
    and o.type in (0,1,2,3,8,9) -- исключаем сообщения
    and shopping_cart_item.quantity <= 1000 -- исключаем фрод
    and shopping_cart_item.number <=100 -- исключаем фрод
    and o.company_id!=1816499 -- исключаем тестовую компанию
-- group by 1 order by 1 desc -- это нужно, если включаешь разбивку по дате
'''.format(date_to=date_to, date_from=date_from))
#.format - это волшебная функция, которая позволяет вставить нам в запрос, который по сути строка ('string'), переменую. Чтобы это сделать в запросе мы берем переменные в фигурные скобки {date_from}, а потом,
#определеяем их как переменную, передавая их в аргументе функции .format (date_to=date_to), то есть той переменной, которую мы задали там еще выше.

GMV = a.fetchone()
# и тут мы такие получили данные, хранятся они у нас в переменной (а). Теперь нам нужно выбрать из них то, что нам нужно. Даже если там все нам нужно. Для этого мы делаем GMV = a.fetcall() или fetchone.
# Собственно fetch это получение данных из какой-то переменной, в данном случае (а).

#просто выводим на экран значения которые нам отдала база. Типа а почему бы и нет?
print(GMV.gmv)
print(GMV.av_check)

#Дальше мы коннектимся к новой базе и выполняем еще один запрос (то есть делаем .execute) и пишем обычный SQL запрс INSERT, который будет добавлять данные в нашу таблицу Бигля. Понятное дело,
#мы опять используем функцию .format для того, что бы определить в запросе переменные, которые будем записывать в базу. Пишем мы, как понятно из запроса, в таблицу opinion_analytics.

create_engine('postgresql://postgres:postgres@192.168.21.30:5454/postgres')\
    .execute('''insert into opinions_analytics ("date", "gmv", "order_av") values ('{date_from}', {gmv}, {order_av});'''.format(
        date_from=date_from, order_av=GMV.av_check, gmv=GMV.gmv
    ))
print('Молодец, все прошло хорошо :)')

