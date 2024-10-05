import os
import json
import re

import UnityPy
from lupa import LuaRuntime
import pandas as pd
from config.configManager import ConfigManager

class ExtractScript:
    def __init__(self):
        """初始化 Lua 环境并加载配置"""
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.cfg_manager = ConfigManager()

    def extract_lua_data(self, text_asset):
        """从 TextAsset 中提取 Lua 数据并直接存储配置信息"""
        lua_content = text_asset.m_Script

        # 提取 header 信息（包含 filename, sheetname, types 和 names）
        header_pattern = r'local conf = \{[\s\S]*?\["data"\] = {'
        header_match = re.search(header_pattern, lua_content, re.DOTALL)
        header = header_match.group(0)
        if not header_match:
            print("Warning: Could not find header in Lua content")
            return [], []

        # 提取 footer
        footer_pattern = r'},\s*}\s*--\w+\s*=\s*conf\s*return conf'
        footer_match = re.search(footer_pattern, lua_content, re.DOTALL)
        footer = footer_match.group(0)

        # 提取 types 和 names
        # types_match = re.search(r'\["types"\]\s*=\s*\{([^\}]+)\}', header)
        names_match = re.search(r'\["names"\]\s*=\s*\{([^\}]+)\}', header)

        # types = re.findall(r'\'(.+?)\'', types_match.group(1)) if types_match else []
        names = re.findall(r'\'(.+?)\'', names_match.group(1)) if names_match else []
        # 提取数据部分
        data_pattern = r'\["data"\] = {.*?},\s*}'
        data_match = re.search(data_pattern, lua_content, re.DOTALL)
        # print(data_match.group(0))
        data = data_match.group(0)[:-2]

        data_list = []
        if data_match:
            data_content = data
            data_rows = re.findall(r'\{([^\}]+)\}', data_content)
            for row in data_rows:
                values = re.findall(r'\'(.*?)\'(?:,\s*|$)|\s*([^,\'\s]+)\s*(?:,|$)', row)
                cleaned_values = [v[0] if v[0] else v[1] for v in values]
                data_list.append(cleaned_values)
        else:
            print("Warning: No data found in Lua content")

        # 更新配置
        config_info = {
            'header': header.replace('\r', ''),  # 保存完整的 header 信息
            'footer': footer.replace('\r', ''),  # 保存 footer 信息
            'names': names  # 如果需要后续使用，可以保留
        }
        self.cfg_manager.updateConfig({text_asset.m_Name: config_info})

        return names, data_list

    def package_lua_file(self, text_asset, csv_path):
        """将修改后的 CSV 文件和配置信息一起打包为原来的 Lua 文件格式"""
        config = self.cfg_manager.loadConfig().get(text_asset.m_Name, {})

        # 使用原始的 Lua 结构
        lua_data = config['header']
        # print(lua_data)
        lua_data += '\n'

        # 从 CSV 文件读取数据
        df = pd.read_csv(csv_path, dtype=str)
        for _, row in df.iterrows():
            lua_data += '{'
            row_data = []
            for val in row:
                if pd.isna(val):
                    processed_val = ''  # 空值处理
                else:
                    processed_val = str(val).replace("'", "\\'")  # 转义单引号
                row_data.append(f"'{processed_val}'")
            lua_data += ',\t'.join(row_data)
            lua_data += '},\n'

        lua_data += config['footer']
        lua_data += '\n'

        # 保存到 test.lua 文件
        with open('test', 'w', encoding='utf-8') as file:
            file.write(lua_data)

        return lua_data

    def save_to_csv(self, text_asset, column_names, data_list):
        """将提取的数据保存为 CSV 文件"""
        df = pd.DataFrame(data_list, columns=column_names)
        save_path = self.cfg_manager.get("output_folder_extract", "./data/3-merge")
        save_filename = os.path.join(save_path, f"{text_asset.m_Name.split('.')[0]}.csv")
        print(f"Saving data to {save_filename}")
        df.to_csv(save_filename, index=False)
        return save_filename

    async def run_extraction(self):
        """执行提取逻辑，遍历 Unity 对象并提取所需 Lua 文件的数据"""
        file_path = self.cfg_manager.get("input_file_extract", "./data/2-origin/luascripts-decrypted")  # 从配置获取文件路径
        with open(file_path, "rb") as file:
            environment = UnityPy.load(file)

        for obj in environment.objects:
            if obj.type.name == 'TextAsset':
                text_asset = obj.read()
                if text_asset.m_Name in ["cfgSound1.lua", "cfgSound.lua"]:
                    print(f"Found Lua file: {text_asset.m_Name}")

                    # 提取 Lua 数据并直接存储配置信息
                    column_names, data_list = self.extract_lua_data(text_asset)

                    # 保存为 CSV 文件
                    csv_path = self.save_to_csv(text_asset, column_names, data_list)
                    print(f"Data saved to {csv_path}")

    async def run_packaging(self):
        """执行打包逻辑，根据修改后的 CSV 文件和配置重新打包为 Lua 文件格式"""
        file_path = self.cfg_manager.get("output_file_decrypt", "./data/2-origin/luascripts-decrypted")  # 从配置获取文件路径
        with open(file_path, "rb") as file:
            environment = UnityPy.load(file)

        for obj in environment.objects:
            if obj.type.name == 'TextAsset':
                text_asset = obj.read()
                if text_asset.m_Name in ["cfgSound1.lua", "cfgSound.lua"]:
                    print(f"Packing Lua file: {text_asset.m_Name}")

                    # 获取合并后的 CSV 文件路径
                    csv_path = self.cfg_manager.get("output_file_merge", "./data/3-merge")
                    csv_filename = os.path.join(csv_path, f"{text_asset.m_Name.split('.')[0]}.csv")
                    print(csv_filename)
                    # 打包 Lua 文件格式
                    lua_data = self.package_lua_file(text_asset, csv_filename)

                    # 修改 Lua 数据，保存到 TextAsset 的 m_Script 属性
                    text_asset.m_Script = lua_data

                    # 取 m_Name 前的文件名，不包含后缀
                    base_name = os.path.splitext(text_asset.m_Name)[0]
                    # 存储打包后的 Lua 数据
                    lua_output_path = self.cfg_manager.get("output_folder_pack", "./data/4-pack")
                    lua_filename = os.path.join(lua_output_path, f"{base_name}_packed.txt")
                    with open(lua_filename, 'w', encoding='utf-8') as lua_file:
                        lua_file.write(lua_data)
                    print(f"Packed Lua data saved to {lua_output_path}")
                text_asset.save()
        # 确保输出路径存在

        # 使用 environment.save() 保存修改后的资源包到目标路径
        new_lua_path = self.cfg_manager.get("output_folder_pack", "./data/4-pack")
        environment.save(pack="lzma", out_path = new_lua_path)  # 传递保存路径给 environment.save()
        if os.path.exists(os.path.join(new_lua_path, "luascripts-packed")):
            os.remove(os.path.join(new_lua_path, "luascripts-packed"))
        os.rename(os.path.join(new_lua_path, "luascripts-decrypted"),
                  os.path.join(new_lua_path, "luascripts-packed"))
        print(f"Modified Unity package saved to {new_lua_path}")



if __name__ == "__main__":
    extractor = ExtractScript()
    # extractor.run_extraction()  # 执行提取
    extractor.run_packaging()  # 执行打包
