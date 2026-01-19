import requests
import json
import env
import re

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

class TextTypeDetector:
    def __init__(self):
        # 预编译正则表达式
        self.multiline_code_pattern = re.compile(r'(```|~~~).*?\1', re.DOTALL)
        self.inline_code_pattern = re.compile(r'`[^`]*`')
        self.html_tag_pattern = re.compile(r'<([^>]+)>')

        # 合并后的 Markdown 正则表达式
        self.markdown_combined_pattern = re.compile(
            r'|'.join([
                r'^\s*#{1,6}\s+.*',      # 标题
                r'^\s*>\s+',              # 引用块
                r'^\s*[-*+]\s+',          # 无序列表
                r'^\s*[-*+]\s+\[[ xX]\]',# 任务列表
                r'\*\*[^*]+\*\*',         # 加粗
                r'__[^_]+__',             # 加粗（替代语法）
                r'\*[^*]+\*',             # 斜体
                r'_[^_]+_',               # 斜体（替代语法）
                r'!\[[^\]]*\]\([^)]*\)',  # 图片
                r'\[[^\]]*\]\([^)]*\)',   # 链接
                r'\|\s*[^|]+\s*\|',       # 表格
                r'~~[^~]+~~',             # 删除线
                r'^\s*`{3,}\w*$',         # 代码块起始行
            ]),
            re.MULTILINE
        )

        # 占位符 
        self.MULTILINE_CODE_PLACEHOLDER = "```\n!@&MULTILINECODE&@!\n```"
        self.INLINE_CODE_PLACEHOLDER = "```\n!@&INLINECODE&@!\n```"
        self.ZZBDS_PLACEHOLDER = "!@ZZBDSINECODE&@!"

    def detect(self, s: str) -> str:
        # Step 1: 处理代码块和行内代码
        if '`' in s:
            backtick_count = s.count('`')
            if backtick_count % 2 != 0:
                return 'text'

            s = self.multiline_code_pattern.sub(self.MULTILINE_CODE_PLACEHOLDER, s)
            s = self.inline_code_pattern.sub(self.INLINE_CODE_PLACEHOLDER, s)

        # Step 2: 替换 .* 为占位符
        if '.*' in s:
            s = s.replace(".*", self.ZZBDS_PLACEHOLDER)

        # 检查是否有类似 Markdown 的伪标签（如 :smile:、.class）
        tag_match = re.search(self.html_tag_pattern, s)
        if tag_match:
            tag = tag_match.group(1).strip()
            if '"' not in tag:
                if ' ' not in tag and ('.' in tag or ':' in tag):
                    return 'markdown'
            return 'html'

        # Step 4: 检测 Markdown
        if self.markdown_combined_pattern.search(s):
            return 'markdown'

        # Step 5: 默认为文本
        return 'text'


    def bysendyh(self,a,b,c,sayBYsayMD5):
        if a!='':
            d=self.detect(a)
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


    def sendyh(self,a,b,c):
        if a:
            d=self.detect(a)
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
        
        
    def setting_board(self,board,group,within):
        a=board
        b=group
        if within=='admin':
            tokento=env.token
        else:
            tokento=within
        if a!="":
            d=self.detect(a)
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
            return json.loads(response.text)
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
            return json.loads(response.text)

def send_button(content,recv_id, recv_type,type='text'):
    url = f'https://chat-go.jwzhd.com/open-apis/v1/bot/send?token={env.token}'
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    payload = {
        'recvId': recv_id,
        'recvType': recv_type,
        'contentType': type,
        'content': content
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print('Response sent successfully:', response.json())
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        print('Error sending response:', e)
        return None

def change_message(msgId,recvId,recvType,contentType,content):
    api_url = f"https://chat-go.jwzhd.com/open-apis/v1/bot/edit?token={env.token}"
    payload = json.dumps({
        "msgId": msgId,
        "recvId": recvId,# 群id
        'recvType': recvType,# group?user?
        'contentType': contentType,# html?
        'content': {
            "text": content
        }
    })
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    response = requests.post(api_url, headers=headers, data=payload)
    return response

def yunhulist(group_id, message_id=None, before=None, after=None):
    """通用的消息获取函数，符合API文档规范"""
    base_url = "https://chat-go.jwzhd.com/open-apis/v1/bot/messages"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    params = {
        "token": env.token,
        "chat-id": group_id,
        "chat-type": "group"  # 当前只支持群聊
    }
    
    # 根据文档添加可选参数
    if message_id is not None:
        params["message-id"] = message_id
    if before is not None:
        params["before"] = before
    if after is not None:
        params["after"] = after
    
    try:
        response = requests.get(
            base_url,
            params=params,
            headers=headers,
            timeout=10
        )
        
        # 记录详细错误信息
        if response.status_code != 200:
            print(f"HTTP 错误({response.status_code}) for group {group_id}: {response.text}")
            return []
        
        data = response.json()
        if data.get("code") != 1:
            print(f"API 错误({data.get('code')}) for group {group_id}: {data.get('msg', '未知错误')}")
            return []
            
        # 返回消息列表和总数（根据文档规范）
        return data.get("data", {}).get("list", [])
    
    except requests.exceptions.RequestException as e:
        print(f"请求失败 for group {group_id}: {str(e)}")
        return []
    except Exception as e:
        print(f"处理消息时发生意外错误 for group {group_id}: {str(e)}")
        return []