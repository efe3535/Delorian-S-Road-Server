Sunucunuzda MQTT broker'ınız bulunmalı, 1883 ve 1923 portlarında dinleme yapmalı. 1883, TCP bağlantıları için ve 1923, WebSocket bağlantıları için. Uygulamada WebSocket kullanıldı. ESP32 ise TCP üzerinden gönderim yapmaktadır.
Uygulama kodlarında ip.js dosyasına sunucunuzun IP adresini giriniz! ESP32 kodunda da IP adresini girmeyi unutmayınız!

Biz, sunucumuzda Mosquitto MQTT broker'ını tercih ettik. 
Mosquitto configimiz:
/etc/mosquitto/mosquitto.conf dosyası:
```
listener 1883

allow_anonymous true

persistence true
persistence_location /var/lib/mosquitto/

log_dest file /var/log/mosquitto/mosquitto.log

include_dir /etc/mosquitto/conf.d


listener 1923
protocol websockets
```
