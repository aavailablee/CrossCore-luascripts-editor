# CrossCore-luascripts-editor

用了UnityPy和https://github.com/AXiX-official 的解加密逻辑


平台就android，ios我没测

### 首先要在data/1-resource里放源luascripts
### 2-origin，被解密的luascripts
### 3-merge

- 目录下是解析出来的4个csv文件（要其他的就在ExtractScript里添加，但有可能要重设计正则匹配） 
- 比如现在修改cfgSound1的没问题，但是cfgCfgLanguage修改了，还进不去（估计正则匹配问题）
- detach，按model(3048)或key(Ushuaia)分离出cfgSound/cfgSound1里的信息，merge后内容存在modified文件夹下
- modified，merge后的csv，之后步骤用


### 4-pack

- txt就是m_Scripts内容
- luascripts-packed就是打包的luascripts


### 5-output

- luascripts-encrypted改名luascripts放进custom里

