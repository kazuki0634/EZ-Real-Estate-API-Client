import json
from pathlib import Path

#データ保存の本体処理
def save(data, ext_option, filename, save_dir):

  #文字列をPathオブジェクトにする
  save_path = Path(save_dir)

  #データの形式が辞書だった場合複数回繰り返す
  if isinstance(data, dict):
    print(f"data = {data}")

    #まとめて保存するファイルのディレクトリのパスを作る
    new_folder_dir = f"{save_dir}/{filename}"
    save_path = Path(new_folder_dir)

    #重複していないならパスをもとにディレクトリを作る
    if not save_path.exists():
      save_path.mkdir()

    #データごとに辞書のキーを名前の最初につけて保存する
    for key, value in data.items():

      tmp_filename = add_ext_option(f"{filename}_{key}", ext_option)

      save_file(value, ext_option, tmp_filename, save_path)

    return True

  #データの形式がそれ以外ならそのまま保存する
  else:
    #拡張子の確認
    filename = add_ext_option(filename, ext_option)

    save_file(data, ext_option, filename, save_path)
    return True

#保存形式に合わせてファイルを保存する
def save_file(data, ext_option, filename, save_path):

  #PBF形式はdataがjsonのまま
  if ext_option == ".pbf":
    with open(save_path / filename, "wb", encoding="utf-8-sig") as f: #wbはバイナリ書き込み専用
      f.write(data)

  #JSON形式、GeoJSON形式はdataがJSONのまま
  if ext_option in [".json", ".geojson"]:
    with open(save_path / filename, "w", encoding="utf-8-sig") as f:
      json.dump(data, f, indent=2, ensure_ascii=False) #ensure_asciiで全角文字がエスケープされるのを防ぐ

  #CSV形式はdataがデータフレーム
  if ext_option == ".csv":
    data.to_csv(save_path / filename, index=False, encoding="utf-8-sig")

#ファイル名に拡張子をつける
def add_ext_option(filename, ext_option):

  L_f = len(filename)
  L_e = len(ext_option)
  if filename[L_f-L_e:L_f] != ext_option:
    filename += ext_option

  return filename

#保存先のディレクトリが正しいか確認する
def is_correct_save_dir(save_dir):

  #save_dirに空白が渡されたら終了
  if not save_dir:
    return False

  #保存先のディレクトリが正しいかを確認
  try:
    save_path = Path(save_dir)

    #保存先のディレクトリが存在しないなら終了
    if not save_path.is_dir():
      return False

  #エラーが出ても終了
  except (TypeError, ValueError):
    return False
  
  #エラーが出なければTrue
  return True

#同名ファイルがあるかどうかを確認する
def is_dupulicate_file(save_dir, filename, ext_option, is_bundle):

  #単体ダウンロードの場合
  if not is_bundle:
    filename = add_ext_option(filename, ext_option)

  #保存先のパス
  save_path = Path(save_dir) / filename

  print(f"filename = {filename}")
  print(f"save_path = {save_path}")

  #保存先に同名ファイルまたは同名フォルダがあるかどうか
  if save_path.exists():
    return True

  else:
    return False