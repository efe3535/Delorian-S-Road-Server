Sunucunuzda MQTT broker'ınız bulunmalı, 1883 ve 1923 portlarında dinleme yapmalı. 1883, TCP bağlantıları için ve 1923, WebSocket bağlantıları için. Uygulamada WebSocket kullanıldı. ESP32 ise TCP üzerinden gönderim yapmaktadır.
Uygulama kodlarında ip.js dosyasına sunucunuzun IP adresini giriniz! ESP32 kodunda da IP adresini girmeyi unutmayınız!

Biz, sunucumuzda Mosquitto MQTT broker'ını tercih ettik. 
