import requests
import pandas as pd

#urlのベース
base_url = "https://www.reinfolib.mlit.go.jp/ex-api/external"

#レスポンスを受け取る関数
def get_api_data(api_id, api_key, params, ext_option):

  #送信先URL（external以降のIDでどのAPIを使うかを決める）
  url = f"{base_url}/{api_id}"

  #ヘッダー
  headers = {"Ocp-Apim-Subscription-Key": api_key}

  #レスポンスを受け取る
  response = requests.get(url, headers=headers, params=params, timeout=10)

  #ログを表示
  print("status:", response.status_code)
  print("url:", response.url)
  print("response:", response.text)

  #エラーの際はmessageが含まれることを利用して、エラーを検出する
  if "message" in response.text: 
    return response.text

  status = response.raise_for_status() #HTTPエラーなら例外を発生させる

  print(f"statusはこうなる\n{status}")

  #PBFならレスポンスの内容をバイナリ形式で返す
  if ext_option == ".pbf":
    return response.content

  data = response.json() #データをjson化

  #GeoJSONならレスポンスをjson化したところで返す
  if ext_option in [".geojson", ".json"]:
    return data

  if "data" not in data or not data["data"]:  #データがない場合は空のデータフレームを返す
    return pd.DataFrame()

  return pd.DataFrame(data["data"]) #データフレームを返す
