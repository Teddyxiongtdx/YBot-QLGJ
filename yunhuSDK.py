from flask import Flask, request, jsonify
import json

app = Flask(__name__)

NormalFuncList = []
CommandFuncList = []
BotFollowedFuncList = []
BotUnFollowedFuncList = []
GroupJoinFuncList = []
GroupLeaveFuncList = []
SettingsFuncList = []
ButtonReportInlineFuncList = []
APIFunList = []

class Message:
    class Normal:
        def __init__(self, func):
            global NormalFuncList
            self.func = func
            NormalFuncList.append(func)
        
        def __call__(self, *args, **kwargs):
            rv = self.func(*args, **kwargs)
            return rv
    
    class Command:
        def __init__(self, func):
            global CommandFuncList
            self.func = func
            CommandFuncList.append(func)
        
        def __call__(self, *args, **kwargs):
            rv = self.func(*args, **kwargs)
            return rv
    
    class BotFollowed:
        def __init__(self, func):
            global BotFollowedFuncList
            self.func = func
            BotFollowedFuncList.append(func)
        
        def __call__(self, *args, **kwargs):
            rv = self.func(*args, **kwargs)
            return rv
    
    class BotUnFollowed:
        def __init__(self, func):
            global BotUnFollowedFuncList
            self.func = func
            BotUnFollowedFuncList.append(func)
        
        def __call__(self, *args, **kwargs):
            rv = self.func(*args, **kwargs)
            return rv
    
    class BotSettings:
        def __init__(self, func):
            global SettingsFuncList
            self.func = func
            SettingsFuncList.append(func)
        
        def __call__(self, *args, **kwargs):
            rv = self.func(*args, **kwargs)
            return rv
    
    class GroupJoin:
        def __init__(self, func):
            global GroupJoinFuncList
            self.func = func
            GroupJoinFuncList.append(func)
        
        def __call__(self, *args, **kwargs):
            rv = self.func(*args, **kwargs)
            return rv
    
    class GroupLeave:
        def __init__(self, func):
            global GroupLeaveFuncList
            self.func = func
            GroupLeaveFuncList.append(func)
        
        def __call__(self, *args, **kwargs):
            rv = self.func(*args, **kwargs)
            return rv
    
    class ButtonReportInline:
        def __init__(self, func):
            global ButtonReportInlineFuncList
            self.func = func
            ButtonReportInlineFuncList.append(func)
        
        def __call__(self, *args, **kwargs):
            rv = self.func(*args, **kwargs)
            return rv
        
    class API:
        def __init__(self, func):
            global APIFunList
            self.func = func
            APIFunList.append(func)
        
        def __call__(self, *args, **kwargs):
            rv = self.func(*args, **kwargs)
            return rv

@app.route('/', methods=['POST'])
def RecvMsg():
    data = request.json
    event_type = data['header']['eventType']
    
    if event_type == "message.receive.normal":
        for func in NormalFuncList:
            func(data=data['event'])
    elif event_type == "message.receive.instruction":
        for func in CommandFuncList:
            func(data=data['event'])
    elif event_type == "bot.followed":
        for func in BotFollowedFuncList:
            func(data=data['event'])
    elif event_type == "bot.unfollowed":
        for func in BotUnFollowedFuncList:
            func(data=data['event'])
    elif event_type == "bot.setting":
        for func in SettingsFuncList:
            func(data=data['event'])
    elif event_type == "group.join":
        for func in GroupJoinFuncList:
            func(data=data['event'])
    elif event_type == "group.leave":
        for func in GroupLeaveFuncList:
            func(data=data['event'])
    elif event_type == "button.report.inline":
        for func in ButtonReportInlineFuncList:
            func(data=data)
    elif event_type == "in.api.v1":
        for func in APIFunList:
            return func(data=data)
    
    with open("RecvMsg.json", "w", encoding="utf-8") as RecvMsg:
        json.dump(data, RecvMsg, ensure_ascii=False, indent=4)
    return jsonify(data)

def Start(host:str, port:int, debug:bool=False):
    app.run(
        host=host,
        port=port,
        debug=debug
    )