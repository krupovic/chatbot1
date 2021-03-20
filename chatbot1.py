import wikipedia
wikipedia.set_lang('ru')
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import sys
import json
import urllib.request
import requests

vk = vk_api.VkApi(token='d0d4c5923dec69c9927712772f9ece9ce681a3e1cb831cf344383f1247d36503ed1ebcc463067b83c02bd')
vk._auth_token()
api = vk.get_api()
longpoll = VkBotLongPoll(vk, "203345016")           #authorizing to vk with token & community id

def fwd(prid, cmids):
    x = {}
    x['peer_id'] = prid
    x['conversation_message_ids'] = [cmids]
    x['is_reply'] = 1
    return json.dumps(x)

def upload_ph(page):
    for i in range(len(page.images)):           #searching for .jpg format image in wiki image list
        if '.jpg' in page.images[i]:
            image_url = page.images[i]
            filename = image_url.split('/')[-1]             #taking file name from image url
            break
    urllib.request.urlretrieve(image_url, filename)             #downloading image
    vk_upload_url = api.photos.getMessagesUploadServer(peer_id = prid)['upload_url']            #getting server upload url
    files = {'photo': open(filename, 'rb')}
    uploaded_photo = (requests.post(vk_upload_url, files = files)).text             #uploading photo to server and getting reply
    ready_2_send = json.loads(uploaded_photo)
    sent = api.photos.saveMessagesPhoto(photo = ready_2_send['photo'], server = ready_2_send['server'], hash = ready_2_send['hash'])            #saving uploaded photo in VK
    sent = sent[0]
    api.messages.send(peer_id = prid, random_id = 0, forward = fwd(prid, cmid), attachment = str('photo' + str(sent['owner_id']) + '_' + str(sent['id'])))          #sending photo as message

api.groups.enableOnline(group_id = "203345016")             #enabling community online

while True:
    for event in longpoll.listen():         #listening for longpoll api requests
        if event.type == VkBotEventType.MESSAGE_NEW:            
            txt = event.message['text']
            prid = event.message['peer_id']
            cmid = event.message['conversation_message_id']
            row_txt = txt.split('\n')

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
                    
            if 'Статистика проведённых игр в беседе' in event.message['text']:
                for i in range(len(row_txt)):
                    if 'М.Калинина' in row_txt[i]:
                        if i - 2 == 1:
                            b = 'Маринка сейчас на первом месте, но это ненадолго :))'
                        else:
                            b = 'Маринка сейчас на ' + str(i-2) + ' месте =)))'
                        api.messages.send(peer_id = prid, random_id = 0, message = b)
#                        api.messages.send(peer_id = event.message['peer_id'], random_id = 0, attachment = 'photo-203345016_457239017')

            if 'бот выкл' in txt.lower() and event.message['from_id'] == 143757001:
                api.messages.send(peer_id = prid, random_id = 0, message = 'Уже вырубаюсь, хозяин!!!', forward = fwd(prid, cmid))
                api.groups.disableOnline(group_id = "203345016")            #disabling community online
                sys.exit()          #force turnoff
            elif 'бот выкл' in event.message['text'].lower() and event.message['from_id'] != 143757001:
                api.messages.send(peer_id = prid, random_id = 0, message = 'Ты не хозяин, не приказывай мне!', forward = fwd(prid, cmid))
                

            if ('Победила мафия, поздравляем!' in row_txt) and ('[id143757001|П.Крупович]' in txt):
                api.messages.send(
                    peer_id = prid,
                    random_id = 0,
                    message = 'Совершенно неудивительно, но победу одержал мафиозный MVP в лице [id143757001|Гения]!',
                    forward = fwd(prid, cmid),
                    attachment = 'audio-2001823365_67823365')
                
            if ('Победил город, поздравляем!' in row_txt) and 'id143757001' in txt:
                api.messages.send(
                    peer_id = prid,
                    random_id = 0,
                    message = 'Победил город, MVP встречи - легендарный [id143757001|Mafia King]!',
                    forward = fwd(prid, cmid),
                    attachment = 'audio-2001823365_67823365')

                
            if ('Победила мафия, поздравляем!' in row_txt) and 'id362871142' in txt:
                api.messages.send(
                    peer_id = prid,
                    random_id = 0,
                    message = 'Забыли кто отец этой игры? Напомню! Это - неотразимый [id362871142|MVP]!',
                    forward = fwd(prid, cmid),
                    attachment = 'audio-2001462885_81462885')
                
            elif ('Победил город, поздравляем!' in row_txt) and 'id362871142' in txt:
                api.messages.send(
                    peer_id = prid,
                    random_id = 0,
                    message = 'Победил город, а нагнул всех - [id362871142|WashedKing]!!!',
                    forward = fwd(prid, cmid),
                    attachment = 'audio-2001462885_81462885')



                
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
