import sys
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import wikipedia
wikipedia.set_lang('ru')
import wikipediaapi as wapi
import json
import urllib.request
import requests
from random import randint as randint

token = open('/home/pi/Python-3.8.0/chatbot1/closed.txt').readline()

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

def translate(st):
    try:
        st = st.split()
        wiki1 = wapi.Wikipedia(language = st[0])
        pagew = wiki1.page(' '.join(st[2:]))
        lngs  = pagew.langlinks
        result = lngs[st[1]].title
        return result
    except Exception as err:
        return repr(err)

config = json.loads((open('/home/pi/Python-3.8.0/chatbot1/config.json')).read())			#opening config file and transforming it into dict

def delete(msgs):
    ids = []
    for el in msgs:
        ids.append(el['conversation_message_id'])
    api.messages.delete(delete_for_all = 1, peer_id = prid, conversation_message_ids = ids)

def savecfg(config):
    cfg = open('/home/pi/Python-3.8.0/chatbot1/config.json', 'w')		#saving changes to config.json
    cfg.write(json.dumps(config, indent = 4))					#saving changes to config.json
    cfg.close()								        #saving changes to config.json

def send(ms: str, prid: int, fwdd: bool):
    if fwdd:
        api.messages.send(peer_id = prid, random_id = 0, message = ms, forward = fwd(prid, cmid))
    else:
        api.messages.send(peer_id = prid, random_id = 0, message = ms)

def online_turnon();
    try:            #online may be already enabled
        api.groups.enableOnline(group_id = "203345016")             #enabling community online
    except Exception:
        pass

def main():
    for event in longpoll.listen():         #listening for longpoll api requests
        if event.type == VkBotEventType.MESSAGE_NEW:            
            txt = event.message['text']
            prid = event.message['peer_id']
            cmid = event.message['conversation_message_id']
            row_txt = txt.split('\n')
          
            if ('стату' in txt.lower()) and ('бот' in txt.lower()) and config['ret-st'] == 1:
                send('!статистика 15', prid, False)

            if 'Участники собраны!' in txt and config['ret-st-n'] == 1:
                send('Приготовьтесь к очередному сливу от тимы, ребята )))', prid, False)
                
            if 'бот вики' in txt.lower():
                a = ' '.join(txt.lower().split()[2:])
                try:
                    send(wikipedia.summary(a), prid, True)             #requesting searched page in wikipedia
                    page = wikipedia.page(a)
                    try:
                        upload_ph(page)             #trying to send photo from wikipedia
                    except Exception:
                        send('Не получается найти необходимое изображение =)', prid, True)             #photo not found
                except Exception:
                    send('Не получается найти указанный запрос =)', prid, True)            #page not found
                    
            if 'бот переведи' in txt.lower():
                send('Type a statement to translate in format: \n<Translate-from language (ISO)> <Translate-to language (ISO)> <Statement> \nExample: \nen ru Joe Biden', prid, True)
                send('Reply to this message with your request', prid, True)
            if 'бот выкл' in txt.lower() and event.message['from_id'] == 143757001:
                api.messages.send(peer_id = prid, random_id = 0, message = 'Уже вырубаюсь, хозяин!!!', forward = fwd(prid, cmid))
                api.groups.disableOnline(group_id = "203345016")            #disabling community online
                sys.exit()          #force turnoff
            elif 'бот выкл' in txt.lower() and event.message['from_id'] != 143757001:
                send('Ты не хозяин, не приказывай мне!', prid, True)
                

            if ('Победила мафия, поздравляем!' in row_txt) and ('id143757001' in txt) and config['win-msg-p-m'] == 1:
                api.messages.send(
                    peer_id = prid,
                    random_id = 0,
                    message = 'Совершенно неудивительно, но победу одержал мафиозный MVP в лице [id143757001|Гения]!',
                    forward = fwd(prid, cmid),
                    attachment = ['audio-2001823365_67823365', 'photo-203345016_457239023'])
                
            if ('Победил город, поздравляем!' in row_txt) and 'id143757001' in txt and config['win-msg-p-p'] == 1:
                api.messages.send(
                    peer_id = prid,
                    random_id = 0,
                    message = 'Победил город, MVP встречи - легендарный [id143757001|Mafia King]!',
                    forward = fwd(prid, cmid),
                    attachment = ['audio-2001823365_67823365', 'photo-203345016_457239024'])

                
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
                
            if 'бот кто маф' in txt.lower() and config['who-is-m'] == 1:
                b = api.messages.getConversationMembers(peer_id = prid)
                numb = randint(0, (b['count']-1-len(b['groups'])))
                send(f'Могу смело утверждать, что маф - [id{b["profiles"][numb]["id"]} | {b["profiles"][numb]["first_name"]} ]', prid, True)
                   
            if txt.lower() == 'return cfg':
                send(json.dumps(config, indent = 4), prid, True)
            if txt.lower() == 'add cfg':
                api.messages.send(peer_id = prid, random_id = 0, message = 'Add something missing to config.json:', forward = fwd(prid, cmid))
            if txt.lower() == 'бот абоба' and config['aboba'] == 1:
                api.messages.send(peer_id = prid, random_id = 0, message = '&#127344;&#127345;&#127358;&#127345;&#127344;', forward = fwd(prid, cmid))

            if ('cfg edit' in txt.lower()) and event.message['from_id'] == 143757001:			#checking that user message contains config edit
                    query = txt.lower().split('cfg edit ')[1].split()
                    try:
                        query[1] = int(query[1])
                        if query[0] in config:			#checking if user typed an unexisting parameter
                            config[query[0]] = int(query[1])	#changing config dict due to user changes
                            savecfg(config)							#saving changes to config.json
                            send(f'Parameter "{query[0]}" successfully switched to {query[1]}.', prid, True) #notification that config file has been edited 
                        else:
                            send(f'No such parameter as "{query[0]}" in config.json.', prid, True)
                    except Exception:
                        send('Argument must be 1 or 0, not str', prid, True)

            if ('бот удали' in txt.lower()):
                if 'reply_message' in event.message:
                    delete([event.message.reply_message])
                    delete(event.message)
                elif (event.message['fwd_messages'] != []):
                    delete(event.message['fwd_messages'])
                    delete(event.message)
                else:
                    send('Не получается', prid, True)

            if 'reply_message' in event.message:
                if event.message['reply_message']['text'] ==  'Add something missing to config.json:' and event.message['from_id'] == 143757001:
                    config[txt.split()[0]] = int(txt.split()[1])	                    #changing config dict due to user changes
                    savecfg(config)								                            #saving changes to config.json
                    send(f'Parameter "{txt.split()[0]}" was successfully added.', prid, True)

                if event.message['reply_message']['text'] ==  'Reply to this message with your request':
                    send(f'Your result is: {translate(txt)}', prid, True)                                                              

online_turnon()
while True:
    try:
        main()

    except Exception as e:
        if config['debug'] == 1:
            api.messages.send(peer_id = prid, random_id = 0, message = str(repr(e)))
        else:
            print(e)
        pass

