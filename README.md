# nhentai-downloader

批次下載 nHentai 相簿的小工具。

A CLI tool to batch-download nHentai gallery.

> 根據歐盟新通過並於 2020 正式實施的兒少保護法規細則，禁止戀童物內容，負責人 Maximum_Joe 在 4Chan 討論區確認並宣布，exHentai 遭到原本儲存機房拒絕合作以避免違法，負責人也表示也不太願意在這個多國禁令之下跨國繼續找機房，他們將在最慢六個月內完全關站，**子站 eHentai 、備份站 nHentai 則可以運行到 2020 年**。

## Prerequisites

* Platform
    * Any platform which support Python 3
* Packages
    * argparse
    * json
    * requests
    * bs4

## Usage

透過下載原始碼並以 Python 3 執行。

Windows 使用者除上述方法外，亦可由 [Release](https://github.com/ychsieh95/nhentai-downloader/releases) 取得 nhentai-downloader.exe，此程式執行不需安裝 Python 3。

### Arguments

**此參數列表為依優先權由高至低列出，範例說明可參考 [`#Example`](#example)。**

* `-i`, `--id`
    * 指定下載的相簿 ID。
* `-bi`, `--begin-id`
    * 指定開始下載的相簿 ID，須與 `--end-id` 一同使用。
* `-ei`, `--end-id`
    * 指定結束下載的相簿 ID，須與 `--begin-id` 一同使用。
* `-u`, `--url`
    * 指定下載的列表。
* `-bp`, `--begin-page`
    * 指定開始下載的列表頁數，若未設定 `--end-page` 則會下載直到最後一頁。
* `-ep`, `--end-page`
    * 指定結束下載的列表頁數，若未設定 `--begin-page` 則會由第一頁開始下載。
* `-s`, `--save-dir`
    * 指定輸出的資料夾路徑，預設為當前目錄。Windows 用戶建議將路經中的 `\` 置換為 `/`。
* `-e`, `--exists-stop`
    * 當下載的相簿 ID 存在，則結束程式，優先權較 `--overwrite` 高。
* `-ow`, `--overwrite`
    * 當下載的相簿 ID 存在，則覆寫相簿，優先權較 `--exists-stop` 低。
* `-l`, `--limit`
    * 限制下載的相簿數量。

## Example

範例為透過 Python 3 執行，若是使用 nhentai-downloader.exe 則將範例中的 `python3 main.py` 置換為 `nhentai-downloader.exe` 即可。

```bash
# 下載 ID 為 xxxxxx 的相簿
$ python3 main.py --id=xxxxxx

# 下載 ID 由 xxxxxx 至 yyyyyy 的相簿
$ python3 main.py --begin-id=xxxxxx --end-id=yyyyyy

# 下載所有相簿並儲存至 ~/galleries
$ python3 main.py --url=https://nhentai.net/ --save-dir=~/galleries

# 下載 5-8 頁的相簿
$ python3 main.py --url=https://nhentai.net/ --begin-page=5 --end-page=8

# 下載所有相簿，若存在則結束下載
$ python3 main.py --url=https://nhentai.net/ --exists-stop

# 下載所有相簿，若存在則覆蓋相簿
$ python3 main.py --url=https://nhentai.net/ --overwrite

# 下載所有相簿但不超過 100 本
$ python3 main.py --url=https://nhentai.net/ --limit=100

# 優先權範例 1：僅會下載 xxxxxx 相簿
$ python3 main.py --id=xxxxxx --begin-id=yyyyyy --end-id=zzzzzz --begin-page=5 --end-page=8

# 優先權範例 2：僅會下載 yyyyyy-zzzzzz 相簿
$ python3 main.py --begin-id=yyyyyy --end-id=zzzzzz --begin-page=5 --end-page=8

# 優先權範例 3：當相簿已存在，則會結束下載而非覆蓋
$ python3 main.py --url=https://nhentai.net/ --exists-stop --overwrite
```

## Disclaimer

此專案僅為學術研究交流用途，請使用者在評估相關爭議與可能風險與責任後再決定是否使用。

The project only for academic exchange. Please assess the associated risks and responsibilities before using.