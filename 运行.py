import json
import requests
from yunhuSDK import Message, Start, jsonify
import re
import random
import time
import zlib
from datetime import datetime
from datetime import time as dtime
from typing import Dict, List, Tuple, Set, Any, Optional
import json
import traceback
import env
import yunhuse
import tool
import sqlitemodel as table3


# ====== 加载函数 ======
yunhusb = yunhuse.TextTypeDetector()# Yunhu-Send-Basic
sendyh=yunhusb.sendyh
setting_board=yunhusb.setting_board
bysendyh=yunhusb.bysendyh
delyh=yunhuse.delete_say

class BotConfig:
    def __init__(self, storage=None):
        if storage is None:
            storage = table3.SQLiteStorage()
        self.storage = storage
        
        # 加载所有配置
        self.groupset = self.storage.load_groupset()
        self.userset = self.storage.load_userset()
        self.blackset = self.storage.load_config('blackset')
        self.Duddle = self.storage.load_config('Duddle')
        self.controlcenter = self.storage.load_config('controlcenter')
        self.N20_Plan = self.storage.load_config('N20_Plan')
        self.recent_messages = {}
        self.percent = re.compile(r'[%]{3}')

    def save_groupset(self):
        self.storage.save_groupset(self.groupset)
    def save_userset(self):
        self.storage.save_userset(self.userset)
    def save_blackset(self):
        self.storage.save_config('blackset', self.blackset)
    def save_Duddle(self):
        self.storage.save_config('Duddle', self.Duddle)
    def save_controlcenter(self):
        self.storage.save_config('controlcenter', self.controlcenter)
    def save_N20_Plan(self):
        self.storage.save_config('N20_Plan', self.N20_Plan)
config = BotConfig()

class MessageDetector:
    def __init__(self, config):
        self.config = config
        self.groupad_pattern = re.compile(r'(yhfx\.jwznb\.com/share|www\.yhchat\.com/group/homepage)')
        self.yunhu_pattern = re.compile(r'yunhu:[\\/]{2,}')
        self.chuanshanjia_ad_pattern = re.compile(r'yunhu:[\\/]{2,}ad\?id=')
        self.post_detail_pattern = re.compile(r'yunhu://post-detail')
        self.shequ_pattern = re.compile(r'yunhu:[\\/]{2,}alley-detail')
        self.webtext_pattern = re.compile(r'^.*[a-zA-Z][a-zA-Z0-9]*\.[a-zA-Z][a-zA-Z0-9]*.*$|^.*yunhu://[a-zA-Z0-9]*.*$')
        #self.load_config()
        blackset = self.config.blackset or {}
        self.blackman = set(blackset.get("CTBlackman", []))
        self.whiteman = set(blackset.get('CTWhiteman', []))
        self.control_groups = self.config.controlcenter.get("controlgroup", [])
        self.N20 = self.config.N20_Plan
        badad1 = blackset.get("badad1", [])
        badad2 = blackset.get("badad2", [])
        if badad1:
            pattern = '|'.join(badad1)
            self.badad1 = re.compile(pattern, flags=re.IGNORECASE)
        else:
            self.badad1 = None
        if badad2:
            pattern = '|'.join(badad2)
            self.badad2 = re.compile(pattern, flags=re.IGNORECASE)
        else:
            self.badad2 = None
    
    def check_message_type(self, say: str) -> Dict[str, bool]:
        """检测消息类型"""
        return {
            'is_yunhu_ad': bool(self.groupad_pattern.search(say)),
            'is_yunhu_url': bool(self.yunhu_pattern.search(say)),
            'is_chuanshanjia_ad': bool(self.chuanshanjia_ad_pattern.search(say)),
            'is_post_detail': bool(self.post_detail_pattern.search(say)),
            'is_shequ_ad': bool(self.shequ_pattern.search(say)),
            'is_bad_ad1': bool(self.badad1.search(say)) if self.badad1 else False,
            'is_bad_ad2': bool(self.badad2.search(say)) if self.badad2 else False,
            'is_url': bool(self.webtext_pattern.search(say))
        }
    
    def check_main(self, say: str, sayer: str, group: str) -> Tuple[bool, List[str]]:
        """主检测"""
        if sayer not in self.whiteman:
            if sayer not in self.config.recent_messages:
                self.config.recent_messages[sayer] = []
            message_list = self.config.recent_messages[sayer]
            crc32_val = zlib.crc32(say.encode('utf-8')) & 0xFFFFFFFF
            crc32_str = format(crc32_val, '08x')
            message_list.append((crc32_str, group))
            if len(message_list) > 20:
                message_list.pop(0)
            groups_set = {grp for msg, grp in message_list if msg == crc32_str}
            self.config.recent_messages[sayer] = message_list
            if len(groups_set) >= 3:  
                return True, list(groups_set)
            return False, []
        return False,[]
    def detect_ANY(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        group = data["chat"]["chatId"]
        sayer = data["sender"]["senderId"]
        sayerwho = data["sender"]["senderNickname"]
        sayco = data["message"].get("content", {})
        saymode = data['message']['contentType']
        if saymode == 'image' and 'imageName' in sayco:
            say = sayco['imageName']
        elif saymode == 'video' and 'videoUrl' in sayco:
            say = sayco['videoUrl']
        elif saymode == 'post':
            say = sayco.get('text', '')
        elif 'text' in sayco:
            say = sayco['text']
        else:
            say = str(sayco) if sayco else ""
        group_config = self.config.groupset.get(group, {})
        if "NBstWhite" in group_config and sayer in group_config["NBstWhite"]:
            return True, ""
        if 'blackman' in group_config and sayer in group_config['blackman']:
            return False, "用户在群黑名单内"
        if saymode in ['text','markdown','html','post','form'] and 'blackword' in group_config:
            blackwords = group_config['blackword'].split()
            for word in blackwords:
                if any(c in word for c in "[.$({+^*?"):
                    pattern = word
                else:
                    pattern = f'.*{word}.*'
                if re.search(pattern, say):
                    return False, f'用户命中群违规词{pattern}'
        msg_types = self.check_message_type(say)
        if group_config.get('UseCTBlackman',True):
            if sayer in self.blackman:
                return False, "【联防】用户在联防黑名单内"
        if saymode in ['expression', 'sticker']:
            return True, ""
        if saymode in ['text','markdown','html','post','form']:
            if group_config.get('UseCTGoodAD',True):
                if msg_types['is_yunhu_ad']:
                    return False, "【联防】消息是云湖群推广广告"
                if msg_types['is_yunhu_url']:
                    if msg_types['is_post_detail'] or msg_types['is_shequ_ad']:
                        pass
                    elif msg_types['is_chuanshanjia_ad']:
                        return False,"【联防】消息是穿山甲广告"
                    else:
                        return False,"【联防】消息含未知云湖链接"
            if group_config.get('UseCTBadAD',True):
                if msg_types['is_chuanshanjia_ad']:
                    return False, "【联防】消息是穿山甲广告"
        if saymode == 'post':
            return True, ""
        if saymode in ['post','expression','sticker'] and self.N20.get(sayer, 0) >= 20:
            return True, ""
        violation_count = 0
        if True:
            same_msg, groups = self.check_main(say, sayer, group)
            if same_msg:
                reply = f'''<details><summary style="cursor: pointer; outline: none;">{sayer} 在 {groups}:</summary>
                <div style="padding: 10px; margin-top: 6px; border-left: 2px solid #1e90ff; color: #555;">{say}</div></details>'''
                group_count = len(groups)
                if group_count >= 5:
                    self.blackman.add(sayer)
                    self.config.blackset['CTBlackman'] = list(self.blackman)
                    _delete_all_over(sayer,group)
                    for g in self.control_groups:
                        sendyh(f'已自动拉黑 {sayer}', g, 'group')
                    return False, "【联防】用户多群发送消息"
                elif group_count == 4:
                    for g in self.control_groups:
                        sendyh(f'检测到用户{sayer}在{group}又发送了相同言论', g, 'group')
                    violation_count += 1
                elif group_count == 3:
                    _delete_all_over(sayer,group,amount=20,page=1)
                    for g in self.control_groups:
                        sendyh(reply, g, 'group')
                    violation_count += 1
        if saymode not in ['image', 'video']:
            if msg_types['is_bad_ad1'] and (msg_types['is_bad_ad2'] or msg_types['is_url']):
                _delete_all_over(sayer,group,amount=20,page=1)
                violation_count += 1
                reply = f'''<details><summary style="cursor: pointer; outline: none; color: #1e90ff;">{sayer}疑似发送广告:</summary>
                <div style="padding: 10px; margin-top: 6px; border-left: 2px solid #1e90ff; color: #555;">{say}</div></details>'''
                for g in self.control_groups:
                    sendyh(reply, g, 'group')
        group_config = self.config.groupset.get(group, {})
        if violation_count >= 2:
            self.blackman.add(sayer)
            self.config.blackset['CTBlackman'] = list(self.blackman)
            for g in self.control_groups:
                sendyh(f'已自动拉黑{sayer}', g, 'group')
        if group_config.get('UseCTBadAD',True) and violation_count >= 1:
                return False, "【联防】消息是恶意广告或多群发送"
        return True, ""

detector = MessageDetector(config)

def _handle_deletion(group, say ,sayMD5, sayer, sayerwho, reason):
    print('detele',group, sayMD5, sayer, sayerwho)
    delyh(sayMD5, group, "group")

    reply=config.groupset.get(group,{}).get('blackre','已自动拦截（默认拦截提示）')
    if reply:
        if config.percent.search(reply):
            replys = config.percent.split(reply)
            replys = [reply for reply in replys if reply]
            reply = random.choice(replys)
        if reason.startswith('【联防】'):
            if config.groupset[group].get('newuser',True):
                reply=reply+'\n新手模式提醒：遇到不想拦截的人，请加入白名单'
        reply = reply.replace("{name}", sayerwho)
        reply = reply.replace("{uid}", sayer)
        reply = reply.replace("{why}", reason)
        sendyh(reply.strip(), group, 'group')
    
    time.sleep(3)
    botsays = tool.get_bot_messages_after(group, sayMD5, 5)
    for botsay in botsays:
        delyh(botsay,group,'group')
    
    groupset1=config.groupset.get(group,{})
    leader=groupset1.get('leader','').strip()
    reply2=groupset1.get('blackre2','').strip()
    reply2 = reply2.replace("{name}", sayerwho)
    reply2 = reply2.replace("{uid}", sayer)
    reply2 = reply2.replace("{why}", reason)
    reply2 = reply2.replace("{leader}", leader)
    if reply2:
        reply2s = reply2.split('\n')
        for block in reply2s:
            if not block.strip():
                continue
            match = re.match(r'^【([^】]+)】\s*(.*)', block.strip(), re.DOTALL)
            if not match:
                continue
            ids_str, content = match.groups()
            ids = [id.strip() for id in ids_str.split(',') if id.strip()]
            processed_content = content.replace('::', '\n').replace("{say}", say).strip()
            for uid in ids:
                sendyh(processed_content, uid, 'user')
        
def _modify_black_list(parts, target, operation, group, boardreply=False):
    reply='Fail!!!'
    if len(parts) >= 3 and parts[2]:
        item = parts[2]
        try:
            if operation == "append":
                if item not in config.blackset[target]:
                    config.blackset[target].append(item)
                    reply='success'
                else:
                    reply='success(already)'
            elif operation == "remove":
                if item in config.blackset[target]:
                    config.blackset[target].remove(item)
                    reply='success'
                else:
                    reply='success(already)'
            else:
                reply='Fail!!!'
            if boardreply:
                yunhusb.setting_board(f'Operation:{operation} - {target}\nResponse:{reply}',group,'admin')
            else:
                sendyh(reply,group,'group')
        except Exception:
            traceback.print_exc()
            sendyh('Fail!!!', group, 'group')
        config.save_blackset()
        detector.load_config()
    else:
        sendyh('Fail!!!-Invalid command format', group, 'group')
        
def _modify_control_list(parts, target_list, operation, sayer):
    if len(parts.split('\n')) > 1:
        item = parts.split('\n')[1]
        if operation == "append" and item not in config.controlcenter[target_list]:
            config.controlcenter[target_list].append(item)
            sendyh(f'{target_list}+{item}', sayer, 'user')
        elif operation == "remove" and item in config.controlcenter[target_list]:
            config.controlcenter[target_list].remove(item)
            sendyh(f'{target_list}-{item}', sayer, 'user')
        else:
            sendyh(f'Fail!!!', sayer, 'user')
        config.save_controlcenter()
        detector.load_config()
        
def _delete_all_over(blackone,replygroup,group_ids=config.blackset['CTWhitegroup'],amount=100,page=3):
    msg_ids=tool.get_sender_messages_in_groups(blackone,group_ids,amount,page)
    for msg in msg_ids:
        for group_id in config.blackset['CTWhitegroup']:
            delyh(msg, group_id, "group")
            time.sleep(0.1)
    htmlreply=f'''<details><summary style="cursor: pointer; outline: none;">自动抹杀了{blackone}的{len(msg_ids)}条消息:</summary>
        <div style="padding: 10px; margin-top: 6px; border-left: 2px solid #1e90ff; color: #555;">{", ".join(str(mid) for mid in msg_ids)}</div></details>'''
    sendyh(htmlreply,replygroup,'group')

def _handle_mass_delete(say,replygroup):
    lines = [line.strip() for line in say.split('\n') if line.strip()]
    if lines:
        parts = lines[0].split()
        if len(parts) < 3 or parts[1] != "抹杀":
            sendyh('Fail!!!',replygroup,'group')
        else:
            user_id = parts[2]
            group_ids = lines[1:]
            if group_ids==[]:
                group_ids=config.blackset['CTWhitegroup']
            _delete_all_over(user_id,replygroup,group_ids)

def _generate_link_message(links):
    return '识别到链接如下：\n' + '\n'.join(links)

def normal_board(bot, say, group):
    win = True
    data={}
    if bot == '公告':
        data=setting_board(say, group, '')
    elif bot == '通知':
        data=setting_board(say, group, '')
    elif bot == '通知2':
        data=setting_board(say, group, '')
    elif bot == '群规':
        data=setting_board(say, group, '')
    elif bot == '信息公示':
        data=setting_board(say, group, '')
    elif bot == '公告2':
        data=setting_board(say, group, '')
    elif bot == 'main' or bot == 'admin':
        data=setting_board(say, group, 'admin')
    else:
        win = False
    return win,bot,data

def _N20(userxxx, group):
    config.N20_Plan[userxxx[2]]=0
    sendyh('success', group, 'group')
    config.save_N20_Plan()
    detector.load_config()

def normal(data):
    group = data["chat"]["chatId"]
    grouptype = data["chat"]["chatType"]
    sayer = data["sender"]["senderId"]
    sayernb = data['sender'].get("senderUserLevel", "")
    sayerwho = data["sender"]["senderNickname"]
    sayco = data["message"].get("content", {})
    sayMD5 = data["message"]["msgId"]
    saymode = data['message']['contentType']
    sayBYsayMD5 = data["message"].get('parentId', '')
    commandid = data["message"].get('commandId', '0')  # 默认为 '0'

    admin_commands = {
        '> 联防黑人+': lambda p: _modify_black_list(p, 'CTBlackman', "append", group),
        '> 联防黑人-': lambda p: _modify_black_list(p, 'CTBlackman', "remove", group),
        '> 联防白人+': lambda p: _modify_black_list(p, 'CTWhiteman', "append", group),
        '> 联防白人-': lambda p: _modify_black_list(p, 'CTWhiteman', "remove", group),
        '> 联防白群+': lambda p: _modify_black_list(p, 'CTWhitegroup', "append", group),
        '> 联防白群-': lambda p: _modify_black_list(p, 'CTWhitegroup', "remove", group),
        '> N20清空': lambda p: _N20(p, group),
        '> 词1+': lambda p: _modify_black_list(p, 'badad1', "append", group),
        '> 词1-': lambda p: _modify_black_list(p, 'badad1', "remove", group),
        '> 词2+': lambda p: _modify_black_list(p, 'badad2', "append", group),
        '> 词2-': lambda p: _modify_black_list(p, 'badad2', "remove", group)
    }

    if_user = grouptype in {'bot', 'user'}

    # 拦截
    if not if_user:#群内
        cansay = detector.detect_ANY(data)
        if not cansay[0]:
            _handle_deletion(group, sayco.get('text',str(sayco)), sayMD5, sayer, sayerwho ,cansay[1])
            if sayer not in config.N20_Plan:
                config.N20_Plan[sayer]=-1
            elif config.N20_Plan[sayer]<=20:
                config.N20_Plan[sayer]=-1
            else:
                pass
            return

    # 消息处理
    if saymode == 'post':
        return
    
    say = sayco.get('text','')
    
    if not if_user:#群内
        """处理用户回复逻辑"""
        groupset=config.groupset.get(group,{})
        
        if re.match(r'^(https?:\/\/)?www\.yhchat\.com\/c\/p\/(\d+)$', say):
            post_id = re.match(r'^(https?:\/\/)?www\.yhchat\.com\/c\/p\/(\d+)$', say).group(2)
            sendyh(f"<yunhu://post-detail?id={post_id}>", group, "group")

        if groupset.get('UseCTBlacklink', False):
            # --- 第一部分：处理普通消息中的链接 ---
            links = tool.extract_links(say)
            if links:
                sendyh(_generate_link_message(links), group, "group")
            if say.lower() in ["ad?", 'ad？', 'link?', 'link？']:
                print(sayco)
                links = tool.extract_links(sayco.get('parent'))
                if links:
                    sendyh(_generate_link_message(links), group, "group")
                else:
                    sendyh('未识别到链接', group, "group")
                    
        # 管理
        if sayernb in ['owner', 'administrator']:
            # 群公告
            prefixes = ('/公告', '/通知', '/群规', '/信息公示')
            if any(say.startswith(prefix) for prefix in prefixes):
                command, content = '', ''
                if '\n' in say:
                    parts = say.split('\n', 1)
                    command = parts[0][1:]
                    content = parts[1] if len(parts) > 1 else ''
                else:
                    parts = say.split(maxsplit=1)
                    command = parts[0][1:]
                    content = parts[1] if len(parts) > 1 else ''
                
                if command:
                    success,bot,response=normal_board(command, content, group)
                    if success:
                        print(response)
                        if response.get('code',1000)!=-1:
                            if content == '':
                                sendyh('#### 已对“'+bot+'”机器人下掉公告', group, "group")
                            else:
                                sendyh('#### 已对“'+bot+'”机器人设置公告：\n'+content, group, "group")
                        else:
                            sendyh('Fail!!! 请检查机器人是否在群内', group, "group")
                    else:
                        sendyh('你可能没有正确使用公告功能，设置失败', group, "group")
                else:
                    sendyh('你可能没有正确使用公告功能，设置失败', group, "group")
            elif any(word in say for word in ['公告','通知','群规','看板']):
                if config.groupset[group]['newuser']:
                    sendyh('（关闭新手模式后不再提醒）\n使用群聊管家多公告功能，请发送：/公告\n[机器人使用指南](yunhu://post-detail?id=30504) [群助手公告记录功能](https://yhfx.jwznb.com/share?key=EoIe6VoF81Da&ts=1755614434)')
        
        # 命令处理
        if say == "/帮助":
            sendyh('#### [机器人使用指南](yunhu://post-detail?id=30504)\n推荐使用[群助手helper](https://yhfx.jwznb.com/share?key=EoIe6VoF81Da&ts=1755614434)', group, "group")
        elif say == '> 看黑':# ALL权限
            sendyh(str(config.blackset['CTBlackman']), group, 'group')
        elif say == '> 看白':
            sendyh(str(config.blackset['CTWhiteman']), group, 'group')
        elif group in config.controlcenter['controlgroup']:# Only反非联
            if commandid==1920: #反非联
                blackone=say.split()[0]
                _modify_black_list(['>','拉黑',blackone], 'CTBlackman', "append", group,boardreply=True)
                _delete_all_over(blackone,group)
            elif commandid==1921:
                unblackone=say.split()[0]
                _modify_black_list(['>','解黑',unblackone], 'CTBlackman', "remove", group,boardreply=True)
            for cmd, handler in admin_commands.items():# 一系列指令
                if say.startswith(cmd):
                    handler(say.split())
                    break
            if say.startswith('> 抹杀'):
                _handle_mass_delete(say,group)
            elif say == '> 词1':
                sendyh(str(config.blackset['badad1']), group, 'group')
            elif say == '> 词2':
                sendyh(str(config.blackset['badad2']), group, 'group')
            elif say=='> 看白群':
                sendyh(str(config.blackset['CTWhitegroup']),group,'group')
            elif say == '> N20整理':
                del_count = 0
                black_count = 0
                users_to_del = [uid for uid, val in config.N20_Plan.items() if val in [0, 1, 2]]
                users_to_black = [uid for uid, val in config.N20_Plan.items() if val == -1]
                for uid in users_to_del:
                    del config.N20_Plan[uid]
                    del_count += 1
                for uid in users_to_black:
                    if uid not in config.blackset['CTBlackman']:
                        config.blackset['CTBlackman'].append(uid)
                    black_count += 1
                    del config.N20_Plan[uid]
                if del_count > 0 or black_count > 0:
                    config.save_N20_Plan()
                    config.save_blackset()
                    detector.load_config()
                sendyh(f'N20整理完成：\n清理 0/1/2 分用户: {del_count} 人\n拉黑 -1 分用户: {black_count} 人', group, 'group')
            elif say.startswith('> N20'):
                parts = say.split()
                if len(parts) == 3:
                    user_id = parts[2]
                    n20_val = config.N20_Plan.get(user_id, "未记录")
                    sendyh(f'用户 {user_id} 的N20值为: {n20_val}', group, 'group')
                else:
                    sendyh('用法: > N20 [用户ID]\n(查询指定用户的N20值)', group, 'group')

        # 智慧检测群主人功能
        if sayernb=='owner':
            if group in config.groupset:
                config.groupset[group]['leader']=sayer
            if group in config.groupset:
                if 'admin' in config.groupset[group]:
                    admins=config.groupset[group]['admin']
                    if sayer in admins:
                        admins.remove(sayer)
                    config.groupset[group]['admin']=admins
        elif sayernb=='administrator':
            if group in config.groupset:
                if 'admin' in config.groupset[group]:
                    admins=config.groupset[group]['admin']
                    if sayer not in admins:
                        admins.append(sayer)
                    config.groupset[group]['admin']=admins
                else:
                    config.groupset[group]['admin']=[sayer]
        elif sayernb=='member':
            if group in config.groupset:
                if 'admin' in config.groupset[group]:
                    admins=config.groupset[group]['admin']
                    if sayer in admins:
                        admins.remove(sayer)
                    config.groupset[group]['admin']=admins
                    
    if sayer not in config.N20_Plan:
        config.N20_Plan[sayer]=0
    elif config.N20_Plan[sayer]==-1:
        pass
    else:
        config.N20_Plan[sayer]+=1
        if sayer not in config.blackset['CTWhiteman'] and config.N20_Plan[sayer]>=20:
            config.blackset['CTWhiteman'].append(sayer)
            config.save_blackset()
            config.save_N20_Plan()
            detector.load_config()
        

@Message.Normal
def handle_normal_message(data):
    print(data)
    normal(data)

@Message.Command
def handle_command_message(data):
    print(data)
    normal(data)

@Message.BotFollowed
def handle_bot_followed(data):
    print('Message.BotFollowed===',data)
    group=data['chatId']
    user=data['userId']
    time.sleep(5)
    print(sendyh('#### 欢迎使用机器人\n[群聊管家机器人使用指南](yunhu://post-detail?id=30504)', user, "user"))

@Message.BotUnFollowed
def handle_bot_unfollowed(data):
    print('Message.BotUnFollowed===',data)

@Message.BotSettings
def handle_bot_settings(data):
    print('Message.BotSettings===', data)
    group = data["groupId"]
    setting = json.loads(data["settingJson"])

    # 提取新设置
    newuser_select=setting.get('fajiaa',{}).get("selectIndex",1)
    newuser=False
    if newuser_select==0:
        newuser=True
    
    for settle in setting:
        if setting[settle]['label'].endswith('board'):
            board=setting[settle].get('value','%drop')
        elif setting[settle]['label'].endswith('joinin'):
            joinin = setting[settle].get('value', '')
        elif setting[settle]['label'].endswith('leave'):
            leave = setting[settle].get('value', '')
        elif setting[settle]['label'].endswith('NW'):
            NBstWhite = setting[settle].get('value', '')
        elif setting[settle]['label'].endswith('UB'):
            UseCTBlackman = setting[settle].get('value', True)
        elif setting[settle]['label'].endswith('UW'):
            UseCTWords = setting[settle].get("selectStatus", [False,False,True])
            UseCTBlacklink = UseCTWords[0]
            UseCTGoodAD = UseCTWords[1]
            UseCTBadAD = UseCTWords[2]
        elif setting[settle]['label'].endswith('BW'):
            blackword = setting[settle].get('value', '')
        elif setting[settle]['label'].endswith('BM'):
            blackman = setting[settle].get('value', '')
        elif setting[settle]['label'].endswith('RE'):
            blackre = setting[settle].get('value', '')
        elif setting[settle]['label'].endswith('RE2'):
            blackre2 = setting[settle].get('value', '')
    if config.percent.search(board):
        boards = config.percent.split(board)
        boards = [b for b in boards if b]
        blen = len(boards)
        
        if blen == 0:
            sendyh('公告内容不能为空', group, "group")
        elif blen == 1:
            setting_board(board, group, 'admin')
        elif 2 <= blen <= 7:
            bot_types = ['公告', '通知', '公告2', '通知2', '群规', '信息公示']
            err_bot=[]
            for i in range(len(bot_types)):
                if i < len(boards) and boards[i]:
                    board_=boards[i].strip()
                    if board_=='%drop':
                        board_='' #%drop=下公告
                else:
                    board_=''
                if i==0:
                    response=setting_board(board_, group, 'admin')
                    bot='main'
                else:
                    _,bot,response=normal_board(bot_types[i-1], board_, group)
                if response.get('code',1000)==-1:
                    err_bot.append({'bot':bot,'board':board_})
            print(err_bot)
            if err_bot:
                if len(err_bot)==0:
                    sendyh(f'公告一键设置成功', group, "group")
                else:
                    buttonvalue=json.dumps(err_bot)
                    reply={
                        'text':f'Fail!!! 发生{len(err_bot)}次错误，请检查机器人入群情况\n[群聊管家机器人使用指南](yunhu://post-detail?id=30504)',
                        "buttons":[[{"text":"retry","actionType":3,"value":'board'+buttonvalue}]]
                    }
                    yunhuse.send_button(reply,group,'group')
        else:
            sendyh('你是如何做到需要如此多的公告的，你们群一定很抽象(上限7)', group, "group")
    else:
        if board=='%drop':
            board=''
        setting_board(board, group, 'admin')

    leader=config.groupset.get(group, {}).get('leader', [])
    admin=config.groupset.get(group, {}).get('admin', '')

    if newuser:
        if not UseCTBlackman:
            sendyh('新手模式提醒：注意到群关闭了联防，这会导致群不安全。请保持联防开启。想给一些人网开一面，请使用群白名单功能。',group,'group')
        if group in config.groupset:
            old_information = {
                '公告内容': config.groupset[group].get('board', ''),
                '进群欢迎': config.groupset[group].get('joinin', ''),
                '退群提醒': config.groupset[group].get('leave', '')
            }
            oldseetings = json.dumps(old_information, ensure_ascii=False, indent=4)
            sendyh(
                '群'+group+'的设置被修改了，以下是旧设置，供备份\n```text\n- --' + str(oldseetings[6:-2]) +
                '\n```\n若不想接受此提醒，请在机器人设置中关闭“新手模式”（不推荐关闭，到时候功能不会用又跑去用隔壁机器人）',
                leader, 'user'
            )
    
    # 更新配置
    config.groupset[group] = {
        'newuser': newuser,
        'board': board,
        "joinin": joinin,
        "leave": leave,
        'NBstWhite': NBstWhite,
        'UseCTBlackman': UseCTBlackman,
        'UseCTBlacklink': UseCTBlacklink,
        'UseCTGoodAD': UseCTGoodAD,
        'UseCTBadAD': UseCTBadAD,
        'blackman': blackman,
        'blackword': blackword,
        'blackre': blackre,
        'blackre2': blackre2,
        'leader':leader,
        'admin':admin
    }

    config.storage.update_group(group, config.groupset[group])
    detector.load_config()

@Message.GroupJoin
def handle_group_join(data):
    print("Message.GroupJoin===", data)
    who = data["nickname"]
    uid = data["userId"]
    group = data["chatId"]
    url = data['avatarUrl']
    if group in config.groupset:
        joinsay = config.groupset[group].get("joinin", '')
        if joinsay != '':
            if config.percent.search(joinsay):
                replys = config.percent.split(joinsay)
                replys = [reply for reply in replys if reply]
                joinsay = random.choice(replys)
            joinsay = joinsay.replace("{name}", who)
            joinsay = joinsay.replace("{uid}", uid)
            joinsay = joinsay.replace("{id}", uid)
            joinsay = joinsay.replace("{url}", url)
            sendyh(joinsay.strip(), group, "group")
    else:
        sendyh('欢迎', group, "group")

@Message.GroupLeave
def handle_group_leave(data):
    print("Message.GroupLeave===", data)
    who = data["nickname"]
    uid = data["userId"]
    group = data["chatId"]
    url = data['avatarUrl']
    if group in config.groupset:
        leavesay = config.groupset[group].get("leave", '')
        if leavesay != '':
            if config.percent.search(leavesay):
                replys = config.percent.split(leavesay)
                replys = [reply for reply in replys if reply]
                leavesay = random.choice(replys)
            leavesay = leavesay.replace("{name}", who)
            leavesay = leavesay.replace("{uid}", uid)
            leavesay = leavesay.replace("{id}", uid)
            leavesay = leavesay.replace("{url}", url)
            sendyh(leavesay.strip(), group, "group")

@Message.ButtonReportInline
def handle_button(data):
    print("Message.ButtonReportInline===", data)
    referer=data['event']['msgId']
    getby=data['event']['userId']
    getin=data['event']['recvId']
    getmode=data['event']['recvType']
    value=data['event']['value']
    group=getin
    if getmode=='group':
        if value.startswith('board'):
            say=value[5:]
            boarddata=json.loads(say)
            for board in boarddata:
                bot=board['bot']
                board_=board['board']
                normal_board(bot, board_, group)
            yunhuse.change_message(referer,getin,'group','text','已重试，请检查是否成功')

if __name__ == "__main__":
    if 'CTWhitegroup' not in config.blackset:
        config.blackset['CTWhitegroup']=[]
        config.save_blackset()
        detector.load_config()
    Start(host="0.0.0.0", port=8501, debug=True)