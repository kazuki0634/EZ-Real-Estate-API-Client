import json

import paths #頻出するパスをここから得る

#渡されたキーと値の組をsettings.jsonに入れる
def save_to_settings(key, value):

  #settings.jsonの中身を入れる辞書を作る
  settings = {}

  #読み込み専用でファイルを開く
  with open(paths.SETTINGS_FILE, "r", encoding="utf-8") as f:

    #settings.jsonの中身を辞書に入れる
    settings = json.load(f)
    
    #辞書にキーと値を保存する
    settings[key] = value

  #書き込み専用でファイルを開く
  with open(paths.SETTINGS_FILE, "w", encoding="utf-8") as f:

    #settings.jsonに新しいjsonを保存する
    json.dump(settings, f, indent=2, ensure_ascii=False)

  print(f"settings.jsonに保存完了　キー={key}")

#settings.jsonからキーに対応する値を受け取ってgui.pyに渡す
def get_from_settings(key):
  
  #読み込み専用でファイルを開く
  with open(paths.SETTINGS_FILE, "r", encoding="utf-8") as f:
    json_f = json.load(f)
    value = json_f[key]
    print(f"settings.jsonから取得完了　キー={key}")

    return value
  