import json
import requests
from RyhBotPythonSDK import Server
import re
import random

import env
import yunhuse
import tool




sendyh=yunhuse.sendyh
setting_board=yunhuse.setting_board
bysendyh=yunhuse.bysendyh
with open("groupset.json", "r", encoding="utf-8") as f:
    groupset = json.load(f)
with open("userset.json", "r", encoding="utf-8") as f:
    userset = json.load(f)



def setting_default(group,groupset):
    groupset[group]={
        "joinin":"欢迎",
        "leave":"有人退群了"
    }
    return groupset

def joinin(data):
    global groupset
    if True:
    # try:
        who=data["nickname"]
        id=data["userId"]
        group=data["chatId"]
        url=data['avatarUrl']
        if not group in groupset:
            groupset=setting_default(group,groupset)
        joinsay=groupset[group]["joinin"]
        if joinsay!='':
            if "%%%%%%%" in joinsay:
                replys=joinsay.split('\n%%%%%%%\n')
                joinsay=random.choice(replys)
            if "{name}" in joinsay:
                joinsay=joinsay.format(name=who)
            if "{id}" in joinsay:
                joinsay=joinsay.format(id=id)
            if "{url}" in joinsay:
                joinsay=joinsay.format(url=url)
            sendyh(joinsay,group,"group")
    # except:
    #     pass
        
def leave(data):
    global groupset
    if True:
    # try:
        who=data["nickname"]
        id=data["userId"]
        group=data["chatId"]
        url=data['avatarUrl']
        if not group in groupset:
            setting_default(group,groupset)
        joinsay=groupset[group]["leave"]
        if joinsay!='':
            if "%%%%%%%" in joinsay:
                replys=joinsay.split('\n%%%%%%%\n')
                joinsay=random.choice(replys)
            if "{name}" in joinsay:
                joinsay=joinsay.format(name=who)
            if "{id}" in joinsay:
                joinsay=joinsay.format(id=id)
            if "{url}" in joinsay:
                joinsay=joinsay.format(url=url)
            sendyh(joinsay,group,"group")
    # except:
    #     pass   
    
def groupsetting(data):
    global groupset
    if True:
    # try:
        group=data["groupId"]
        setting=json.loads(data["settingJson"])
        
        board=setting["fzbysd"]["value"]
        joinin=setting["gjrtxb"]["value"]
        leave=setting["kiuwfu"]["value"]
        blackman=setting['nkjvgk']["value"]
        blackword=setting['lsxega']['value']
        blackre=setting['iaqjev']['value']
        
        setting_board(board,group,'admin')

        groupset[group]={
            'board':board,
            "joinin":joinin,
            "leave":leave,
            'blackman':blackman,
            'blackword':blackword,
            'blackre':blackre
        }
        
    # except:
    #     pass
    with open("groupset.json", "w", encoding="utf-8") as f:
        json.dump(groupset, f, ensure_ascii=False, indent=4)


#功能：设置其他机器人的群公告
def normal_board(bot,say,group):
    win=True
    if bot=='公告':
        setting_board(say,group,'453565c0344a43d5894e6a8ff3e6fc74')
    elif bot=='通知':
        setting_board(say,group,'cf9febf112b04c6aad6beaacff07bf26')
    else:
        win=False
        sendyh('出错啦',group,"group")
    if win:
        if say=='':
            sendyh('#### 已对“'+bot+'”机器人下掉公告',group,"group")
        else:
            sendyh('#### 已对“'+bot+'”机器人设置公告：\n'+say,group,"group")

def normal(data):
    global groupset
    global userset
    if True:
    # try:
        group=data["chat"]["chatId"]
        grouptype=data["chat"]["chatType"]

        sayer=data["sender"]["senderId"]
        sayernb=data['sender']["senderUserLevel"]
        sayerwho=data["sender"]["senderNickname"]

        sayco=data["message"]['content']
        sayMD5=data["message"]["msgId"]

        sayBYsayMD5=data["message"]['parentId']

        if "text" in sayco:
            say=sayco["text"]
            if_user=grouptype=='bot' or grouptype=='user'
            if if_user:
                # owner
                if sayernb=='owner':
                    if say=='* data':
                        replyddd='groupset:\n```\n'+str(groupset)+'\n```\nuserset:\n```\n'+str(userset)+'\n```'
                        sendyh(replyddd,sayer,'user')
            
            cansay=True
            # 群聊发言合理性检验
            if group in groupset:
                if 'blackman' in groupset[group] and 'blackword' in groupset[group]:
                    blackman_=groupset[group]['blackman']
                    if blackman_!='':
                        blackmans=blackman_.split()
                        for blackman in blackmans:
                            if sayer==blackman:
                                cansay=False
                                break
                    
                    blackword_=groupset[group]['blackword']
                    if blackword_!='':
                        blackwords=blackword_.split()
                        
                        for blackword in blackwords:
                            zzbds=False
                            rewords='[.\\$({+^*?'
                            for reword in rewords:
                                if reword in blackword:
                                    zzbds=True
                                    break
                            if zzbds:
                                if re.search(blackword, say):
                                    cansay=False
                                    break
                            else:
                                if blackword in say:
                                    cansay=False
                                    break
            else:
                setting_default(group,groupset)
            
            print('cansay',cansay)
            if not cansay:
                yunhuse.delete_say(sayMD5,group,"group")
                if group in groupset:
                    if 'blackre' in groupset[group]:
                        if groupset[group]['blackre']!='':
                            sendyh(groupset[group]['blackre'],group,'group')
            else:
                job=False
                #功能：设置群公告
                if sayernb=='owner' or sayernb=='administrator':
                    if say.startswith('*公告'):
                        job=True
                        says=say.split('\n')

                        board=''
                        i=0
                        for say_board in says:
                            if i==0:
                                pass
                            elif i==1:
                                board=say_board
                            else:
                                board=board+'\n'+say_board
                            i=i+1
                            
                        if len(says[0])==3:
                            setting_board(board,group,'admin')
                            if board=='':
                                sendyh('#### 取消公告成功',group,"group")
                            else:
                                sendyh('#### 设置公告成功：\n'+board,group,"group")
                        else:
                            if ' ' in says[0]:
                                sayss=says[0].split()
                                normal_board(sayss[1],board,group)
                            else:
                                bot=says[0][3:]
                                normal_board(bot,board,group)
                    elif say.startswith('* 公告'):
                        job=True
                        says=say.split('\n')

                        board=''
                        i=0
                        for say_board in says:
                            if i==0:
                                pass
                            elif i==1:
                                board=say_board
                            else:
                                board=board+'\n'+say_board
                            i=i+1
                            
                        sayss=says[0].split()
                        if len(sayss)==3:
                            normal_board(sayss[2],board,group)
                        elif len(sayss)==2:
                            if len(sayss[1])==2:
                                setting_board(board,group,'admin')
                                if board=='':
                                    sendyh('#### 取消公告成功',group,"group")
                                else:
                                    sendyh('#### 设置公告成功：\n'+board,group,"group")
                            else:
                                bot=sayss[1][2:]
                                normal_board(bot,board,group)                      
                        else:
                            pass
                    else:
                        pass
                print('job',job)
                # 智能发送
                if sayer in userset and not job:
                    userset_=userset[sayer]
                    if userset_['open']:
                        use=False
                        if userset_['detect']=='两空格':
                            if say.endswith("  "):
                                use=True
                                say=say[:-2]
                        elif userset_['detect']=='所有':
                            use=True
                        if use:
                            if userset_['delete']:
                                yunhuse.delete_say(sayMD5,group,"group")
                            sendname=''
                            sendid=''
                            if userset_["name"]:
                                sendname=sayerwho
                            if userset_["id"]:
                                sendid="("+sayer+")"
                            planB=(sendname=='') and (sendid=='')
                            reply=''
                            if userset_['skin3']=='默认皮肤':
                                reply=sendname+sendid+'：\n'+say
                                if planB:
                                    reply=say
                            elif userset_['skin3']=='云湖应援色':
                                reply='<p style="color:#9b43f9;">'+sendname+sendid+'：</p>\n'+say
                                if planB:
                                    reply=say
                            else:
                                reply='功能未启用，请在个人设置中重新设置'
                            
                            # 检查引用
                            if sayBYsayMD5=='':
                                sendyh(reply,group,"group")
                            else:
                                bysendyh(reply,group,'group',sayBYsayMD5)
        # except:
        #     none

'''（try，except）    
if sendname=="" and sendid=="":
    if userset_["skin3"]=="默认皮肤":
        reply=say
    elif userset_["skin3"]=="云湖应援色":
        say2=check(say)# 放到tool里检测是否为markdown，如果是，转html
        say3=html_color(say2,"#9b43f9","1")# 转颜色/大小
        reply=say3
    else:
        skin0=userset_["skin"]
        skins=skin0.split('\n-----\n')
        skin1=skin[1]
        skin1s=skin1.split("\n\n")
        skin2=skin1s[len(skin1s)-1]
        if skin2!=",":
            skin2s=skin2.split(",")
            msg=html_color(check(say),skin2s[0],skin2s[1])
        elif skin2.startswith(","):
            size=skin2[1:]
            msg=html_color(check(say),'',size)
        elif skin2.endswith(","):
            color=skin2[:-1]
            msg=html_color(check(say),color,'')
            
else:
    if userset_["skin3"]=="默认皮肤":
        msg=say
        skin="{name}{id}：\n{msg}"
        # 替换
    elif userset_["skin3"]=="云湖应援色":
        msg=html_color(check(say),"#9b43f9","1")
        skin='<p style="color:#9b43f9;">{name}{id}：</p>\n{msg}'
        # 替换
    else:
        skin0=userset_["skin"]
        skins=skin0.split('\n-----\n')
        skin1=skin[0]
        # 替换
'''



def command(data):
    global groupset
    global userset
    if True:
    # try:
        group=data["chat"]["chatId"]
        grouptype=data["chat"]["chatType"]
        sayer=data["sender"]["senderId"]
        sayernb=data['sender']["senderUserLevel"]
        sayco=data["message"]['content']
        commandid=data["message"]['commandId']
        sayMD5=data["message"]["msgId"]

        # 个人设置
        # 启用发送优化功能：zznwrd
        # 触发条件：bqwusq
        # 撤回再发送：rpvxww
        # 显示昵称：jehnve
        # 显示id：ajrmjo
        # 发送气泡：neaxtb
        # 自定义皮肤：owufaw
        if commandid==1088:
            if grouptype=='bot':
                list=['zznwrd','bqwusq','rpvxww','jehnve','ajrmjo','neaxtb','owufaw']
                ifinsayco=True
                for i1088 in list:
                    if not i1088 in sayco['formJson']:
                        ifinsayco=False
                if ifinsayco:
                    set1=sayco['formJson']['zznwrd']["value"]
                    set2=sayco['formJson']['bqwusq']["selectValue"]
                    set3=sayco['formJson']['rpvxww']["value"]
                    set4=sayco['formJson']['jehnve']["value"]
                    set5=sayco['formJson']['ajrmjo']["value"]
                    set6=sayco['formJson']['neaxtb']["selectValue"]
                    set7=sayco['formJson']['owufaw']["value"]
                    userset[sayer]={
                        'open':set1,
                        'detect':set2,
                        "delete":set3,
                        "name":set4,
                        "id":set5,
                        "skin3":set6,
                        "skin":set7
                    }
                    a=sendyh('设置完毕\n```\n'+str(userset[sayer])+'\n```\n（如果设置出错，请留存该日志）',sayer,"user")
                    print(a)
            else:
                sendyh('#### 机器人使用指南\n[群聊管家机器人使用指南](yunhu://post-detail?id=1132)\n**`注：个人设置请私信机器人，群内设置无效`**',group,"group")
        
        if "text" in sayco:
            say=sayco["text"]
            cansay=True
            # 群聊发言合理性检验
            if group in groupset:
                if 'blackman' in groupset[group] and 'blackword' in groupset[group]:
                    blackman_=groupset[group]['blackman']
                    if blackman_!='':
                        blackmans=blackman_.split()
                        for blackman in blackmans:
                            if sayer==blackman:
                                cansay=False
                                break
                    
                    blackword_=groupset[group]['blackword']
                    if blackword_!='':
                        blackwords=blackword_.split()
                        
                        for blackword in blackwords:
                            zzbds=False
                            rewords='[.\\$({+^*?'
                            for reword in rewords:
                                if reword in blackword:
                                    zzbds=True
                                    break
                            if zzbds:
                                if re.search(blackword, say):
                                    cansay=False
                                    break
                            else:
                                if blackword in say:
                                    cansay=False
                                    break
            else:
                setting_default(group,groupset)
            
            print('cansay',cansay)
            if not cansay:
                yunhuse.delete_say(sayMD5,group,"group")
                if group in groupset:
                    if 'blackre' in groupset[group]:
                        if groupset[group]['blackre']!='':
                            sendyh(groupset[group]['blackre'],group,'group')
    with open("userset.json", "w", encoding="utf-8") as f:
        json.dump(userset, f, ensure_ascii=False, indent=4)





@Server.Message.Normal
def handle_normal_message(data):
    print(data)
    normal(data)

@Server.Message.Command
def handle_command_message(data):
    print(data)
    command(data)

@Server.Message.BotFollowed
def handle_bot_followed(data):
    print(data)

@Server.Message.BotUnFollowed
def handle_bot_unfollowed(data):
    print(data)

@Server.Message.BotSettings
def handle_bot_settings(data):
    groupsetting(data)

@Server.Message.GroupJoin
def handle_group_join(data):
    print("Group joined:", data)
    joinin(data)

@Server.Message.GroupLeave
def handle_group_leave(data):
    print("Group left:", data)
    leave(data)

if __name__ == "__main__":
    Server.Start(host="0.0.0.0", port=8501, debug=True)