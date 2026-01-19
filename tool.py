import json
import requests
import env
import yunhuse
import re

def extract_links(say):
    # 定义正则表达式模式
    markdown_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    href_pattern = r'href=["\']([^"\']+)["\']'
    data_url_pattern = r'data-url=["\']([^"\']+)["\']'
    
    # 查找所有匹配的链接
    markdown_links = re.findall(markdown_link_pattern, say)
    href_links = re.findall(href_pattern, say)
    data_url_links = re.findall(data_url_pattern, say)
    
    # 提取链接部分（去掉链接文本）
    all_links = []
    all_links.extend([link[1] for link in markdown_links])  # 提取[]()中的链接
    all_links.extend(href_links)
    all_links.extend(data_url_links)
    return all_links


def is_abnormal_word(s):
    """判断单个单词是否为异常格式"""
    # 条件1：出现连续的英文字母、数字、指定符号
    pattern1 = r'^[a-zA-Z0-9_\-#￥%&*!@#$^%&*/()]+$'
    if re.fullmatch(pattern1, s):
        return True

    # 条件2：纯英文且无数字
    if s.isalpha():
        uppercase_indices = [i for i, c in enumerate(s) if c.isupper()]
        if len(uppercase_indices) < 2:
            return False
        first = uppercase_indices[0]
        expected = [first + i for i in range(len(uppercase_indices))]
        return uppercase_indices != expected


def is_abnormal_text(text):
    words = text.split()
    for word in words:
        if is_abnormal_word(word):
            return True
    return False

def checkword(text):
    with open("zblackset.json", "r", encoding="utf-8") as f:
        blackset = json.load(f)
    if is_abnormal_text(text):
        return False
        

def replace(text, old, new):
    parts = text.rsplit(old, 1)  # 从右边开始拆分，最多拆一次
    if len(parts) == 1:
        return text  # 没找到 old，不替换
    else:
        return new.join(parts)

def get_sender_messages_in_groups(sender_id, group_ids, message_count=20,page=1):
    collected_msg_ids = []
    # 确保group_ids是列表格式
    if isinstance(group_ids, str):
        group_ids = [group_ids]

    for group_id in group_ids:
        last_msg_id=None
        for i in range(page):
            messages = yunhuse.yunhulist(group_id, before=message_count,message_id=last_msg_id)
            try:
                current_msg_id = messages[-1].get("msgId")#(-1是最老的消息)
            except Exception:
                break
            for msg in messages:
                msg_id = msg.get("msgId")
                if msg.get("senderId") == sender_id:
                    collected_msg_ids.append(msg_id)
            if last_msg_id == current_msg_id:
                break
            last_msg_id = current_msg_id

    return collected_msg_ids

def get_sender_messages_in_group(group_id, sender_id=None, start_message_id=None, message_count=100):
    collected_msg_ids = []

    if message_count>100:
        message_count=100
    
    messages = yunhuse.yunhulist(group_id=group_id,message_id=start_message_id,before=message_count)
    
    # 筛选消息
    for msg in messages:
        if sender_id is not None:# 如果指定了sender_id，则只匹配该发送者
            if msg.get("senderId") == sender_id:
                if msg_id := msg.get("msgId"):
                    collected_msg_ids.append(msg_id)
        else:# 未指定sender_id时返回所有消息
            if msg_id := msg.get("msgId"):
                collected_msg_ids.append(msg_id)
    
    return collected_msg_ids

def get_bot_messages_after(group_id, message_id, count=5):
    # 获取指定消息之后count条消息
    messages = yunhuse.yunhulist(group_id,message_id=message_id,after=count)
    
    bot_msg_ids = []
    exclude_bot_ids = ["30858771","78248353","76965303","39032934"]

    for msg in messages:
        if msg.get("senderType") == "bot" and (msg.get("senderId") not in exclude_bot_ids):
            if msg_id := msg.get("msgId"):
                bot_msg_ids.append(msg_id)

    return bot_msg_ids