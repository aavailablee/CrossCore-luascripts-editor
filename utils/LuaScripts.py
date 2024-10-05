import pickle

import requests

from utils.ABCustom import ABCustom


class LuaScripts:

    @staticmethod
    def GenEncryptABData(rawfile, outfile, isAndroid, fix=True):
        with open(rawfile, 'rb') as f:
            rawBytes = bytearray(f.read())

        if fix:
            luaFileURL = "https://cdn.megagamelog.com/cross/release/android/curr/Custom/luascripts" if isAndroid else \
                "https://cdn.megagamelog.com/cross/release/ios/curr/Custom/luascripts"

            try:
                response = requests.head(luaFileURL)
                response.raise_for_status()
                fileSize = int(response.headers.get('Content-Length', 0))
                len_target = fileSize - 153  # 最后好像是个0b

                print(f"Lua file size should be: {len_target}, "
                      f"but got {len(rawBytes)}")

                if len(rawBytes) <= len_target:
                    print("Extending rawBytes to fit the Lua file size.")
                    padding_length = len_target - len(rawBytes)
                    rawBytes.extend(bytes(padding_length))  # 使用零字节填充
                else:
                    raise Exception("rawBytes is too long")
                print("rawBytes is OK.")

            except requests.RequestException as e:
                print(f"Error: {str(e)}")
                return

                # 直接对 rawBytes 进行加密操作
            rawBytes = rawBytes + bytes([0x0b])  # most important
            ABCustom.DdooEennccyypptt(rawBytes)
            print(f"{len(rawBytes)}")

            # 请求文件的前 152 字节并将其并入
            try:
                response = requests.get(luaFileURL, headers={'Range': 'bytes=0-151'})
                response.raise_for_status()

                if len(response.content) != 152:
                    raise Exception(f"Failed to download exactly 152 bytes, got {len(response.content)} bytes.")

                # 将下载的 152 字节附加到 rawBytes 前面
                finalBytes = response.content + rawBytes

                print("152 bytes from URL prepended to finalBytes.")

            except requests.RequestException as e:
                print(f"Error: {str(e)}")
                return

            # 只保存 finalBytes
            with open(outfile, 'wb') as f:
                f.write(finalBytes)

    @staticmethod
    def GenDecryptABData(rawfile, outfile):
        with open(rawfile, 'rb') as f:
            f.seek(152)  # Skip the first 152 bytes
            bytesData = bytearray(f.read())
        # print(bytesData[0])
        ABCustom.DdooEennccyypptt(bytesData)
        # print(bytesData[0])
        with open(outfile, 'wb') as f:
            f.write(bytesData)