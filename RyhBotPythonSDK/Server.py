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

class Message:
    class Normal:
        def __init__(self, func) -> None:
            global NormalFuncList
            self.func=func
            NormalFuncList.append(func)
        def __call__(self, *args, **kwds):
            rv=self.func(*args,**kwds)
            return rv
    class Command:
        def __init__(self, func) -> None:
            global CommandFuncList
            self.func=func
            CommandFuncList.append(func)
        def __call__(self, *args, **kwds):
            rv=self.func(*args,**kwds)
            return rv
    class BotFollowed:
        def __init__(self, func) -> None:
            global BotFollowedFuncList
            self.func=func
            BotFollowedFuncList.append(func)
        def __call__(self, *args, **kwds):
            rv=self.func(*args,**kwds)
            return rv
    class BotUnFollowed:
        def __init__(self, func) -> None:
            global BotUnFollowedFuncList
            self.func=func
            BotUnFollowedFuncList.append(func)
        def __call__(self, *args, **kwds):
            rv=self.func(*args,**kwds)
            return rv
    class BotSettings:
        def __init__(self, func) -> None:
            global SettingsFuncList
            self.func=func
            SettingsFuncList.append(func)
        def __call__(self, *args, **kwds):
            rv=self.func(*args,**kwds)
            return rv
    class GroupJoin:
        def __init__(self, func) -> None:
            global GroupJoinFuncList
            self.func=func
            GroupJoinFuncList.append(func)
        def __call__(self, *args, **kwds):
            rv=self.func(*args,**kwds)
            return rv
    class GroupLeave:
        def __init__(self, func) -> None:
            global GroupLeaveFuncList
            self.func=func
            GroupLeaveFuncList.append(func)
        def __call__(self, *args, **kwds):
            rv=self.func(*args,**kwds)
            return rv

@app.route('/', methods=['POST'])
def RecvMsg():
    data = request.json
    if data['header']['eventType'] == "message.receive.normal":
        for func in NormalFuncList:
            func(data=data['event'])
    if data['header']['eventType'] == "message.receive.instruction":
        for func in CommandFuncList:
            func(data=data['event'])
    if data['header']['eventType'] == "bot.followed":
        for func in BotFollowedFuncList:
            func(data=data['event'])
    if data['header']['eventType'] == "bot.unfollowed":
        for func in BotUnFollowedFuncList:
            func(data=data['event'])
    if data['header']['eventType'] == "bot.setting":
        for func in SettingsFuncList:
            func(data=data['event'])
    if data['header']['eventType'] == "group.join":
        for func in GroupJoinFuncList:
            func(data=data['event'])
    if data['header']['eventType'] == "group.leave":
        for func in GroupLeaveFuncList:
            func(data=data['event'])

    with open("RecvMsg.json", "w", encoding="utf-8") as RecvMsg:
        json.dump(data, RecvMsg, ensure_ascii=False, indent=4)
    return jsonify(data)

def Start(host:str, port:int, debug:bool=False):
    app.run(
        host=host,
        port=port,
        debug=debug
    )