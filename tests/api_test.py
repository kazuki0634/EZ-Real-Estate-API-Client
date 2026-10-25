import requests
import pandas as pd

#APIキー
API_KEY = "API_KEY"

#送信先URL（external以降のIDでどのAPIを使うかを決める）
URL = "https://www.reinfolib.mlit.go.jp/ex-api/external/XIT001"

#ヘッダー
headers = {"Ocp-Apim-Subscription-Key": API_KEY}

#パラメータ
params = {
    "year": "2025",
    "quarter": "1",
    "area": "10,27",
    "city": "",
    "priceClassification": "02"
}

#レスポンスを受け取る
try:
  response = requests.get(URL, headers=headers, params=params, timeout=10)

  response.raise_for_status() #HTTPエラーなら例外を発生させる

  data = response.json() #データをjson化

  if "data" in data and data["data"]:  #jsonに"data"キーがあるなら実行
    df = pd.DataFrame(data["data"])
    print(df.head())

    #CSV保存
    df.to_csv("data_2.csv", index=False, encoding="utf-8-sig")
    print("保存完了")

  else:
    print("データがありません。")
    print(data)
  

#エラー一覧
except requests.exceptions.HTTPError as e:
  print(f"HTTPエラーが発生しました {e}")
  print(response.status_code)   # HTTPステータスコード
  print(response.text)          # APIから返ってきた内容

except requests.exceptions.RequestException as e:
  print(f"APIリクエストに失敗しました: {e}")
