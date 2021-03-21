import wikipedia
wikipedia.set_lang('ru')
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import sys
import json
import urllib.request
import requests

token = open('/home/pi/Python-3.8.0/chatbot1/closed.txt').readline()			#opening config file and transforming it into dict

vk = vk_api.VkApi(token=token)
vk._auth_token()
api = vk.get_api()
longpoll = VkBotLongPoll(vk, "203345016")           #authorizing to vk with token & community id

def fwd(prid, cmids):
    x = {}					#creating empty dict()
    x['peer_id'] = prid				#adding message peer id to dict
    x['conversation_message_ids'] = [cmids]	#adding id's of messages needed to reply to dict
    x['is_reply'] = 1				#adding flag of replying to message (forward if 0)
    return json.dumps(x)			#making a JSON file from dict

def upload_ph(page):
    json_data = json.loads(requests.get('http://ru.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='+page.title).text)	#finding the page with the url needed			
    image_url = list(json_data['query']['pages'].values())[0]['original']['source']			#cropping image url 
    urllib.request.urlretrieve(image_url, image_url.split('/')[-1])             			#downloading image
    vk_upload_url = api.photos.getMessagesUploadServer(peer_id = prid)['upload_url']            	#receiving server upload url
    files = {'photo': open(image_url.split('/')[-1], 'rb')}						#opening photo to upload
    uploaded_photo = (requests.post(vk_upload_url, files = files)).text             			#uploading photo to server and receiving reply
    ready_2_send = json.loads(uploaded_photo)
    sent = (api.photos.saveMessagesPhoto(photo = ready_2_send['photo'], server = ready_2_send['server'], hash = ready_2_send['hash']))[0]            #saving uploaded photo in VK
    api.messages.send(peer_id = prid, random_id = 0, forward = fwd(prid, cmid), attachment = str('photo' + str(sent['owner_id']) + '_' + str(sent['id'])))          #sending photo as message

config = json.loads((open('/home/pi/Python-3.8.0/chatbot1/config.json')).read())

try:            #online may be already enabled
    api.groups.enableOnline(group_id = "203345016")             #enabling community online
except Exception:
    pass
while True:
    try:
        for event in longpoll.listen():         #listening for longpoll api requests
            if event.type == VkBotEventType.MESSAGE_NEW:            
                txt = event.message['text']
                prid = event.message['peer_id']
                cmid = event.message['conversation_message_id']
                row_txt = txt.split('\n')
                
                if config['ret-m-pl'] == 1:
                    if 'Статистика проведённых игр в беседе' in event.message['text']:
                        for i in range(len(row_txt)):
                            if 'М.Калинина' in row_txt[i]:
                                if i - 2 == 1:
                                    b = 'Маринка сейчас на первом месте, но это ненадолго :))'
                                else:
                                    b = 'Маринка сейчас на ' + str(i-2) + ' месте =)))'
                                api.messages.send(peer_id = prid, random_id = 0, message = b)
        #                        api.messages.send(peer_id = event.message['peer_id'], random_id = 0, attachment = 'photo-203345016_457239017')


                if 'бот' and 'стату' in txt.lower():
                    api.messages.send(peer_id = prid, random_id = 0, message = '!статистика 15')

                if 'Участники собраны!' in txt:
                    api.messages.send(peer_id = prid, random_id = 0, message = 'Приготовьтесь к очередному сливу от тимы, ребята )))')
                    
                if 'бот вики' in txt.lower():
                    a = ' '.join(txt.lower().split()[2:])
                    try:
                        api.messages.send(peer_id = prid, random_id = 0, message = wikipedia.summary(a), forward = fwd(prid, cmid))             #requesting searched page in wikipedia
                        page = wikipedia.page(a)
                        try:
                            upload_ph(page)             #trying send photo from wikipedia
                        except Exception:
                            api.messages.send(peer_id = prid, random_id = 0, message = 'Не получается найти необходимое изображение =)', forward = fwd(prid, cmid))             #photo not found
                    except Exception:
                        api.messages.send(peer_id = prid, random_id = 0, message = 'Не получается найти указанный запрос =)', forward = fwd(prid, cmid))            #page not found
                        
                
                if 'бот выкл' in txt.lower() and event.message['from_id'] == 143757001:
                    api.messages.send(peer_id = prid, random_id = 0, message = 'Уже вырубаюсь, хозяин!!!', forward = fwd(prid, cmid))
                    api.groups.disableOnline(group_id = "203345016")            #disabling community online
                    sys.exit()          #force turnoff
                elif 'бот выкл' in txt.lower() and event.message['from_id'] != 143757001:
                    api.messages.send(peer_id = prid, random_id = 0, message = 'Ты не хозяин, не приказывай мне!', forward = fwd(prid, cmid))
                    

                if ('Победила мафия, поздравляем!' in row_txt) and ('[id143757001|П.Крупович]' in txt) and config['win-msg-p-m'] == 1:
                    api.messages.send(
                        peer_id = prid,
                        random_id = 0,
                        message = 'Совершенно неудивительно, но победу одержал мафиозный MVP в лице [id143757001|Гения]!',
                        forward = fwd(prid, cmid),
                        attachment = 'audio-2001823365_67823365')
                    
                if ('Победил город, поздравляем!' in row_txt) and 'id143757001' in txt and config['win-msg-p-p'] == 1:
                    api.messages.send(
                        peer_id = prid,
                        random_id = 0,
                        message = 'Победил город, MVP встречи - легендарный [id143757001|Mafia King]!',
                        forward = fwd(prid, cmid),
                        attachment = 'audio-2001823365_67823365')

                    
                if ('Победила мафия, поздравляем!' in row_txt) and 'id362871142' in txt and config['win-msg-v-m'] == 1:
                    api.messages.send(
                        peer_id = prid,
                        random_id = 0,
                        message = 'Забыли кто отец этой игры? Напомню! Это - неотразимый [id362871142|MVP]!',
                        forward = fwd(prid, cmid),
                        attachment = 'audio-2001462885_81462885')
                    
                elif ('Победил город, поздравляем!' in row_txt) and 'id362871142' in txt and config['win-msg-v-p'] == 1:
                    api.messages.send(
                        peer_id = prid,
                        random_id = 0,
                        message = 'Победил город, а нагнул всех - [id362871142|WashedKing]!!!',
                        forward = fwd(prid, cmid),
                        attachment = 'audio-2001462885_81462885')
                if txt.lower() == 'edit cfg' and event.message['from_id'] == 143757001:				#checking for config edit request
                    api.messages.send(peer_id = prid, random_id = 0, message = 'Make some changes in config.json:', forward = fwd(prid, cmid))			#sending editing notification
                if event.message['reply_message']['text'] ==  'Make some changes in config.json:' and event.message['from_id'] == 143757001:			#checking that user message contains config edit
                    if txt.split()[0] in config:			#checking if user typed an unexisting parameter
                        config[txt.split()[0]] = int(txt.split()[1])	#changing config dict due to user changes
                        cfg = open('/home/pi/Python-3.8.0/chatbot1/config.json', 'w')		#saving changes to config.json
                        cfg.write(json.dumps(config))						#saving changes to config.json
                        cfg.close()								#saving changes to config.json
                        api.messages.send(							
                            peer_id = prid,
                            random_id = 0,
                            message = ('Parameter "' + txt.split()[0] + '" successfully switched to ' + txt.split()[1] + '.'), #notification that config file has been edited 
                            forward = fwd(prid, cmid))
                        api.messages.send(peer_id = prid, random_id = 0, message = ('config.json is now ' + str(config))) 	#returning new config.json
                    else:
                        api.messages.send(
                            peer_id = prid,
                            random_id = 0,
                            message = ('No such parameter as "' + txt.split()[0] + '" in config.json.'),
                            forward = fwd(prid, cmid))
                            

                            
                            
    except Exception:
        pass



                
'''
            if 'Игра начнётся если наберётся достаточное количество' in event.message['text']:
                api.messages.send(peer_id = event.message['peer_id'], random_id = 0, message = 'Живо все зашли @all @all @all')

            if 'Игра начнётся если наберётся достаточное количество' in event.message['text']:
                api.messages.send(peer_id = event.message['peer_id'], random_id = 0, message = 'Живо все зашли @all @all @all')
						
'''


#vk.messages.send( #Отправляем собщение
#    chat_id=1,
#    random_id=0,
#    message='!статистика')
#exit()
