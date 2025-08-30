import requests
import json

Token = ''

def WebSend(api_url, headers, data) -> dict:
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    return json.loads(response.text)

class Send:
    def __init__(self):
        Webhook='https://chat-go.jwzhd.com/open-apis/v1/bot/send?token='
        self.api_url = Webhook+Token
        self.headers = {"Content-Type": "application/json; charset=utf-8",}
    def Text(self,recvId:str,recvType:str,text:str,buttons:list=[]):
        data = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "text",
            "content": { 
                "text": text,
                "buttons":[buttons]
            }
        }
        return WebSend(self.api_url,self.headers,data)
    def Markdown(self,recvId:str,recvType:str,markdown:str,buttons:list=[]):
        data = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "markdown",
            "content": {
                "text": markdown,
                "buttons":[buttons]
            }
        }
        return WebSend(self.api_url,self.headers,data)
    def Image(self,recvId:str,recvType:str,imageUrl:str,buttons:list=[]):
        data = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "image",
            "content": {
                "imageUrl": imageUrl,
                "buttons":[buttons]
            }
        }
        return WebSend(self.api_url,self.headers,data)
    def File(self,recvId:str,recvType:str,fileName:str,fileUrl:str,buttons:list=[]):
        data = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "file",
            "content": {
                "fileName": fileName,
                "fileUrl": fileUrl,
                "buttons":[buttons]
            }
        }
        return WebSend(self.api_url,self.headers,data)

class Edit:
    def __init__(self):
        Webhook = 'https://chat-go.jwzhd.com/open-apis/v1/bot/edit?token='
        self.api_url = Webhook+Token
        self.headers = {"Content-Type": "application/json; charset=utf-8",}
    def Text(self,msgId:str,recvId:str,recvType:str,new_text:str,buttons:list=[]):
        data = {
            "msgId": msgId,
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "text",
            "content": {
                "text": new_text,
                "buttons":[buttons]
            }
        }
        return WebSend(self.api_url,self.headers,data)
    def Markdown(self,msgId:str,recvId:str,recvType:str,new_markdown:str,buttons:list=[]):
        data = {
            "msgId": msgId,
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "markdown",
            "content": {
                "text": new_markdown,
                "buttons":[buttons]
            }
        }
        return WebSend(self.api_url,self.headers,data)
    def Image(self,msgId:str,recvId:str,recvType:str,new_image_url:str,buttons:list=[]):
        data = {
            "msgId": msgId,
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "image",
            "content": {
                "imageUrl": new_image_url,
                "buttons":[buttons]
            }
        }
        return WebSend(self.api_url,self.headers,data)
    def File(self,msgId:str,recvId:str,recvType:str,new_file_name:str,new_file_url:str,buttons:list=[]):
        data = {
            "msgId": msgId,
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "file",
            "content": {
                "fileName": new_file_name,
                "fileUrl": new_file_url,
                "buttons":[buttons]
            }
        }
        return WebSend(self.api_url,self.headers,data)


class Messages:
    def __init__(self):
        Webhook = 'https://chat-go.jwzhd.com/open-apis/v1/bot/messages?token='
        self.api_url = Webhook+Token
        self.headers = {"Content-Type": "application/json; charset=utf-8",}
    def Before(self,chat_id:str,chat_type:str,before:int):
        target_url = f"{self.api_url}&chat-id={chat_id}&chat-type={chat_type}&before={before}"
        response = requests.get(target_url, headers=self.headers)
        return json.loads(response.text)
    def After(self,chat_id:str,chat_type:str,message_id:str,after:int):
        target_url = f"{self.api_url}&chat-id={chat_id}&chat-type={chat_type}&message-id={message_id}&after={after-1}"
        response = requests.get(target_url, headers=self.headers)
        return json.loads(response.text)

class Board:
    def __init__(self):
        Webhook = 'https://chat-go.jwzhd.com/open-apis/v1/bot/board?token='
        self.api_url = Webhook+Token
        self.headers = {"Content-Type": "application/json; charset=utf-8",}
    def Text(self,recvId:str,recvType:str,text:str):
        data = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "text",
            "content": text,
        }
        return WebSend(self.api_url,self.headers,data)
    def Markdown(self,recvId:str,recvType:str,markdown:str):
        data = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "markdown",
            "content": markdown,
        }
        return WebSend(self.api_url,self.headers,data)
    def Html(self,recvId:str,recvType:str,html:str):
        data = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": "html",
            "content": html,
        }
        return WebSend(self.api_url,self.headers,data)
    def Dismiss(self,recvId:str,recvType:str):
        data = {
            "recvId": recvId,
            "recvType": recvType,
        }
        api_url = f'https://chat-go.jwzhd.com/open-apis/v1/bot/board-dismiss?token={Token}'
        return WebSend(api_url,self.headers,data)
    class All:
        def __init__(self):
            Webhook = 'https://chat-go.jwzhd.com/open-apis/v1/bot/board-all?token='
            self.api_url = Webhook+Token
            self.headers = {"Content-Type": "application/json; charset=utf-8",}
        def Text(self,text:str):
            data = {
                "contentType": "text",
                "content": text,
            }
            return WebSend(self.api_url,self.headers,data)
        def Markdown(self,markdown:str):
            data = {
                "contentType": "markdown",
                "content": markdown,
            }
            return WebSend(self.api_url,self.headers,data)
        def Html(self,html:str):
            data = {
                "contentType": "html",
                "content": html,
            }
            return WebSend(self.api_url,self.headers,data)
        def Dismiss(self):
            api_url = f'https://chat-go.jwzhd.com/open-apis/v1/bot/board-all-dismiss?token={Token}'
            response = requests.post(api_url, headers=self.headers)
            return json.loads(response.text)

def Delete(msgId:str, chatId:str, chatType:str):
    Webhook = 'https://chat-go.jwzhd.com/open-apis/v1/bot/recall?token='
    api_url = Webhook+Token
    headers = {"Content-Type": "application/json; charset=utf-8",}
    data = {
        "msgId": msgId,
        "chatId": chatId,
        "chatType": chatType
    }
    return WebSend(api_url,headers,data)