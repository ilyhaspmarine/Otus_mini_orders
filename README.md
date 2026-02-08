# Домашнее задание №7
## Restfull

### Сервис заказов
#### Функционал
- Создание нового заказа
- Отправка писем счастья при успешной оплате (сообщение в брокер сервису нотификаций)
- Отправка писем горя при провале оплаты (сообщение в брокер сервису нотификаций)

### ПОДГОТОВКА
#### в /etc/hosts прописываем
```
127.0.0.1 arch.homework 
```

#### Запускаем docker
любым вариантом, у меня docker desktop с виртуализацией VT-d

#### Запускаем minikube
```
minikube start --driver=docker
```

#### NGINX
Считам, что с прошлых дз он всё ещё в кластере


### СТАВИМ ПРИЛОЖЕНИЕ
#### Создаем namespace под сервис аутентификации
```
kubectl create namespace order
```

#### "Внешняя" поставка секретов в кластер
##### Секрет с данными для подключения к БД
```
kubectl apply -f ./secret/order_secret.yaml -n order
```

#### Переходим в директорию с чартом
```
cd ./order-app
```

#### Загружаем чарты зависимостей
```
helm dependency update
```

#### Возвращаемся в корень
```
cd ../
```

#### Устанавливаем чарт сервиса
```
helm install order order-app -n order
```

#### Включаем (и не закрываем терминал)
```
minikube tunnel
```

#### Проверяем health-check (в новом окне терминала)
```
curl http://arch.homework/order/health/
```


### КАК УДАЛИТЬ ПРИЛОЖЕНИЕ
#### Удаляем чарт и БД
```
helm uninstall order -n order
```

#### Удаляем секрет
```
kubectl delete secret order-db-secret -n order
```

#### Удаляем PVC, оставшиеся от БД
```
kubectl delete pvc -l app.kubernetes.io/name=order-postgresql,app.kubernetes.io/instance=order -n order
```

#### Сносим PV, оставшиеся от БД (если reclaimPolicy: Retain)
```
kubectl get pv -n order
```
Смотрим вывод, узнаем <имя PV> (к сожалению, меток у него не будет - я проверил)
```
kubectl delete pv <имя PV> -n order
```

### Готово!