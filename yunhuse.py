import requests
import json
import env

def delete_say(msgId,chatId,chatType):
    Webhook = 'https://chat-go.jwzhd.com/open-apis/v1/bot/recall?token='
    api_url = Webhook + env.token
    headers = {"Content-Type": "application/json; charset=utf-8", }
    data = {
        "msgId": msgId,
        "chatId": chatId,
        "chatType": chatType
    }
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    return json.loads(response.text) 

def detect(content:str):
    # 检测html
    keywords_html = ['<br>','</']
    found_keyword_html=False
    for keyword in keywords_html:
        if keyword in content:
            found_keyword_html = True
            break

    # 检测markdown
    keywords_md=["> ","#",'#',"#","*","`","---",'](','+ ','- ','|']
    found_keyword_md=False
    for keyword in keywords_md:
        if keyword in content:
            found_keyword_md=True
            break

    if found_keyword_html:
        replymode='html'
    elif found_keyword_md:
        replymode='markdown'
    else:
        replymode='text'
    
    return replymode


def bysendyh(a,b,c,sayBYsayMD5):
    if a!='':
        d=detect(a)
        api_url = f"https://chat-go.jwzhd.com/open-apis/v1/bot/send?token={env.token}"
        payload = json.dumps({
            "recvId": str(b),
            "recvType": str(c),
            "contentType": d,
            "content": {
                "text": a
            },
            "parentId": sayBYsayMD5
        })
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(api_url, headers=headers, data=payload)
        data=json.loads(response.text)
        try:
            return data['data']['messageInfo']['msgId']
        except:
            return data


def sendyh(a,b,c):
    if a!='':
        d=detect(a)
        api_url = f"https://chat-go.jwzhd.com/open-apis/v1/bot/send?token={env.token}"
        payload = json.dumps({
            "recvId": str(b),
            "recvType": str(c),
            "contentType": d,
            "content": {
                "text": a
            }
        })
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(api_url, headers=headers, data=payload)
        data=json.loads(response.text)
        try:
            return data['data']['messageInfo']['msgId']
        except:
            return data
    
    
def setting_board(board,group,within):
    a=board
    b=group
    if within=='admin':
        tokento=env.token
    else:
        tokento=within
    if a!="":
        d=detect(a)
        api_url = f"https://chat-go.jwzhd.com/open-apis/v1/bot/board?token={tokento}"
        payload = json.dumps({
            "recvId": str(b),
            "recvType": 'group',
            "contentType": d,
            "content": a
        })
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        response = requests.post(api_url, headers=headers, data=payload)
        return response
    else:
        api_url = f"https://chat-go.jwzhd.com/open-apis/v1/bot/board-dismiss?token={tokento}"
        payload = json.dumps({
            "recvId": str(b),
            "recvType": 'group'
        })
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        response = requests.post(api_url, headers=headers, data=payload)
        return response