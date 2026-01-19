from typing import Dict, List, Tuple, Set, Any, Optional
import sqlite3
import json

class SQLiteStorage:
    def __init__(self, db_path="config.db"):
        self.db_path = db_path
        self.init_db()
        self.migrate_from_json()
    
    def init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 1. 群设置表 (groupset) - 单独表
        c.execute('''
            CREATE TABLE IF NOT EXISTS groupset (
                group_id TEXT PRIMARY KEY,
                settings TEXT NOT NULL
            )
        ''')
        
        # 2. 用户设置表 (userset) - 单独表
        c.execute('''
            CREATE TABLE IF NOT EXISTS userset (
                user_id TEXT PRIMARY KEY,
                settings TEXT NOT NULL
            )
        ''')
        
        # 3. 统一配置表 (configs) - 存储其他所有配置
        c.execute('''
            CREATE TABLE IF NOT EXISTS configs (
                config_type TEXT PRIMARY KEY,
                config_data TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def migrate_from_json(self):
        """从JSON文件迁移数据到数据库"""
        json_files = {
            'groupset': 'groupset.json',
            'userset': 'userset.json',
            'blackset': 'zblackset.json',
            'Duddle': 'zduddle.json',
            'controlcenter': 'zcontrolcenter.json',
            'N20_Plan': 'zN20.json'
        }
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 检查是否已经有数据
        c.execute("SELECT COUNT(*) FROM configs WHERE config_type = 'blackset'")
        if c.fetchone()[0] == 0:  # 没有数据，需要迁移
            print("检测到新数据库，开始从JSON文件迁移数据...")
            
            for config_type, filename in json_files.items():
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 特殊处理groupset
                        if config_type == 'groupset':
                            for group_id, settings in data.items():
                                c.execute(
                                    "INSERT OR REPLACE INTO groupset VALUES (?, ?)",
                                    (group_id, json.dumps(settings, ensure_ascii=False))
                                )
                        elif config_type == 'userset':
                            for user_id,settings in data.items():
                                c.execute(
                                    "INSERT OR REPLACE INTO userset VALUES (?, ?)",
                                    (user_id, json.dumps(settings, ensure_ascii=False))
                                )
                        else:
                            c.execute(
                                "INSERT OR REPLACE INTO configs VALUES (?, ?)",
                                (config_type, json.dumps(data, ensure_ascii=False))
                            )
                    print(f"  ✓ 已迁移 {filename}")
                except Exception as e:
                    print(f"  ✗ 迁移 {filename} 失败: {e}")
            
            conn.commit()
            print("数据迁移完成！")
        conn.close()
    
    # === 群设置操作 ===
    def load_groupset(self) -> Dict[str, Any]:
        """加载所有群设置"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT group_id, settings FROM groupset")
        rows = c.fetchall()
        conn.close()
        
        groupset = {}
        for group_id, settings_json in rows:
            groupset[group_id] = json.loads(settings_json)
        return groupset
    
    def save_groupset(self, groupset: Dict[str, Any]):
        """保存群设置"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 清空表
        c.execute("DELETE FROM groupset")
        
        # 插入新数据
        for group_id, settings in groupset.items():
            c.execute(
                "INSERT INTO groupset VALUES (?, ?)",
                (group_id, json.dumps(settings, ensure_ascii=False))
            )
        
        conn.commit()
        conn.close()
    
    def update_group(self, group_id: str, settings: Dict[str, Any]):
        """更新单个群设置"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO groupset VALUES (?, ?)",
            (group_id, json.dumps(settings, ensure_ascii=False))
        )
        conn.commit()
        conn.close()
    
    def delete_group(self, group_id: str):
        """删除群设置"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM groupset WHERE group_id = ?", (group_id,))
        conn.commit()
        conn.close()
    
    # === 用户设置操作 ===
    def load_userset(self) -> Dict[str, Any]:
        """加载用户设置"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT user_id, settings FROM userset")
        rows = c.fetchall()
        conn.close()
        
        userset = {}
        for user_id, settings_json in rows:
            userset[user_id] = json.loads(settings_json)
        return userset
    
    def save_userset(self, userset: Dict[str, Any]):
        """保存用户设置"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("DELETE FROM userset")
        for user_id, settings in userset.items():
            c.execute(
                "INSERT INTO userset VALUES (?, ?)",
                (user_id, json.dumps(settings, ensure_ascii=False))
            )
        
        conn.commit()
        conn.close()
    
    # === 统一配置操作 ===
    def load_config(self, config_type: str) -> Dict[str, Any]:
        """加载指定类型的配置"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT config_data FROM configs WHERE config_type = ?", (config_type,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return {}
    
    def save_config(self, config_type: str, data: Dict[str, Any]):
        """保存指定类型的配置"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO configs VALUES (?, ?)",
            (config_type, json.dumps(data, ensure_ascii=False))
        )
        conn.commit()
        conn.close()
    
    # === 开发者工具 ===
    def delete_n20_values(self, values: List[int]):
        """删除指定N20值的记录"""
        n20_data = self.load_config('N20_Plan')
        users_to_delete = [
            user_id for user_id, value in n20_data.items()
            if value in values
        ]
        for user_id in users_to_delete:
            del n20_data[user_id]
        self.save_config('N20_Plan', n20_data)
        return len(users_to_delete)
    
    def get_n20_negative_users(self) -> List[str]:
        """获取N20为-1的用户"""
        n20_data = self.load_config('N20_Plan')
        return [user_id for user_id, value in n20_data.items() if value == -1]
