import threading, requests, json, time
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime


nextupdate = time.time()

classes = ("Raider",
	"Necromancer",
	"Assassin",
	"Elementalist",
	"Pathfinder",
	"Inquisitor",
	"Gladiator",
	"Slayer",
	"Chieftain",
	"Juggernaut",
	"Guardian",
	"Champion",
	"Deadeye",
	"Saboteur",
	"Trickster",
	"Berserker",
	"Hierophant",
	"Occultist",
	"Ascendant",
	"Witch",
	"Templar",
	"Duelist",
	"Marauder",
	"Scion",
	"Shadow",
	"Ranger")

ranks = (100,500,2000,5000)

##load settings file
with open('settings.txt','r') as file:
        settings = json.loads(file.read())
        settings = settings[0]['settings']
        file.close()   

def classcount():
        if(settings['createclasspage'] == 0):
                print("skipped building classes.html")
                return;
        print("Building classes.html")
        login = settings['database']
        temp2 = time.time();
        output = "<?php header('Access-Control-Allow-Origin: {}');?>classname,top100,top500,top2000,top5000\n".format(settings['xhraccess'])
        cnx = mysql.connector.connect(user=login['user'], password=login['password'],
                              host=login['hostname'],
                              database=login['database'])
        cursor = cnx.cursor()
        
        for classname in classes:
                output += classname
                for rank in ranks:
                        query = "SELECT COUNT(*) AS total FROM leaderboard WHERE time=(SELECT time FROM leaderboard ORDER BY time DESC LIMIT 1) AND classname='{}' AND rank <= {}".format(classname,rank)
                        cursor.execute(query)
                        output += "," + str(cursor.fetchone()[0])
                output += "\n"

        with open(settings['pathToclasses'],'w') as file:
                file.write(output)
                file.close()
        print("Finished building classes.html in {} seconds".format(time.time() - temp2))
        cursor.close()
        cnx.close()

def update():
        login = settings['database']
        cnx = mysql.connector.connect(user=login['user'], password=login['password'],
                              host=login['hostname'],
                              database=login['database'])
        cursor = cnx.cursor()
        timestamp = time.time()
        fetchtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        offset = 0
        while(offset < settings['ranks']):
                payload = {'offset' : offset, 'limit' : 200}
                temp1 = time.time()
                url  = "http://api.pathofexile.com/ladders/{}".format(settings['league'])
                r = requests.get(url,params=payload)
                data = r.json()['entries']
                insert = "INSERT INTO leaderboard VALUES "
                length = len(data)
                for obj in data:
                        rank = obj['rank']
                        name = obj['character']['name']
                        account = obj['account']['name']
                        isdead = obj['dead']
                        classname = obj['character']['class']
                        exp = obj['character']['experience']
                        level = obj['character']['level']
                        insert += "('{}', {}, '{}', '{}', {}, {}, '{}', '{}')".format(name,exp,fetchtime,account,level,rank,classname,isdead)
                        if(data.index(obj) != length - 1):
                                insert += ", "
                
                cursor.execute(insert)
                
                print("Added rows {} to {} in {} seconds".format(offset,offset+200,time.time()-temp1))
                offset += 200
                
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Finished after {} seconds".format(time.time() - timestamp))       


def checktime():
  threading.Timer(5.0, checktime).start()
  global nextupdate
  if(time.time() > nextupdate):
          nextupdate = time.time() + settings['updateinterval'];          
          print("Updating...")
          update()
          classcount()
          
checktime()

