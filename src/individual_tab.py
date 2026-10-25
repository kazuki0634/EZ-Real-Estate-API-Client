import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import threading

import api #APIとの通信
import save_utils #api.pyから受けとったdataを保存するためのもの
import settings #ユーザ設定用のjsonに読み書きするためのもの

from tab import Tab #タブのクラス

import time

#個別ダウンロードのタブのクラス
class IndividualTab(Tab):
  def __init__(self, def_width, def_height, root, api_key, api_catalog, tab_frame):
    super().__init__(def_width, def_height, root, api_key, api_catalog, tab_frame)

    #タブの名前
    self.tab_name = "individual_tab"

    #現在のAPI名
    self.api_name = tk.StringVar()

    #入力欄用フレーム
    self.input_frame = None

    #保存用フレーム
    self.save_frame = None

    #保存成功時のラベル
    self.success_label = None

    #date_time
    self.dt = datetime.datetime.now()

    #マウスの位置
    self.mouse_x = None
    self.mouse_y = None

  #使用するAPIを選択するプルダウンを作る
  def create_choose_api(self):
    
    #API名一覧を作る
    self.api_names = [
      f"{api_id}：{api_info["name"]}"
      for api_id, api_info in self.api_ids.items()
    ]

    print(self.api_names)

    #API選択用のフレームを作る
    self.choose_frame = ttk.Frame(self.tab_frame)
    self.choose_frame.pack(anchor="w", padx=20, pady=3)

    #ラベル
    api_name_label = ttk.Label(
      self.choose_frame,
      text="API一覧"
    )
    api_name_label.grid(row=0, column=0, sticky="ew")

    #必須の説明のラベル
    requried_label = ttk.Label(
      self.choose_frame,
      text="（パラメータに必須とあるものは必ず入力してください）"
    )
    requried_label.grid(row=0, column=1)

    #プルダウン
    self.api_name_combobox = ttk.Combobox(
      self.choose_frame,
      width=60,
      background="#F0F0F0",
      textvariable=self.api_name,
      values=self.api_names,
      state="readonly" #ユーザが直接編集禁止
      )

    #ユーザがComboboxを選択する度に呼び出される
    self.api_name_combobox.bind( 
      "<<ComboboxSelected>>",
      lambda event: self.choose_api(event)
    )
    self.api_name_combobox.grid(row=1, column=0)

    #（※１）が単一選択であることについての説明
    label_1 = ttk.Label(
      self.choose_frame,
      text="（パラメータに※のあるものは最低１つ選択してください）"
    )
    label_1.grid(row=1, column=1)

  #プルダウンで選択したAPIのIDを取得
  def choose_api(self, event):

    #プルダウン選択時、プルダウンからAPIの表示名を取得
    api_name = self.api_name_combobox.get()

    #APIのIDを取得
    self.api_id = api_name[0:6] #APIの表示名の先頭6文字がAPIのID

    #api_idsから使用するAPIの部分だけ抜き出す
    self.api_info = self.api_ids[self.api_id] 

    print("API名:", api_name)
    print("API ID:", self.api_id)
    print("API情報:", self.api_info)

    #入力用と保存用のフレームを作る
    super().create_frames()

    super().create_input_frame()

  #ダウンロード準備
  def prepare_download(self):

    #api.pyに渡すパラメータの辞書を作る
    params = super().create_params(self.widgets, self.api_info)

    #バリデーションチェック
    is_ok = super().check_validate(params, self.api_id)
    if not is_ok:
      return

    #保存形式やcsvの１行目を日本語にするかの設定の取得
    ext_option, is_trans = super().get_ext_options()

    #StringVar（ウィジェット変数）からAPIキーの文字列を取り出す
    api_key = self.api_key.get()

    #保存先の取得
    save_dir = self.save_entry.get()
    print(f"save_dir = {save_dir}")

    #保存先のディレクトリが正しいか確認
    if not save_utils.is_correct_save_dir(save_dir):
      super().failed_download(
        "ディレクトリエラー", "保存先のフォルダが正しいか確認してください")
      
      return

    #ファイル名の取得
    filename = self.file_name_entry.get()

    #同名ファイルが存在するかの確認
    is_ok = super().confirm_overwrite(save_dir, filename, ext_option)
    if not is_ok:
      return

    #ダウンロード中のウィンドウを出す
    super().open_downloading_window("indeterminate")

    #ダウンロード処理とダウンロード中の表示を別スレッドで行う
    download_thread = threading.Thread(
      target=self.download,
      args=(api_key, params, ext_option, is_trans, filename, save_dir)
    )
    download_thread.start()

  #ダウンロードの本体処理
  def download(self, api_key, params, ext_option, is_trans, filename, save_dir):

    #保存形式に対応したデータをAPIから受け取る
    data = api.get_api_data(self.api_id, api_key, params, ext_option)

    print(f"data = {data}")
    print(f"data_type = {type(data)}")

    #レスポンスがエラーかどうかを判定する
    if super().is_response_error(data):
      return

    #csv保存の時、任意でデータフレームの１行目の見出しを英語→日本語にする
    if ext_option == ".csv":
      if is_trans and "response_trans" in self.api_info:
        response_trans = self.api_info["response_trans"]
        data.rename(columns=response_trans, inplace=True) #inplace=Trueで元のdf自体を書き換え
    
    #名前を付けて保存
    can_save = save_utils.save(data, ext_option, filename, save_dir)
    if not can_save:
      self.root.after(
        0,
        super().failed_download,
        "ディレクトリエラー",
        "保存先のフォルダが正しいか確認してください"
      )
      return

    #ダウンロード成功時の処理をする
    self.root.after(
      0,
      super().succeeded_download,
      (filename)
    )