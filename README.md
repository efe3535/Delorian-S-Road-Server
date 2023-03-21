Sunucunuzda MQTT broker'ınız bulunmalı, 1883 ve 1923 portlarında dinleme yapmalı. 1883, TCP bağlantıları için ve 1923, WebSocket bağlantıları için. Uygulamada WebSocket kullanıldı. ESP32 ise TCP üzerinden gönderim yapmaktadır.
Uygulama kodlarında ip.js dosyasına sunucunuzun IP adresini giriniz! ESP32 kodunda da IP adresini girmeyi unutmayınız!

`server.db` dosyası bir adet yol çalışması içermektedir, test için kullanabilirsiniz. Dilerseniz, bu dosyayı silerek programın kendi veritabanını oluşturmasını da sağlayabilirsiniz!

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

Ek olarak Express JS üzerinde bir giriş sunucumuz çalışıyor. Bu sunucu 3366 portunu kullanmakta olup users.json dosyasında kullanıcıları depolar.
`sroad_user_service` dizininde `npm install` çalıştırıp gerekli dosyaları indirdikten sonra `npm start` ile sunucunuzu başlatabilirsiniz.
