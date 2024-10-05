import asyncio
from pathlib import Path

import requests

from config.configManager import ConfigManager
from utils.main import utils_main

cfgManager = ConfigManager()

## abc
class DecryptScript:
    def __init__(self,
                 input_file_decrypt: str = '',
                 output_file_decrypt: str = '',
                 input_file_encrypt: str = '',
                 output_file_encrypt: str = '',
                 isAndroid: bool = True,
                 game: str = ''):
        self.game = game if game != '' else 'JCZX'
        self.input_file_decrypt = input_file_decrypt if input_file_decrypt != '' \
            else cfgManager.get("input_file_decrypt", './data/1-resource/luascripts')
        self.output_file_decrypt = output_file_decrypt if output_file_decrypt != '' \
            else cfgManager.get("output_file_decrypt", './data/2-origin/luascripts-decrypted')
        self.input_file_encrypt = input_file_encrypt if input_file_encrypt != '' \
            else cfgManager.get("input_file_encrypt", './data/4-pack/luascripts-packed')
        self.output_file_encrypt = output_file_encrypt if output_file_encrypt != '' \
            else cfgManager.get("output_file_encrypt", './data/5-output/luascripts-encrypted')
        self.isAndroid = isAndroid

    async def decrypt(self):
        if self.game == 'JCZX':
            #  todo
            if (None is self.input_file_decrypt) or (None is self.output_file_decrypt):
                raise Exception(f'解密流程，参数不足，'
                                f'inputFileDecrypt:{self.input_file_decrypt}, '
                                f'outputFileDecrypt:{self.output_file_decrypt}')
            # 显式传递参数列表
            args = ['-i', self.input_file_decrypt,
                    '-o', self.output_file_decrypt,
                    '--decrypt',
                    '--platform', 'android' if self.isAndroid else 'ios']
            utils_main(args)
            pass
        else:
            # throw
            raise Exception(f"未指定游戏")
            pass

    async def encrypt(self):
        if self.game == 'JCZX':
            #  todo
            if (None is self.input_file_encrypt) or (None is self.output_file_encrypt):
                raise Exception(f'加密流程，参数不足，'
                                f'inputFileEncrypt:{self.input_file_encrypt}, '
                                f'outputFileEncrypt:{self.output_file_encrypt}')
            # 显式传递参数列表
            args = ['-i', self.input_file_encrypt,
                    '-o', self.output_file_encrypt,
                    '--encrypt',
                    '--platform', 'android' if self.isAndroid else 'ios']
            utils_main(args)
            pass
        else:
            # throw
            raise Exception(f"未指定游戏")
            pass

    async def get_file_size_async(self, url: str) -> int:
        try:
            response = requests.head(url)
            if response.status_code == 200:
                return int(response.headers.get('Content-Length', 0))
            else:
                raise Exception(f"Failed to get file size. HTTP {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
            return 0


if __name__ == '__main__':
    size = asyncio.run(
        DecryptScript('./utils/test', './utils/test2').encrypt()
    )
    print(size)
