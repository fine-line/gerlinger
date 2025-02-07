# Gerlinger
Веб-приложение с набором прикладных программ-калькуляторов для конструкторов ПГС

## Расчет температурной нагрузки

### Описание
В калькуляторе реализован расчет температурной нагрузки по СП 20.13330.2016 (изм.5) СП 131.13330.2020 (изм.2)<br>
Программа предназначена для избавления от необходимости лезть в таблицы СП 131 и в карты СП 20

### Как это работает
При вычислении нормативных температур по СП 131 программа находит ближайшую метеостанцию к исследуемой точке.<br>
Карты оцифрованы вручную. При вычислении нормативных температур по картам СП 20 программа находит среднее взвешенное между температурами ближайших изолиний в зависимости от расстояния до них.<br>
Все остальное - стандартные формулы СП. Для конструкций, не защищенных от солнечной радиации выдается результат для всех ориентаций (горизонтальная, южная, северная, западная/восточная)
### Особенности
Координаты населенных пунктов таблицы СП 131 были взяты на сайте [ИНИД](https://data.rcsi.science/data-catalog/datasets/160/)

Заменены названия следующих населенных пунктов таблицы СП 131 (есть подозрение, что в СП 131 указаны не названия населенных пунктов, а названия метеостанций, отчего и расхождение):
+ Верхне-Марково заменено на Верхнемарково
+ Большерецк заменено на Усть-Большерецк
+ Исиль-Куль заменено на Исилькуль
+ Усть-Щугор заменено на Усть-Щугер
+ Бердигястях заменено на Бердигестях
+ Эйк заменено на Эйик
+ Им. Полины Осипенко заменено на имени Полины Осипенко
+ Троицко-Печорское заменено на Троицко-Печорск
+ Охотский Перевоз заменено на Охотский-Перевоз
+ Джаорэ заменено на Джаоре
+ Нера заменено на Усть-Нера
+ Усть-Мома заменено на Хонуу
+ Байдуков заменено на Байдуково

Часть пунктов СП 131 представляют собой заброшенные метеостанции. Координаты следующих метеостанций определялись вручную:
Калакан,
Нерчинск,
Ича,
Кроноки,
мыс Лопатка,
о. Беринга,
Семлячики,
Усть-Воямполка,
Агата,
мыс Челюскин,
Ай-Петри,
Брохово,
Среднекан,
Ниванкюль,
о. Сосновец,
Варандей,
Канин Нос,
Ходовариха,
Хоседа-Хард,
Сосуново,
Буяга,
Джалинда,
Джикимда,
Исить,
Иэма,
Сухана,
Токо,
Томпо,
Туой-Хая,
Шелагонцы,
Погиби,
Джаоре,
Березово,
Усть-Олой,
Эньмувеем,
Марресаля

## Разработчики
+ Головин Андрей - [fine-line](https://github.com/fine-line)

## Лицензия
Данный проект имеет лицензию GNU AFFERO GENERAL PUBLIC LICENSE - больше информации в файле [LICENSE.md](LICENSE.md)

