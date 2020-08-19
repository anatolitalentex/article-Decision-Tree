import math
import pandas as pd
from functools import reduce

# Дата сет
d = {
    "Погода":["ясно","ясно","облачно","дождь","дождь","дождь","облачно","ясно","ясно","дождь","ясно","облачно","облачно","дождь"],
    "Температура":["Жарко","Жарко","Жарко","Тепло","Холодно","Холодно","Холодно","Тепло","Холодно","Тепло","Тепло","Тепло","Жарко","Тепло"], 
    "Влажность":["Высокая","Высокая","Высокая","Высокая","Норм","Норм","Норм","Высокая","Норм","Норм","Норм","Высокая","Норм","Высокая"],
    "Ветер":["Нет","Есть","Нет","Нет","Нет","Есть","Есть","Нет","Нет","Нет","Есть","Есть","Нет","Есть"],
    # Последний массив - это наша целевая переменная, показывающая результат, 
    # основывающийся на предыдущих данных.
    "Гольф":["×","×","○","○","○","×","○","×","○","○","○","○","○","×"],
}
df0 = pd.DataFrame(d)

# Лямбда-выражение для распределения значений, аргумент - pandas.Series, 
# возвращаемое значение - массив с количеством каждого из значений
# Из вводных данных s с помощью value_counts() находим частоту каждого из значений, 
# и пока в нашем словаре есть элементы, будет работать цикл, запускаемый items().
# Чтобы выходные данные не менялись с каждым запуском цикла, мы используем sorted, 
# который меняет порядок от большего к меньшему
# В итоге, генерируется массив, содержащий строку из следующих компонентов: ключ (k) и значение (v).
cstr = lambda s:[k+":"+str(v) for k,v in sorted(s.value_counts().items())]

# Структура данных Decision Tree
tree = {
    # name: Название этого нода (узла)
    "name":"decision tree "+df0.columns[-1]+" "+str(cstr(df0.iloc[:,-1])),
    # df: Данные, связанные с этим нодом (узлом)
    "df":df0,
    # edges: Список ребер (ветвей), выходящих из этого узла, 
    # или пустой массив, если ниже нет листового узла.
    "edges":[],
}

# Генерацию дерева, у узлов которого могут быть ветви, сохраняем в open
open = [tree]

# Лямба-выражение для вычесления энтропии. 
# Аргумент - pandas.Series、возвращаемое значение - число энтропии
entropy = lambda s:-reduce(lambda x,y:x+y,map(lambda x:(x/len(s))*math.log2(x/len(s)),s.value_counts()))

# Зацикливаем, пока open не станет пустым
while(len(open)!=0):
    # Вытаскиваем из массива open первый элемент,
    # и вытаскиваем данные, хранящиеся в этом узле
    n = open.pop(0)
    df_n = n["df"]

    # В случае, если энтропия этого узла равна 0, мы больше не можем вырастить из него новые ветви
    # поэтому прекращаем ветвление от этого узла
    if 0==entropy(df_n.iloc[:,-1]):
        continue
    # Создаем переменную, в которую будем сохранять список значений атрибута с возможностью разветвления
    attrs = {}
    # Исследуем все атрибуты, кроме последнего столбца класса атрибутов
    for attr in df_n.columns[:-1]:
        # Создаем переменную, которая хранит значение энтропии при ветвлении с этим атрибутом,
        # данные после разветвления и значение атрибута, который разветвляется.
        attrs[attr] = {"entropy":0,"dfs":[],"values":[]}
        # Исследуем все возможные значения этого атрибута. 
        # Кроме того, sorted предназначен для предотвращения изменения порядка массива, 
        # из которого были удалены повторяющиеся значения атрибутов, при каждом его выполнении.
        for value in sorted(set(df_n[attr])):
            # Фильтруем данные по значению атрибута
            df_m = df_n.query(attr+"=='"+value+"'")
            # Высчитываем энтропию, данные и значения сохрнаяем
            attrs[attr]["entropy"] += entropy(df_m.iloc[:,-1])*df_m.shape[0]/df_n.shape[0]
            attrs[attr]["dfs"] += [df_m]
            attrs[attr]["values"] += [value]
            pass
        pass
    # Если не осталось ни одного атрибута, значение которого можно разделить, 
    # прерываем исследование этого узла.
    if len(attrs)==0:
        continue
    # Получаем атрибут с наименьшим значением энтропии
    attr = min(attrs,key=lambda x:attrs[x]["entropy"])
    # Добавляем каждое значение разветвленного атрибута
    # и данные, полученные после разветвления, в наше дерево и в open.
    for d,v in zip(attrs[attr]["dfs"],attrs[attr]["values"]):
        m = {"name":attr+"="+v,"edges":[],"df":d.drop(columns=attr)}
        n["edges"].append(m)
        open.append(m)
    pass

# Выводим дата сет
print(df0,"\n-------------")
# Метод преобразования дерева в символы, аргуметы - tree:структура данных древа,
# indent:присоединяймый к дочернему узлу indent,
# Возвращаемое значение - символьное представление древа.
# Этот метод вызывается рекурсивно для преобразования всех данных в дереве в символы.
def tstr(tree,indent=""):
    # Создаем символьное представление этого узла.
    # Если этот узел является листовым узлом (количество элементов в массиве ребер равно 0), 
    # частотное распределение последнего столбца данных df, связанных с деревом, преобразуется в символы.
    s = indent+tree["name"]+str(cstr(tree["df"].iloc[:,-1]) if len(tree["edges"])==0 else "")+"\n"
    # Зацикливаем все ветви этого узла.
    for e in tree["edges"]:
        # Добавляем символьное представление дочернего узла к символьному представлению родительского узла.
        # Добавляем еще больше символов к indent этого узла.
        s += tstr(e,indent+"  ")
        pass
    return s
# Выводим древо в его символьном представлении.
print(tstr(tree))
