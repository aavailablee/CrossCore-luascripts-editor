import os
import time

import pandas
import pandas as pd

from config.configManager import ConfigManager
from config.log import SingletonLogger


class MergeScript:
    def __init__(self, dataFrame):
        self.dataFrame = dataFrame
        self.cfg_manager = ConfigManager()
        self.logger = SingletonLogger().get_logger()

    def mergeScript(self):
        mergedPath = ConfigManager.getPath("merge_folder")
        fileList = os.listdir(mergedPath)
        for index, file in enumerate(fileList):
            if file.endswith(".csv") and not file.startswith("merged_"):
                print(f"{index}: {file}")
                with open(f'{mergedPath}/{file}', 'r', encoding='utf') as csvFile:
                    try:
                        singleFile = pandas.read_csv(csvFile)
                        self.mergeScriptSingle(singleFile)
                    except pandas.errors.EmptyDataError as e:
                        print(f"{e}: {file}")
        self.saveScript()

    def mergeScriptSingle(self, singleFile):
        # 假设 'key' 是连接列，并且 'script1' 是要替换的列
        # 使用 pandas 的 merge 函数进行左连接，并选择替换列
        # 这里的 'key' 是主键，'script1'是你需要替换的列名
        updated_df = pd.merge(self.dataFrame, singleFile[['key', 'script1', 'script2']], on='key', how='left',
                              suffixes=('', '_new', ))

        # 用 singleFile 中的 script1 列替换 self.dataFrame 中相应的列
        updated_df['script1'].update(updated_df['script1_new'])
        updated_df['script2'].update(updated_df['script2_new'])

        # 删除临时生成的 'script1_new' 列
        updated_df.drop(columns=['script1_new'], inplace=True)
        updated_df.drop(columns=['script2_new'], inplace=True)

        # 更新 self.dataFrame
        self.dataFrame = updated_df

    def detachScript(self,
                     model: str = '',
                     key: str = ''):
        detach_df = None
        if model is None and key is None:
            self.logger.error("Please provide either model(3048) or key(Ushuaia)")
            raise Exception("detachScript requires model or key parameter")
        elif model:
            detach_df = self.dataFrame[self.dataFrame['model'].astype(str).str[:4] == model]
        elif key:
            detach_df = self.dataFrame[self.dataFrame['key'].str.split('_').str[0] == key]
        output_folder_detach_df = self.cfg_manager.get('output_folder_detach_folder', './data/3-merge/detach')
        filename = os.path.join(output_folder_detach_df, key+'.csv')
        if detach_df:
            detach_df.to_csv(filename, index=False)
        else:
            self.logger.warning("404 File Not Found")


    def saveScript(self):
        mergePath = ConfigManager.getPath("merge_folder")
        nameString: str = "merged_" + time.strftime("%y%m%d_%H%M%S") + ".csv"
        mergedName = os.path.join(mergePath, nameString)
        self.dataFrame.to_csv(mergedName, index=False)
        print(f"merged")
    def savetoPacket(self):
        mergePath = ConfigManager.getPath("merge_folder")
        print(mergePath)


if __name__ == '__main__':


    dataframe = pd.read_csv('../data/3-merge/cfgSound1.csv', dtype='str')
    mergeScript = MergeScript(dataframe)
    df = mergeScript.detachScript(model='3048', key='Ushuaia')
    print(df)
