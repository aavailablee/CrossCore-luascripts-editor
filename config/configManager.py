import json
import os
from pathlib import Path

# 获取当前脚本所在的文件夹路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
config_path = Path(os.path.join(current_dir, "config.json"))


def loadConfig():
    """读取配置"""
    if not config_path.exists():
        with open(config_path, "w", encoding="utf-8") as tmp:
            json.dump({}, tmp)
    with open(config_path, "r", encoding="utf-8") as json_file:
        config = json.load(json_file)
    return config


class ConfigManager:
    _instance = None  # 私有类变量用于存储单例实例

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.config = loadConfig()  # 加载配置
        return cls._instance

    def loadConfig(self):
        """读取配置"""
        with open(config_path, "r", encoding="utf-8") as json_file:
            config = json.load(json_file)
        return config

    def updateConfig(self, new_config):
        """更新配置，合并新配置与已有配置"""
        current_config = self.loadConfig()  # 读取当前配置
        current_config.update(new_config)  # 合并新配置
        with open(config_path, 'w', encoding="utf-8") as json_file:
            json.dump(current_config, json_file, indent=4, ensure_ascii=False)  # 处理中文字符

    def get(self, key, default=None):
        """获取配置中的值，找不到时返回默认值"""
        if key not in self.config:
            self.config[key] = default  # 将默认值存入配置
            self.updateConfig(self.config)  # 更新配置文件
        return self.config.get(key, default)


# 示例用法
if __name__ == "__main__":
    config_manager = ConfigManager()
    # 使用 get 方法获取配置

    # 更新配置示例，传入新配置字典
    new_config = {}  # 在这里可以动态生成或从其他地方获取配置
    # 例如，动态添加配置
    new_key = "some_key"
    new_value = "new_value1"  # 这里可以从其他来源获得
    new_config[new_key] = new_value

    # self.updateConfig(new_config)
