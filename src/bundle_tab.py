import datetime
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import threading

import api #APIとの通信
import save_utils #api.pyから受けとったdataを保存するためのもの
import settings #ユーザ設定用のjsonに読み書きするためのもの

from tab import Tab

#定数
#地理空間情報のほうに必要なパラメータ
geo_params = ["response_format", "z", "x", "y"]

#個別ダウンロードのタブのクラス
class BundleTab(Tab):
  def __init__(self, def_width, def_height, root, api_key, api_catalog, tab_frame):
    super().__init__(def_width, def_height, root, api_key, api_catalog, tab_frame)

    #タブの名前
    self.tab_name = "bundle_tab"

    #現在の利用形式
    self.usage = tk.StringVar()
    self.usages = ["不動産価格情報", "鑑定評価情報", "地理空間情報"]

    #カテゴリのリスト
    self.categories = self.api_catalog["categories"]

    #入力欄用フレーム
    self.input_frame = None

    #保存用フレーム
    self.save_frame = None

    #保存成功時のラベル
    self.success_label = None

    #date_time
    self.dt = datetime.datetime.now()

  #利用形式選択するプルダウンを作る
  def create_choose_usage(self):

    #API選択用のフレームを作る
    self.choose_frame = ttk.Frame(self.tab_frame)
    self.choose_frame.pack(anchor="w", padx=20, pady=3)

    #ラベル
    api_name_label = ttk.Label(
      self.choose_frame,
      text="利用形式"
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
      width=17,
      background="#F0F0F0",
      textvariable=self.usage,
      values=self.usages,
      state="readonly" #ユーザが直接編集禁止
      )

    #ユーザがComboboxを選択する度に呼び出される
    self.api_name_combobox.bind( 
      "<<ComboboxSelected>>",
      lambda event: self.choose_usage(event)
    )
    self.api_name_combobox.grid(row=1, column=0)

    #（※１）が単一選択であることについての説明
    label_1 = ttk.Label(
      self.choose_frame,
      text="（パラメータに※のあるものは最低１つ選択してください）"
    )
    label_1.grid(row=1, column=1)

  #プルダウンで選択した利用形式からどのAPIを使うか選択
  def choose_usage(self, event):

    #選択した利用形式のインデックスを取り出す
    self.usage_index = self.api_name_combobox.current()

    super().create_frames()

    if self.usage_index == 0:
      self.api_id = "XIT001"
      self.api_info = self.api_ids[self.api_id]
      self.create_period_input_fields()

    elif self.usage_index == 1:
      self.api_id = "XCT001"
      self.api_info = self.api_ids[self.api_id]
      self.create_period_input_fields()

    elif self.usage_index == 2:
      self.api_id = "XST001"
      self.create_geo_input_fields()

    print(f"api_id = {self.api_id}")

  #複数年ダウンロードに使用するAPIに対応した入力欄を作る
  def create_period_input_fields(self):

    #複数年以外の親クラスの関数をそのまま実行
    super().create_input_frame()

    #開始時期と終了時期のフレームや入力欄を作る
    period_label_lst = ["開始時期", "終了時期"]
    period_name_lst = ["start", "end"]
    quarter_lst = ["1", "2", "3", "4"]

    #入力説明のフレーム
    rule_frame = ttk.Frame(self.input_frame)
    rule_frame.pack(anchor="w", padx=10, pady=(15, 5))

    #入力説明のラベル
    rule_label = ttk.Label(
      rule_frame,
      text=f"〇ダウンロード時期　{self.api_info["params"]["year"]["rule"]}"
    )
    rule_label.pack()

    #開始時期と終了時期
    for i in range(2):

      #複数年ダウンロードのフレーム
      period_frame = ttk.Frame(self.input_frame)
      period_frame.pack(anchor="w", padx=10)

      #時期のラベル
      mutliple_year_label = ttk.Label(
        period_frame,
        text=period_label_lst[i]
      )
      mutliple_year_label.pack(anchor="w")

      #年の入力欄
      year_entry = ttk.Entry(
        period_frame,
        width=10
      )
      year_entry.pack(anchor="w", side="left")

      self.widgets[f"{period_name_lst[i]}_year"] = year_entry

      #「年」のラベル
      year_label = ttk.Label(
        period_frame,
        text="年"
      )
      year_label.pack(anchor="w", padx=1, side="left")

      if self.api_id == "XIT001":
        #四半期のプルダウン
        quarter_combobox = ttk.Combobox(
          period_frame,
          width=10,
          values=quarter_lst,
          state="readonly"
        )
        quarter_combobox.set(quarter_lst[0])
        quarter_combobox.pack(anchor="w", side="left")
        
        self.widgets[f"{period_name_lst[i]}_quarter"] = quarter_combobox

        #「四半期」のラベル
        quarter_label = ttk.Label(
          period_frame,
          text="四半期"
        )
        quarter_label.pack(anchor="w", padx=1, side="left")

  #地理空間情報のダウンロードに使用するAPIに対応した入力欄を作る
  def create_geo_input_fields(self):

    #パラメータ名とその入力欄やプルダウンのウィジェットの辞書
    self.widgets = {}

    #この形式のものを対象とする
    self.api_info = self.api_catalog["api_ids"]["XST001"]

    #保存形式のリスト
    self.ext_options = self.api_info["ext_options"]

    #保存形式、Z、X、Yのウィジェットだけ先に作る
    self.create_geo_widgets()

    #使用するAPIに対応した保存設定欄を作成する
    super().create_save_frame()

    #APIのカテゴリごとのページを作成する
    self.create_pages()

    #z：ズームレベルの初期値をチェックボックスに反映する
    self.check_zoom_level()

  #保存形式、z、x、yのウィジェットだけ先に作る
  def create_geo_widgets(self):

    for param_name in geo_params:
      super().create_params_widget(self.input_frame, param_name, self.api_info["params"][param_name])

    self.widgets["z"].set("15")

    #zの変化したときにチェックボックスの有効・無効を切り替える
    self.widgets["z"].bind(
      "<<ComboboxSelected>>",
      lambda event: self.check_zoom_level(event)
    )

  #zの変化したときにチェックボックスの有効・無効を切り替える
  def check_zoom_level(self, event=None):

    #z（z：ズームレベル）をウィジェットから取り出す
    z = int(self.widgets["z"].get())

    #チェックボックスを作ったAPIのうち
    for api_id, checkbutton in self.checkbuttons.items():

      #zの値がAPI側で指定した範囲内かどうか
      z_options = self.api_ids[api_id]["params"]["z"]["options"]

      #範囲内ならチェックボックスと詳細ボタンを触れるように
      if z_options[0] <= z <= z_options[1]:
        checkbutton.config(state="normal")

        if api_id in self.detail_buttons:
          self.detail_buttons[api_id].config(state="normal")

      #範囲外ならチェックボックスを触れないようにする
      else:
        checkbutton.config(state="disabled")

        #チェックボックスのウィジェット変数もfalseにする
        self.check_vars[api_id].set(False)

        #詳細ボタンがある場合それも触れないようにする
        if api_id in self.detail_buttons:
          self.detail_buttons[api_id].config(state="disabled")

          #詳細ウィンドウの中身のパラメータも空にする
          self.empty_detail_params(api_id)

  #詳細ウィンドウ内のパラメータの辞書のパラメータごとの中身を空にする
  def empty_detail_params(self, api_id):

    params = self.api_ids[api_id]["params"]

    for param_name in params.keys():

      #応答形式、z、x、yはスキップ
      if not param_name in geo_params:
        self.detail_params[api_id][param_name] = ""

  #APIのカテゴリごとのページを作成する
  def create_pages(self):

    #カテゴリのフレーム
    categories_frame = ttk.Labelframe(
      self.input_frame,
      text="カテゴリ"
      )
    categories_frame.pack(fill="both") #x軸いっぱいを埋めるように

    #カテゴリのフレームの
    categories_frame.columnconfigure(0, weight=1)
    categories_frame.rowconfigure(0, minsize=5)

    #ページのリスト
    self.pages = []

    #カテゴリごとにページを作る
    for category in self.categories:

      #ページのフレーム
      page_frame = ttk.Frame(
        categories_frame
      )

      #ページのフレームのチェックボックスの幅を均等にする
      for column in range(3):
        page_frame.columnconfigure(column, weight=1)

      #リストに入れる
      self.pages.append(page_frame)

    #現在のページ番号
    self.current_page_index = 0

    for i, page_frame in enumerate(self.pages):

      #進むボタン、戻るボタン専用のフレーム
      change_page_frame = ttk.Frame(page_frame)
      change_page_frame.grid(row=0, column=0, columnspan=3) #columnspanで複数列にまたがって使える

      #カテゴリ名のラベル
      category_label = ttk.Label(
        change_page_frame,
        text=f"〇 {self.categories[i]}"
      )
      category_label.grid(row=0, column=0, sticky="ew")

      #ラベルの幅を確保する
      change_page_frame.columnconfigure(0, minsize=75)

      #ボタンが非表示の時も幅を確保する
      change_page_frame.columnconfigure(1, minsize=75)
      change_page_frame.columnconfigure(3, minsize=75)

      if i != 0:

        #戻るボタン
        back_button = ttk.Button(
          change_page_frame,
          text="戻る",
          command=lambda i=i: self.change_page(i-1)
        )

        back_button.grid(row=0, column=1)

      #ぺージ番号
      page_index_label = ttk.Label(
        change_page_frame,
        text=f"{i+1} / {len(self.pages)}"
      )

      page_index_label.grid(row=0, column=2, padx=5)

      if i != len(self.pages) - 1:

        #進むボタン
        next_button = ttk.Button(
          change_page_frame,
          text="次へ",
          command=lambda i=i: self.change_page(i+1)
        )

        next_button.grid(row=0, column=3)


    #チェックボックスのウィジェットそのものが入った辞書
    self.checkbuttons = {}

    #チェックボックスのウィジェット変数の入った辞書
    self.check_vars = {}

    #カテゴリごとのAPIの数
    count_api = [0 for _ in range(len(self.categories))]

    #APIごとの詳細ウィンドウ内のパラメータが入った辞書
    self.detail_params = {}

    #APIごとの詳細ウィンドウ内のウィジェットが入った辞書
    self.detail_widgets = {}

    #APIごとの詳細ボタンのウィジェットが入った辞書
    self.detail_buttons = {}

    #APIごとに見る
    for api_id, api_info in self.api_ids.items():

      #カテゴリが設定されていないAPIを除く
      if not "category" in api_info:
        continue

      #表示するかどうか
      is_pack = True

      #APIごとの全パラメータの辞書
      params = api_info["params"]

      #応答形式、z、x、yがなければスキップする
      for param_name in geo_params:
        if not param_name in params:
          is_pack = False
          break

      if not is_pack:
        continue

      #詳細ウィンドウに入れるパラメータの辞書を作る
      self.create_detail_params(api_id, params)

      #チェックボックスの状態を管理する変数
      check_var = tk.BooleanVar(value=False)

      #どのカテゴリか確認する
      for i, category in enumerate(self.categories):

        if api_info["category"] == category:

          #APIごとのフレームを作る
          api_frame = ttk.Frame(self.pages[i])

          #API名 + zの範囲のテキスト
          z_range = api_info["params"]["z"]["options"]
          name = api_info["display_name"]
          text = f"{name}　z：{z_range[0]}～{z_range[1]}"

          #チェックボックス
          checkbutton = ttk.Checkbutton(
            api_frame,
            text=text,
            variable=check_var
          )
          checkbutton.grid(row=0, column=0)

          #チェックボックスとそれを管理するウィジェット変数をそれぞれ辞書に入れる
          self.checkbuttons[api_id] = checkbutton
          self.check_vars[api_id] = check_var

          #詳細ウィンドウを作ったAPIのみ開くためのボタンを追加する
          if self.detail_params[api_id]:

            #詳細ボタン
            detail_button = ttk.Button(
              api_frame,
              text="詳細",
              width=4,
              padding=(1, 1)
            )
            detail_button.grid(row=0, column=1, padx=(5, 0))

            detail_button.bind(
              "<1>",
              lambda event, a_id=api_id, d_name=api_info["display_name"], p=params:
              self.open_detail_window(event, a_id, d_name, p)
            )

            #詳細ボタンを辞書に追加する
            self.detail_buttons[api_id] = detail_button

          #行と列を計算して配置
          row = count_api[i] // 3 + 1
          column = count_api[i] % 3

          #APIごとのフレームを配置
          api_frame.grid(row=row, column=column, pady=(3, 0))

          #配置したapiの数をリストに反映する
          count_api[i] += 1

          break

    print(f"checkbuttons = {self.checkbuttons}")

    #0ページ目を表示する
    self.change_page(0)

  #APIごとに詳細ウィンドウに入れるパラメータのウィジェットを作る
  def create_detail_params(self, api_id, params):

    #APIごとの詳細ウィンドウ内のパラメータの辞書
    detail_params = {}

    #応答方式、z、x、y以外のパラメータの値を辞書に入れる
    for param_name in params.keys():

      if not param_name in geo_params:
        detail_params[param_name] = ""

    #作成した辞書を全体の辞書に入れる
    self.detail_params[api_id] = detail_params

  #APIごとの詳細のウィンドウを開く
  def open_detail_window(self, event, api_id, display_name, params):

    #ボタンのstateを調べる（そのままだとTcl_Obj型なのでstrに変換する）
    state = str(self.detail_buttons[api_id]["state"])

    #ボタンがdisiabledになっているなら何もせず戻る
    if state == "disabled":
      return
    
    #ウィンドウの位置を取得
    x, y = super().get_widget_pos(self.root)

    #ウィンドウのサイズなどの設定
    detail_window = tk.Toplevel(self.root, bg="#d9d9d9")
    detail_window.geometry(f"+{x+100}+{y+200}")
    detail_window.title(display_name)
    detail_window.resizable(width=False, height=False)

    #このウィンドウを閉じるまでルートウィンドウを触れないようにする
    detail_window.grab_set()

    #ウィンドウを閉じる際にパラメータの値を辞書に入れる
    detail_window.protocol(
      "WM_DELETE_WINDOW",
      lambda: self.save_detail_params(detail_window, api_id, params)
    )

    #パラメータごとに名前と入力欄を作る
    for param_name, param_info in params.items():

      #応答方式、z、x、yは作成済みなのでスキップ
      if not param_name in geo_params:

        #すでに値が保存されているならその値を反映する
        if self.detail_params[api_id][param_name] != "":
          initial_value = self.detail_params[api_id][param_name]

        else:
          initial_value = None

        super().create_params_widget(detail_window, param_name, param_info, initial_value)

  #詳細ウィンドウが閉じられる際にパラメータを辞書に入れる
  def save_detail_params(self, detail_window, api_id, params):

    print(f"api_id = {api_id}")

    for param_name, param_info in params.items():

      if not param_name in geo_params:
        self.detail_params[api_id][param_name] = self.widgets[param_name].get()

    print(f"{api_id} = {self.detail_params[api_id]}")

    #ウィンドウを閉じる
    detail_window.destroy()

  #任意のページを表示する
  def change_page(self, open_index):

    #現在のページを非表示にする
    self.pages[self.current_page_index].grid_forget()

    #指定されたページを表示する
    self.pages[open_index].grid(row=1, column=0, sticky="ew")

    #ページ番号を保存する
    self.current_page_index = open_index

  #ダウンロード準備
  def prepare_download(self):

    #複数年ダウンロードの場合
    if self.api_id != "XST001":
      self.prepare_period_download()

    #地理空間情報ダウンロードの場合
    else:
      self.prepare_geo_download()

  #複数年のダウンロード準備
  def prepare_period_download(self):

    #ダウンロードする期間を計算する
    self.period_lst = self.calc_period()

    print(f"period_lst = {self.period_lst}")

    #期間のリストが正常に帰ってこなければ終了
    if self.period_lst == None:
      return
    
    #api.pyに渡すパラメータの辞書を年以外で作る
    params = super().create_params(self.widgets, self.api_info)

    #バリデーションチェック
    is_ok = super().check_validate(params, self.api_id)
    if not is_ok:
      return

    #複数期間のparamsを作る
    bundle_period = self.create_bundle_period()

    print(f"bundle_period = {bundle_period}")

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
    is_ok = super().confirm_overwrite(save_dir, filename, ext_option, is_bundle=True)
    if not is_ok:
      return

    #ダウンロード中のウィンドウを出す
    super().open_downloading_window("determinate")

    #進捗の最大数をカウントする
    super().count_progress(self.period_lst)

    #ダウンロード処理とダウンロード中の表示を別スレッドで行う
    download_thread = threading.Thread(
      target=self.period_download,
      args=(api_key, params, bundle_period, ext_option, is_trans, filename, save_dir)
    )
    download_thread.start()
   
  #ダウンロードする期間を計算する
  def calc_period(self):

    #不動産価格情報の場合四半期がある
    if self.api_id == "XIT001":
      return self.calc_quarter_period()
    else:
      return self.calc_year_period()

  #不動産価格情報の場合、年と四半期の両方をチェックする
  def calc_quarter_period(self):

    #検索する期間のリスト
    period_lst = []

    #取引価格か成約価格かの確認
    index = self.widgets["priceClassification"].current()
    trans_values = self.api_info["params"]["priceClassification"]["options"]
    priceClassification = trans_values[index]

    #取りうる時期の範囲
    scope = self.api_info["validation"]["scope"]
    scope_period = scope["priceClassification"][priceClassification]["year"]

    min_val = self.get_year_num(scope_period[0])
    max_val = self.get_year_num(scope_period[1])

    print(f"scope_period = {min_val} ～ {max_val}")

    #開始年と終了年
    start_year = self.widgets["start_year"].get()
    end_year = self.widgets["end_year"].get()

    if not start_year.isdigit() or not end_year.isdigit():
      super().failed_download("パラメータエラー", "年は整数で入力してください")
      return None

    if not len(start_year) == 4 or not len(end_year) == 4:
      super().failed_download("パラメータエラー", "年は４桁で入力してください")
      return None

    if not (min_val <= int(start_year) <= int(end_year) <= max_val):
      super().failed_download("パラメータエラー", "開始時期と終了時期を指定の範囲に収めてください")
      return None

    #開始年の四半期と終了年の四半期
    start_quarter = self.widgets["start_quarter"].get()
    end_quarter = self.widgets["end_quarter"].get()

    if start_year in scope["year"]:
      quarter = scope["year"][start_year]

      if not int(start_quarter) in quarter:
        super().failed_download("パラメータエラー", "四半期が正しい範囲内か確認してください")
        return None

    if end_year in scope["year"]:
      quarter = scope["year"][end_year]

      if not int(end_quarter) in quarter:
        super().failed_download("パラメータエラー", "四半期が正しい範囲内か確認してください")
        return None

    start_year, end_year = int(start_year), int(end_year)
    start_quarter, end_quarter = int(start_quarter), int(end_quarter)

    #開始時期と終了時期が同じとき
    if (start_year, start_quarter) == (end_year, end_quarter):
      period_lst.append({start_year:[start_quarter]})

    #開始時期より終了時期が後の時
    elif (start_year, start_quarter) < (end_year, end_quarter):

      lst = []

      while not ((start_year, start_quarter) == (end_year, end_quarter)):

        lst.append(start_quarter)
        start_quarter += 1

        if start_quarter == 5:
          period_lst.append({start_year:lst})

          start_year += 1
          start_quarter = 1
          lst = []

      #同じ年の場合は最後の四半期を追加して時期のリストに追加
      if start_year == end_year:
        lst.append(end_quarter)
        period_lst.append({start_year:lst})

      #違う年の場合は次の年の次の四半期を追加して時期のリストに追加
      else:
        start_year += 1
        lst.append(end_quarter)
        period_lst.append({start_year:lst})

    #開始時期より終了時期が前の時
    else:
      super()._download("パラメータエラー", "開始時期は終了時期より前にしてください")
      return None

    #正常終了時はダウンロードするべき時期のリストを返す
    return period_lst

  #鑑定評価情報は年だけチェックする
  def calc_year_period(self):

    #検索する期間のリスト
    period_lst = []

    #取りうる時期の範囲
    min_val = self.get_year_num(self.api_info["params"]["year"]["input_validation"]["min"])
    max_val = self.get_year_num(self.api_info["params"]["year"]["input_validation"]["max"])

    print(f"scope_period = {min_val} ～ {max_val}")

    #開始年と終了年
    start_year = self.widgets["start_year"].get()
    end_year = self.widgets["end_year"].get()

    if not start_year.isdigit() or not end_year.isdigit():
      super().failed_download("パラメータエラー", "年は整数で入力してください")
      return None

    if not len(start_year) == 4 or not len(end_year) == 4:
      super().failed_download("パラメータエラー", "年は４桁で入力してください")
      return None

    if not (min_val <= int(start_year) <= int(end_year) <= max_val):
      super().failed_download("パラメータエラー", "開始時期と終了時期を指定の範囲に収めてください")
      return None

    start_year, end_year = int(start_year), int(end_year)

    #開始時期と終了時期が同じとき
    if start_year == end_year:
      period_lst.append(start_year)

    #開始時期より終了時期が後の時
    elif start_year < end_year:

      while not start_year == end_year:
        period_lst.append(start_year)
        start_year += 1

      period_lst.append(end_year)

    #開始時期より終了時期が前の時
    else:
      super().failed_download("パラメータエラー", "開始時期は終了時期より前にしてください")
      return None

    #正常終了時はダウンロードするべき時期のリストを返す
    return period_lst

  #期間ごとのparamsを作る
  def create_bundle_period(self):

    #期間ごとの年や四半期のリスト
    bundle_period = []

    #期間が年と四半期の組み合わせで渡されたとき
    if isinstance(self.period_lst[0], dict):

      for period in self.period_lst:
        print(f"period = {period}")

        #年と四半期の組み合わせをリストに追加する
        for year, quarters in zip(period.keys(), period.values()):

          if quarters == [1, 2, 3, 4]:
            bundle_period.append([str(year), ""])

          else:
            for i in range(len(quarters)):
              quarters[i] = str(quarters[i])
            bundle_period.append([str(year), quarters])

    #期間が年のみで渡されたとき
    else:
      for year in self.period_lst:
        bundle_period.append(str(year))

    #期間が入ったリストを返す
    return bundle_period

  #ダウンロードの本体処理
  def period_download(self, api_key, params, bundle_period, ext_option, is_trans, filename, save_dir):

    #保存形式に対応したデータをAPIから受け取る
    data = self.bundle_period_download(self.api_id, api_key, params, bundle_period, ext_option)

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

  #複数のAPIから順番にダウンロードする
  def bundle_period_download(self, api_id, api_key, params, bundle_period, ext_option):

    print(f"bundle_period = {bundle_period}")

    #ダウンロードしたデータをdf化して入れるリスト
    data_lst = []

    #bundle_periodの中身が年と四半期の組み合わせの時
    if isinstance(bundle_period[0], list):

      for period in bundle_period:
        year, quarters = period

        #期間ごとのparamsを作る
        tmp_params = params.copy()

        tmp_params["year"] = year

        #四半期がリストで渡されている場合はその回数だけ繰り返す
        if quarters != "":

          for quarter in quarters:
            tmp_params["quarter"] = quarter

            print(f'year, quarters = {year}, {quarters}')
            print(tmp_params)

            #保存形式に対応したデータをAPIから受け取る
            data = api.get_api_data(api_id, api_key, tmp_params, ext_option)

            #レスポンスがエラーかどうかを判定する
            if super().is_response_error(data):
              return

            #エラーでなければリストに追加する
            else:
              data_lst.append(data)

        else:
          tmp_params["quarter"] = ""

          print(f'year, quarters = {year}, {quarters}')
          print(tmp_params)

          #保存形式に対応したデータをAPIから受け取る
          data = api.get_api_data(api_id, api_key, tmp_params, ext_option)


          #レスポンスがエラーかどうかを判定する
          if super().is_response_error(data):
            return

          #エラーでなければリストに追加する
          else:
            data_lst.append(data)

        #プログレスバーを進める
        super().advance_progress()

        print("===========================")

    #bundle_periodの中身が年だけのとき
    else:

      for year in bundle_period:

        #期間ごとのparamsを作る
        tmp_params = params.copy()

        tmp_params["year"] = year

        print(tmp_params)
        print("===========================")

        #保存形式に対応したデータをAPIから受け取る
        data = api.get_api_data(api_id, api_key, tmp_params, ext_option)

        #プログレスバーを進める
        super().advance_progress()

        #レスポンスがエラーかどうかを判定する
        if super().is_response_error(data):
          return

        #エラーでなければリストに追加する
        else:
          data_lst.append(data)

    #作成したデータフレームを結合させる
    new_df = pd.concat(data_lst)

    return new_df

  #地理空間情報ダウンロード
  def prepare_geo_download(self):

    print("geo")

    #選択したAPIの数
    selected_api_count = sum(
      check_var.get() for check_var in self.check_vars.values())

    print(f"selected_api_count = {selected_api_count}")

    if selected_api_count == 0:
      super().failed_download("パラメータエラー", "利用するAPIを選んでください")
      return
    
    #api.pyに渡すパラメータの辞書をgeo_paramsのみで作る
    params = super().create_params(self.widgets, self.api_info)

    #geo_paramsのみのバリデーションチェック
    is_ok = super().check_validate(params, self.api_id)
    if not is_ok:
      return

    #geo_params以外のバリデーションチェック
    for api_id, detail_params in self.detail_params.items():

      #詳細ウィンドウのパラメータがあるものだけバリデーションチェック
      if detail_params:
        is_ok = super().check_validate(
          detail_params, api_id, f"{self.api_ids[api_id]["display_name"]}にエラーがあります。")
        
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
        "ディレクトリエラー", "保存先のフォルダが正しいか確認してください"
      )
      return

    #ファイル名の取得
    filename = self.file_name_entry.get()

    #同名ファイルが存在するかの確認
    is_ok = super().confirm_overwrite(save_dir, filename, ext_option, is_bundle=True)
    if not is_ok:
      return

    #ダウンロード中のウィンドウを出す
    super().open_downloading_window("determinate")

    #進捗の最大数をカウントする
    super().count_progress(selected_api_count)

    #ダウンロード処理とダウンロード中の表示を別スレッドで行う
    download_thread = threading.Thread(
      target=self.geo_download,
      args=(api_key, params, ext_option, is_trans, filename, save_dir)
    )
    download_thread.start()
  
#ダウンロードの本体処理
  def geo_download(self, api_key, params, ext_option, is_trans, filename, save_dir):

    #保存形式に対応したデータをAPIから受け取る
    data = self.bundle_geo_download(api_key, params, ext_option)

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

  #複数のAPIから順番にダウンロードする
  def bundle_geo_download(self, api_key, params, ext_option):

    #API名と対応したデータを入れる辞書
    data_dic = {}

    #チェックボックスにチェックしてあるAPIについて
    for api_id, check_var in self.check_vars.items():

      if check_var.get():
        tmp_params = params.copy()

        #詳細ウィンドウがあるAPIはパラメータを辞書に追加
        if self.detail_params[api_id]:

          for param_name, param_val in self.detail_params[api_id].items():

            tmp_params[param_name] = param_val

        print(f"{api_id}：{self.api_ids[api_id]["name"]}")
        print(f"tmp_params = {tmp_params}")

        #保存形式に対応したデータをAPIから受け取る
        data = api.get_api_data(api_id, api_key, tmp_params, ext_option)

        #プログレスバーを進める
        super().advance_progress()

        #レスポンスがエラーかどうかを判定する
        if super().is_response_error(data):
          return

        #エラーでなければ辞書に追加する
        else:
          data_dic[api_id] = data

    return data_dic
  