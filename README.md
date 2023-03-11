# CYL_SCP

## 使用說明
### 1. 安裝相關套件
在CYL_SCP資料夾中執行指令: `pip3 install -r requirements.txt`
### 2. 修改config.json
參數說明

`source_files`: 要上傳或下載的所有檔案路徑

`source_folders`: 要上傳或下載的所有資料夾路徑

* 上傳檔案請修改`put_config.json`
* 下載檔案請修改`get_config.json`

把config中的key改為`_source_folders`或`_source_files`就不會對該項目進行操作

### 3. 執行方式
在CYL_SCP資料夾中執行python指令

查看程式參數說明`python3 cylscp.py -h`
```python
CYL-SCP help you get transfer files !

options:
  -h, --help            show this help message and exit
  -P                    do put (upload)
  -G                    do get (download)
  -H HOST [HOST ...]    host: ip or mac(d0:14:11:b0:0f:12) with interface
  -u USER_PWD USER_PWD  username and password
  -c CONFIG_FILE        config file
  -d [TARGET_DIR]       target directory

enjoy !!! Mark and Ken Love u
```

上傳範例:
```
python3 cylscp.py -P -H <IPv4/IPv6(MAC INTERFACE)> -u <USER> <PASSWD> -d <TARGET_DIRECTORY> -c <CONFIG_PATH>

python3 cylscp.py -P -H 192.168.50.165 -u root root -d /root -c ./put_config.json
```

  * 上傳遠段位置預設為`/`，你可使用參數 `-d` 變更存放位置。
  * 上傳的 config.json 可使用相對路徑(相對於此 config.json 目錄的位置)填寫。

下載範例:
```
python3 cylscp.py -G -H <IPv4/IPv6(MAC INTERFACE)> -u <USER> <PASSWD> -c <CONFIG_PATH>
python3 cylscp.py -G -H d0:14:11:b0:0f:75 19 -u root root -c ./get_config.json
```

  * 使用下載模式的話會建立資料夾(IPv6: 資料夾名稱為mac號碼，IPv4: 資料夾名稱為IP)。
  * 下載預設目錄為 `(config.json目錄的位置)/(ip/mac)/`，你可使用參數 `-d` 變更存放位置。