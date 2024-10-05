class ABCustom:
    arrEncypt = [2, 3, 1, 1, 3, 1, 2, 1, 1, 3, 1, 2, 4, 1, 1, 2, 2, 4, 4]

    @staticmethod
    def DdooEennccyyppttSsttrr(string: str) -> str:
        strArr = list(string)
        indexArr = 0
        length = len(string)

        i = 0
        while i < length:
            arrEncyptVal = ABCustom.arrEncypt[indexArr]
            indexArr = (indexArr + 1) % len(ABCustom.arrEncypt)  # 循环

            j = i + arrEncyptVal
            if j >= length:
                break

            strArr[i], strArr[j] = strArr[j], strArr[i]
            i = j + 1

        return ''.join(strArr)

    @staticmethod
    def DdooEennccyypptt(targetData: bytearray):
        # print(len(targetData))
        # key = (len(targetData) % 254) + 1  # 动态初始化 key 值
        key = (len(targetData) % 254)  # 动态初始化 key 值
        # key = ( (len(targetData)-1) % 254) + 1  # 动态初始化 key 值 c# ignore 0b
        # print(key)
        step = max(1, len(targetData) // 100)

        for i in range(0, len(targetData), step):
            originValue = targetData[i]
            # 执行 XOR 操作，并且确保结果在 0-255 之间
            targetData[i] = (targetData[i] ^ key) & 0xFF
            # 更新 key 值，模拟 C# 的 byte 操作，确保值在 0-255 范围内
            key = (originValue + targetData[i]) & 0xFF

    # @staticmethod
    # def DdooEennccyypptt(targetData: bytearray):
    #     key = (len(targetData) % 254) + 1  # 模拟 C# 计算 key 的方式
    #     step = max(1, len(targetData) // 100)
    #
    #     for i in range(0, len(targetData), step):
    #         originValue = targetData[i]
    #         targetData[i] = (targetData[i] ^ key) & 0xFF  # 确保字节值在 0-255 之间
    #         key = (originValue + targetData[i]) & 0xFF  # 保持 C# 的溢出行为


