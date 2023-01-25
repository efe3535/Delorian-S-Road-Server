import paho.mqtt.client as mqtt
from string import ascii_lowercase
from random import sample
from base64 import b64decode
from os import chdir
from json import dumps, loads
import sqlite3
from time import sleep
from requests import get
from datetime import datetime

conn = sqlite3.connect("server.db")

cur = conn.cursor()
# cur.execute("CREATE TABLE IF NOT EXISTS calismalar (id,koorx,koory,reason,hasphoto,photopath)")
cur.execute('''CREATE TABLE IF NOT EXISTS calismalar
         (id integer primary key AUTOINCREMENT,
          koorx varchar(20) NOT NULL,
          koory varchar(20) NOT NULL,
          reason varchar(256) NOT NULL,
          descr varchar(256),
          timestamp varchar(16),
          ended INTEGER NOT NULL,
          hasphoto INTEGER NOT NULL,
          photopath varchar(20))''')
conn.commit()

exists = False

client = mqtt.Client()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe("esp32/images")
    client.subscribe("esp32/setdone")
    client.subscribe("esp32/coordinates")
    client.subscribe("esp32/koorbyid")
    client.subscribe("esp32/calismalar")
    client.subscribe("esp32/reponse")
    client.subscribe("esp32/sendphoto")
    client.subscribe("esp32/photobyid")
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    exists = False
    
    if msg.topic == "esp32/setdone":
        query = "UPDATE calismalar SET ended=1 WHERE id="
        cur.execute(query + msg.payload.decode())
        conn.commit()
        

    elif msg.topic == "esp32/coordinates":
        # print("coordinates\n", msg.payload)
        koorXlist = cur.execute("SELECT koorx FROM calismalar").fetchall()
        koorYlist = cur.execute("SELECT koory FROM calismalar").fetchall()

            
        if len(koorXlist) > 0 and len(koorYlist) > 0: # Veri tabanı dolu ise
            for koorX in koorXlist: # Koordinatların X eksenlerinin olduğu listede gezin
                koorXlist = cur.execute("SELECT koorx FROM calismalar").fetchall() # liste güncelle
                koorYlist = cur.execute("SELECT koory FROM calismalar").fetchall() # liste güncelle

                # Mutlak değer ( yeni gelen koordinatlar - veritabanındaki koordinatlar ) 0.0005'ten küçük ise (GPS sapmalarını ve aynı konumun eklenmesini önlemek amacıyla)

                # if((abs(float(msg.payload.decode().split(",")[0]) - float(list(koorX)[0])) < 0.0005 or abs(float(msg.payload.decode().split("?")[0].split(",")[1]) - float(list(koorX)[0])) < 0.0005) and (abs(float(list(koorYlist[koorXlist.index(koorX)])[0]) - float(msg.payload.decode().split("-")[0].split(",")[1])) < 0.0005)):
                if(abs(float(msg.payload.decode().split(",")[0]) - float(list(koorX)[0])) < 0.0005) and (abs(float(list(koorYlist[koorXlist.index(koorX)])[0]) - float(msg.payload.decode().split(",")[1].split("?")[0])) < 0.0005):
                    exists = True
                    break
                else:
                    exists = False
                
                    """
                    if abs(float(list(koorX)[0]) - float(msg.payload.decode().split("-")[0].split(",")[0])) < 0.0005 and abs(float(list(koorYlist[koorXlist.index(koorX)])[0]) - float(msg.payload.decode().split("-")[0].split(",")[1])) < 0.0005:
                        exists = True
                        print("ZATEN VAR!!!")
                        break
                    elif abs(float(list(koorX)[0]) - float(msg.payload.decode().split("-")[0].split(",")[0])) >= 0.0005 and abs(float(list(koorYlist[koorXlist.index(koorX)])[0]) - float(msg.payload.decode().split("-")[0].split(",")[1])) >= 0.0005:
                        exists = False
                    """
                
            if exists == False:
                xkoor = str(msg.payload.decode("utf-8")).split(",")[0]
                ykoor = str(msg.payload.decode("utf-8")).split(",")[1].split("?")[0]
                # if str(msg.payload.decode("utf-8")).split(",")[0][0] == "-":
                #    xkoor = "-"+str(msg.payload.decode("utf-8")).split(",")[1].split("-")[0]

                reason = str(msg.payload.decode("utf-8")).split("?")[1]
                success = True
                try:
                    descr = get(f"https://nominatim.openstreetmap.org/search.php?q={xkoor},{ykoor}&polygon_geojson=1&format=json", headers={"Accept-Language":"tr"})
                except:
                    success=False
                
                if success:
                    descr = loads(descr.content)[0]["display_name"]
                else:
                    descr = "Yer tayin edilemedi."
                cur.execute(
                    "INSERT INTO calismalar(koorx,koory,reason,descr,timestamp,ended,hasphoto,photopath) VALUES (?,?,?,?,?,?,?,?)", 
                    (
                        xkoor, 
                        ykoor, 
                        reason, 
                        descr,
                        str(datetime.timestamp(datetime.now())*1000),
                        0,
                        0,
                        ""
                    )
                );
                conn.commit()
                exists = True
                
        else: # Veritabanı boş ise 
            xkoor = str(msg.payload.decode("utf-8")).split(",")[0]
            ykoor = str(msg.payload.decode("utf-8")).split(",")[1].split("?")[0]
            reason = str(msg.payload.decode("utf-8")).split(",")[1].split("?")[1]

            descr = get(f"https://nominatim.openstreetmap.org/search.php?q={xkoor},{ykoor}&polygon_geojson=1&format=json", headers={"Accept-Language":"tr"})
                
            if(descr.status_code == 200):
                descr = loads(descr.content)[0]["display_name"]
                cur.execute("INSERT INTO calismalar(koorx,koory,reason,descr,timestamp,ended,hasphoto,photopath) VALUES (?,?,?,?,?,?,?,?)", 
                    ( 
                        xkoor,
                        ykoor,
                        reason,
                        descr,
                        str(datetime.timestamp(datetime.now())*1000),
                        0,
                        0,
                        ""
                    )
                )
                conn.commit()

    elif msg.topic == "esp32/calismalar":
        calismalar = cur.execute("SELECT id,koorx,koory,reason,descr,timestamp,ended,hasphoto from calismalar").fetchall()
        client.publish( "esp32/responsecalismalar", dumps({"calismalar":[list(calisma) for calisma in calismalar]}))
    elif msg.topic == "esp32/koorbyid":
        try:
            koor = cur.execute("SELECT id,koorx,koory,reason,descr,hasphoto,photopath FROM calismalar WHERE id = "+ msg.payload.decode()).fetchall()
            client.publish("esp32/responsekoorbyid", str(koor))
        except:
            koor = cur.execute("SELECT id,koorx,koory,reason,hasphoto,photopath FROM calismalar WHERE id = "+ msg.payload.decode()).fetchall()
            client.publish("esp32/responsekoorbyid", str(koor))
    elif msg.topic == "esp32/sendphoto":
        # addPhoto = cur.execute(f"UPDATE calismalar SET hasphoto = 1 WHERE id="+ msg.payload.decode().split(',')[0])
        # addPhoto = cur.execute(f"UPDATE calismalar SET photopath = {str(msg.payload.decode().split(',')[1:])} WHERE id={msg.payload.decode().split(',')[0]}")
        # conn.commit()
        hasPhotoAlready = cur.execute("SELECT hasphoto FROM calismalar WHERE id =?",(msg.payload.decode().split(",")[0])).fetchall()
        if(str(list(hasPhotoAlready[0])[0]) != "1"):
            updateId = cur.execute(f"UPDATE calismalar SET hasphoto = 1 WHERE id=?", (msg.payload.decode().split(',')[0]))
            addPhoto = cur.execute(f"UPDATE calismalar SET photopath = ? WHERE id=?", (str(msg.payload.decode().split(',')[1:]), msg.payload.decode().split(',')[0]))
        elif(str(list(hasPhotoAlready[0])[0]) == "1"):
            getPhotos = cur.execute("SELECT photopath FROM calismalar WHERE id=?",(msg.payload.decode().split(",")[0])).fetchall()
            addPhoto = cur.execute(f"UPDATE calismalar SET photopath = ? WHERE id=?", ("📷".join(list(getPhotos[0])) +"📷"+ str(msg.payload.decode().split(',')[1:]), msg.payload.decode().split(',')[0]))            

        conn.commit()
    elif msg.topic == "esp32/photobyid":
        photo = cur.execute("SELECT photoPath FROM calismalar WHERE id = ?", (msg.payload.decode())).fetchall()
        # print(list(photo[0])[0])

        client.publish("esp32/responsephotobyid", str(list(photo[0])[0]))
        conn.commit()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 3600)

client.loop_forever()