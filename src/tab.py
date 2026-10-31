import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import api #APIとの通信
import save_utils #api.pyから受けとったdataを保存するためのもの
import settings #ユーザ設定用のjsonに読み書きするためのもの

#タブごとのクラス作成
class Tab:
  def __init__(self, def_width, def_height, root, api_key, api_catalog, tab_frame):
    self.def_width = def_width
    self.def_height = def_height
    self.root = root
    self.api_key = api_key
    self.api_catalog = api_catalog
    self.tab_frame = tab_frame

    #タブの名前
    self.tab_name = None

    #APIのIDとその中身の辞書
    self.api_ids = self.api_catalog["api_ids"]

    #頻出する組み合わせの辞書
    self.frequent = self.api_catalog["frequent"]

    #パラメータ名とその入力欄やプルダウンのウィジェットの辞書
    self.widgets = {}

    #ダウンロード中のウィンドウ
    self.downloading_window = None

  #マウス位置を取得
  def get_mouse_pos(self, event):
    mouse_x, mouse_y = event.x_root, event.y_root

    print(f"x = {mouse_x}, Y = {mouse_y}")

    return mouse_x, mouse_y

  #ウィジェットの位置を取得
  def get_widget_pos(self, widget):
    x, y = widget.winfo_rootx(), widget.winfo_rooty()
    print(x, y)

    return x, y

  #入力用と保存用のフレームを作る
  def create_frames(self):

    #古い入力欄用フレームがある場合は消す
    if self.input_frame is not None:
      self.input_frame.destroy()

    #古い保存用フレームがある場合は消す
    if self.save_frame is not None:
      self.save_frame.destroy()

    #入力欄用のフレーム
    self.input_frame = ttk.LabelFrame(
      self.tab_frame,
      text="パラメータ",
      width=self.def_width,
      height=380
      )
    self.input_frame.pack_propagate(False) #フレームのサイズの自動更新を防ぐ
    self.input_frame.pack(anchor="w", pady=(10, 0), padx=20)

    #保存用のフレーム
    self.save_frame = ttk.LabelFrame(
      self.tab_frame,
      text="保存設定",
      width=self.def_width, 
      height=135
      )
    self.save_frame.grid_propagate(False) 
    self.save_frame.pack(anchor="w", pady=(10, 5), padx=20)

    #保存用のフレームの行列のサイズ比率の設定
    self.save_frame.columnconfigure(2, minsize=150)

  #使用するAPIに対応した入力欄を作る
  def create_input_frame(self):

    #パラメータ名とその入力欄やプルダウンのウィジェットの辞書
    self.widgets = {}

    #APIごとの保存形式のリスト
    self.ext_options = self.api_info["ext_options"]

    #パラメータごとに、名前と内容の辞書を作る
    for param_name, param_info in self.api_info["params"].items():

      #パラメータにonly_one_sideがある場合は、指定されたタブ以外はスキップ
      if "only_one_side" in param_info:
        if self.tab_name != param_info["only_one_side"]:
          continue

      #パラメータごとのウィジェットを作る
      self.create_params_widget(self.input_frame, param_name, param_info)

    #使用するAPIに対応した保存設定欄を作成する
    self.create_save_frame()

  #パラメータごとに、フレームとラベル、ウィジェットを作る
  def create_params_widget(self, base_frame, param_name, param_info, initial_value=None, widgets=None):

    #パラメータごとに、名前と内容の辞書を受け取る
    #type→選択式か入力式か　val→値　
    #options→選択式の場合はこの中から選ぶ　required→送信必須かどうか

    #パラメータごとのフレーム
    frame = ttk.Frame(base_frame)
    frame.pack(anchor="w", padx=10)

    #パラメータの初期値が関数側で指定されていなければ、param_infoから読み込む
    if initial_value == None:
      initial_value = param_info["initial_value"]

    #ウィジェットを保存する辞書が指定されていなければself.widgetsにする
    if widgets == None:
      widgets = self.widgets

    #必須かどうか
    required = param_info["required"]

    #必須かどうかを明記する
    if required:
      text = f"(必須) {param_info['trans_name']}"

    else:
      #１つは必須かどうかを明記する
      if "validation" in self.api_info and \
        "at_least_one" in self.api_info["validation"]:

        if param_name in self.api_info["validation"]["at_least_one"]:
          text = f"(※１) {param_info['trans_name']}"
        else:
          text = param_info["trans_name"]

      else:
        text = param_info["trans_name"]

    #パラメータ名のラベル
    label = ttk.Label(
      frame,
      text=text
    )
    label.pack(anchor="w")

    #パラメータのプルダウン・入力欄
    #単一選択式のプルダウン
    if param_info["type"] == "select":
      #a~bのように数字選択式の場合
      if len(param_info["options"]) == 2 and \
      type(param_info["options"][0]) == int and \
      type(param_info["options"][1]) == int:
        a, b = param_info["options"][0], param_info["options"][1]
        tmp_values = list(range(a, b+1))
        
        combobox = ttk.Combobox(
          frame,
          values=tmp_values,
          width=30,
          state="readonly"
        )

      #他の単一選択式はあえて日本語の値を選択できるようにする
      else:
        combobox = ttk.Combobox(
                  frame,
                  values=param_info["trans_values"], #ここで日本語の値を入れる
                  width=30,
                  state="readonly"
        )

      combobox.set(initial_value) #comboboxはsetで初期値を決める
      combobox.pack(anchor="w", side="left", pady=(0,7))

      widgets[param_name] = combobox

    #複数選択式の入力欄
    elif param_info["type"] == "multiple":
      entry = ttk.Entry(
        frame,
        width=27,
      )

      entry.insert(0, initial_value) #entryはinsertで初期値を決める
      entry.config(state="readonly")
      entry.pack(anchor="w", side="left", pady=(0,7))

      widgets[param_name] = entry

      #複数選択用のウィンドウを開くボタン
      button = ttk.Button(
        frame,
        text="選択",
        width=4,
        padding=(1, 1)
      )
      button.pack(anchor="w", side="left", pady=(0,7))

      button.bind(
        "<1>",
        lambda event, b=base_frame, p=param_info, e=entry, r=required:
        self.open_multiple_window(event, b, p, e, r)
      )

    #入力式の入力欄
    elif param_info["type"] == "input":
      entry = ttk.Entry(
        frame,
        width=32
      )

      entry.insert(0, initial_value) #entryはinsertで初期値を決める
      entry.pack(anchor="w", side="left", pady=(0,7))

      widgets[param_name] = entry

    #パラメータごとの入力説明
    rule_label = ttk.Label(
      frame,
      text=param_info["rule"]
    )
    rule_label.pack(anchor="w", side="left", padx=20)
    
    print(f'param_name = {param_name}')
    print(f'param_info = {param_info}')

    print(f'widgets = {self.widgets}')

  #使用するAPIに対応した保存設定欄を作成する
  def create_save_frame(self):

    #保存形式のラベル
    ext_options_label = ttk.Label(
      self.save_frame,
      text="保存形式"
    )
    ext_options_label.grid(row=0, column=0, padx=(10, 0), sticky="nw")

    #保存形式のプルダウン
    self.ext_options_combobox = ttk.Combobox(
      self.save_frame,
      values=self.ext_options["ext_names"],
      width=25,
      state="readonly"
    )
    self.ext_options_combobox.current(0)
    self.ext_options_combobox.grid(row=0, column=1, padx=(10, 0), sticky="nw")

    if "response_format" in self.widgets: #geojsonやpbfの場合
      self.ext_options_combobox.config(state="disabled")
      self.widgets["response_format"].bind(
        "<<ComboboxSelected>>",
        lambda event: self.fix_ext_option(event)
      )
    else: #csvやjsonの場合
      self.ext_options_combobox.bind(
      "<<ComboboxSelected>>",
      lambda event: self.hide_checkbutton(event)
    )

    #チェックボックスの状態を管理する変数
    self.save_check_var = tk.BooleanVar(value=True)

    #CSVの見出しを翻訳するか確認するチェックボックス
    self.is_trans_checkbutton = ttk.Checkbutton(
      self.save_frame,
      text="CSVの1行目を日本語化",
      variable=self.save_check_var,
      onvalue=True,
      offvalue=False
    )
    if self.ext_options["ext_names"][0] == "CSV":
      self.is_trans_checkbutton.grid(row=0, column=2, sticky="nw")

    #保存ファイル名のラベル
    file_name_label = ttk.Label(
      self.save_frame,
      text="ファイル名"
    )
    file_name_label.grid(row=2, column=0, padx=(10, 0), pady=(10, 0), sticky="nw")

    #保存ファイル名の入力欄
    self.file_name_entry = ttk.Entry(
      self.save_frame,
      width=50
    )
    self.file_name_entry.insert(0, "data")
    self.file_name_entry.grid(row=2, column=1, padx=(10, 0), pady=(10, 0), sticky="w")

    #保存先のラベル
    save_label = ttk.Label(
      self.save_frame,
      text="保存先"
    )
    save_label.grid(row=3, column=0, padx=(10, 0), pady=(10, 0), sticky="nw")

    #保存先の入力欄
    self.save_entry = ttk.Entry(
      self.save_frame,
      width=50,
    )
    self.save_entry.insert(0, settings.get_from_settings("save_dir"))
    self.save_entry.config(state="readonly")
    self.save_entry.grid(row=3, column=1, padx=(10, 0), pady=(10, 0), sticky="nw")

    #保存先を参照できるようにするボタン
    save_button = ttk.Button(
      self.save_frame,
      text="参照",
      command=lambda: self.select_save_directory()
    )

    save_button.grid(row=3, column=2, padx=(10, 0), pady=(10, 0), sticky="nw")

    #ダウンロードボタン
    download_button = ttk.Button(
      self.save_frame,
      text="ダウンロード",
      command=lambda: self.prepare_download()
    )
    download_button.grid(row=3, column=3, padx=(30, 0), pady=(10, 0), sticky="nw")

  #複数選択用のウィンドウを開く
  def open_multiple_window(self, event, base_frame, param_info, entry, required):
    print(f"param_info = {param_info}")

    #ウィンドウを開くときのマウス位置の取得
    self.mouse_x, self.mouse_y = self.get_mouse_pos(event)

    #ウィンドウ作成＆サイズなどの設定
    multiple_window = tk.Toplevel(self.root, bg="#d9d9d9")
    multiple_window.geometry(f"+{self.mouse_x}+{self.mouse_y}")
    multiple_window.title(param_info["trans_name"])
    multiple_window.resizable(width=False, height=False)

    #このウィンドウを閉じるまでルートウィンドウを触れないようにする
    multiple_window.grab_set()

    print(f"base_frameの型は{type(base_frame)}")

    #bundle_tabのほうの詳細ウィンドウから呼び出されたとき限定の処理
    if isinstance(base_frame, tk.Toplevel):
      multiple_window.protocol(
        "WM_DELETE_WINDOW",
        lambda b=base_frame, m=multiple_window: keep_grab_set(b, m)
      )

      #複数選択用のウィンドウを閉じたあとに詳細ウィンドウのgrab_setを再び行う
      def keep_grab_set(base_frame, multiple_window):
        multiple_window.destroy()
        base_frame.grab_set()

    #選択肢の値とその翻訳、表示される最大列数
    options = param_info["options"]
    if isinstance(options, str):
        options = self.frequent[options]["options"]

    trans_values = param_info["trans_values"]
    if isinstance(trans_values, str):
        trans_values = self.frequent[trans_values]["trans_values"]

    multiple_columns = param_info["multiple_columns"]
    if isinstance(multiple_columns, str):
      multiple_columns = self.frequent[multiple_columns]["multiple_columns"]

    #選択上限がある場合はそれを取得する
    if "selection_limit" in param_info:
      selection_limit = param_info["selection_limit"]
      if isinstance(selection_limit, str):
        selection_limit = self.frequent[selection_limit]["selection_limit"]

    #選択上限がないときはとりあえず大きい数にしておく（引っかからないように）
    else:
      selection_limit = 10000

    #選択されている(trueの)チェックボックスの数
    selection_count = 0

    #チェックボックスの有効・無効の反映
    def update_checkbuttons():

      for option, checkbutton in checkbuttons.items():

        #選択済みの場合は触れる状態に
        if check_vars[option].get():
          checkbutton.config(state="normal")

        #選択済みでない場合、上限に達していなければ触れる
        elif selection_count < selection_limit:
          checkbutton.config(state="normal")

        #選択済みでないうえ上限に達していれば触れない
        else:
          checkbutton.config(state="disabled")

    #チェックボックスのtrueの増減を感知する
    def count_checkbutton(option):
      nonlocal selection_count #再代入するならnonlocalが必要

      #チェックボックスがtrueなら+1、falseなら-1
      if check_vars[option].get():
        selection_count += 1
        
      else:
        selection_count -= 1

      #チェックボックスの有効・無効の反映
      update_checkbuttons()

    #入力欄の中身がある場合それをチェックボックスに反映する
    previous_selections = (entry.get()).split(",")

    print(f"以前の複数選択 = {previous_selections}")

    #チェックボックスのウィジェットそのものが入った辞書
    checkbuttons = {}

    #チェックボックスのウィジェット変数の入った辞書
    check_vars = {}

    #パラメータごとにチェックボックスを作る
    for i, (option, trans_value) in enumerate(zip(options, trans_values)):

      #以前選択したものはTrue、そうでないものはFalseが初期値
      if option in previous_selections:
        check_var = tk.BooleanVar(value=True)

      else:
        check_var = tk.BooleanVar(value=False)

      check_var.trace_add(
        "write", 
        callback=lambda *args, opt=option: count_checkbutton(opt)
      ) #trace_addが関数にデフォルトで渡すvar_name, index, modeを*argsに入れる

      checkbutton = ttk.Checkbutton(
        multiple_window,
        text=trans_value,
        variable=check_var
      )

      #行と列を計算して配置
      row = i // multiple_columns
      column = i % multiple_columns

      checkbutton.grid(row=row, column=column, pady=(3, 0), padx=(5, 0))

      #チェックボックスとそれを管理するウィジェット変数をそれぞれ辞書に入れる
      checkbuttons[option] = checkbutton
      check_vars[option] = check_var

    #チェックボックスすべてをカウントし、有効・無効を反映する
    selection_count = sum(check_vars[option].get() for option in check_vars.keys())
    update_checkbuttons()

    #選択上限がない場合は、全選択ボタンを作る
    if selection_limit == 10000:
      select_all_button = ttk.Button(
        multiple_window,
        text="全選択",
        command=lambda: select_all()
      )

      select_all_button.grid(row=row+1, column=multiple_columns//2, pady=10)

      #全選択ボタンの機能
      def select_all():
        nonlocal check_vars, checkbuttons

        print(checkbuttons)

        #今全選択されているかどうかを確認する
        is_select_all = True

        for check_var in check_vars.values():

          #1つでもtrueでなかった場合
          if not check_var.get():
            is_select_all = False
            break

        #今全選択されていない場合
        if not is_select_all:
          for check_var in check_vars.values():
            check_var.set(True)

        #今全選択されている場合
        else:
          for check_var in check_vars.values():
            check_var.set(False)
          
    #選択した項目の保存ボタン
    save_button = ttk.Button(
      multiple_window,
      text="保存",
      command=lambda: self.set_multiple_entry(multiple_window, base_frame, check_vars, entry, required)
    )

    if selection_limit == 10000:
      save_button.grid(row=row+2, column=multiple_columns//2, pady=10)

    else:
      save_button.grid(row=row+1, column=multiple_columns//2, pady=10)

  #選択したものを入力欄に反映する
  def set_multiple_entry(self, multiple_window, base_frame, check_vars, entry, required):

    #デフォルトの値
    default_option = entry.get()

    #入力欄に書き込めるようにして内容削除
    entry.config(state="normal")
    entry.delete(0, tk.END)

    #選択した値の入ったリスト
    selected_values = []

    for option, check_var in check_vars.items():
      if check_var.get():
        selected_values.append(option)

    #何も選択しなかったら場合
    if not selected_values:

      #必須項目なら一番最初の項目を入れる
      if required:
        entry.insert(0, default_option)

      else:
        entry.insert(0, "")

    #1つでも選択していたら入力欄に挿入する
    else:
      entry.insert(0, ",".join(selected_values))

    entry.config(state="readonly")

    #ウィンドウを閉じる
    multiple_window.destroy()

    if isinstance(base_frame, tk.Toplevel):
      base_frame.grab_set()

  #フォーマット形式を設定するパラメータがあった場合、プルダウンを固定する
  def fix_ext_option(self, event):

    #フォーマット形式がウィジェット側で設定されているか確かめる
    ext_option = self.widgets["response_format"].get()

    if ext_option in ["GeoJSON", "PBF（バイナリベクトルタイル）"]:
      #書き込めるように
      self.ext_options_combobox.config(state="normal")

      #保存形式のプルダウンのほうに反映
      self.ext_options_combobox.set(ext_option)

      print(f"ext_option = {ext_option}")

      #書き込めないように戻す
      self.ext_options_combobox.config(state="disabled")

  #CSV以外の時にチェックボックスを隠す
  def hide_checkbutton(self, event):
    ext_option = self.ext_options_combobox.get()

    if ext_option != "CSV":
      self.is_trans_checkbutton.grid_forget()
    else:
      self.is_trans_checkbutton.grid(row=0, column=2, sticky="nw")
      
  #保存先のディレクトリを参照する
  def select_save_directory(self):
    directory = filedialog.askdirectory()

    #保存先のディレクトリを選択した後
    if directory:

      #入力欄に反映する
      self.save_entry.config(state="normal")
      self.save_entry.delete(0, tk.END)
      self.save_entry.insert(0, directory)
      self.save_entry.config(state="readonly")

      #settings.jsonに保存する
      settings.save_to_settings("save_dir", directory)

  #ダウンロード中の表示をするウィンドウを作る
  def create_downloading_window(self, mode):

    #ルートウィンドウの位置を取得
    x, y = self.root.winfo_x(), self.root.winfo_y()

    #ダウンロード中のウィンドウ
    self.downloading_window = tk.Toplevel(self.tab_frame, bg="#d9d9d9")
    self.downloading_window.geometry(f"400x200+{x+200}+{y+100}")
    self.downloading_window.title("")
    self.downloading_window.resizable(width=False, height=False)
    self.downloading_window.attributes("-topmost", True)

    # #ダウンロード途中でダウンロードウィンドウを閉じたときの処理
    # self.downloading_window.protocol(
    #   "WM_DELETE_WINDOW",
    #   lambda: self.destroy_downloading_window()
    # )

    #ダウンロード途中はダウンロードウィンドウを閉じないように
    self.downloading_window.protocol(
      "WM_DELETE_WINDOW",
      lambda: "break"
    )

    #ダウンロード中のラベル
    downloading_label = ttk.Label(
      self.downloading_window,
      text="ダウンロード中"
    )
    downloading_label.pack()

    #プログレスバー（非確定）
    if mode == "indeterminate":
      self.progressbar = ttk.Progressbar(
        self.downloading_window,
        length=200,
        maximum=100,
        mode=mode #indeterminate…非確定 determinate…確定
      )
      self.progressbar.pack()
      self.progressbar.start(interval=10)

      #現在の進捗のラベル
      self.progress_label = ttk.Label(
        self.downloading_window,
        text="ダウンロード中"
      )
      self.progress_label.pack()

    #プログレスバー（確定）
    elif mode == "determinate":
      self.progressbar = ttk.Progressbar(
        self.downloading_window,
        length=200,
        maximum=1,
        value=0,
        mode=mode
      )
      self.progressbar.pack()

      #現在の進捗のラベル
      self.progress_label = ttk.Label(
        self.downloading_window
      )
      self.progress_label.pack()

  # #ダウンロード途中でダウンロードウィンドウを閉じたときの処理
  # def destroy_downloading_window(self):

  #   #destoryしてから変数のほうもNoneにする
  #   self.downloading_window.destroy()
  #   self.downloading_window = None

  #進捗の最大数をカウントする
  def count_progress(self, progress_data):

    #現在の進捗
    self.progress = 0

    #進捗の最大数
    self.max_progress = 0

    #リストだった場合
    if isinstance(progress_data, list):

      #リストの中身がリスト（年と四半期）だった場合
      if isinstance(progress_data[0], list):
        for period in progress_data:

          #通年だった場合
          if period[1] == "":
            self.max_progress += 1

          else:
            self.max_progress += len(period[1])

      #リストの中身が年のみだった場合
      else:
        self.max_progress = len(progress_data)

    #数字だった場合
    else:
      self.max_progress = progress_data

    #進捗のラベルの更新
    self.progress_label.config(text=f"{self.progress} / {self.max_progress}")

  #複数ダウンロードの場合、進捗を画面に反映する
  def advance_progress(self):

    #現在の進捗を進める
    self.progress += 1

    #プログレスバーの表示変更
    self.progressbar.configure(value=(self.progress)/self.max_progress)
    self.progressbar.update()

    #進捗のラベルの更新
    if self.progress != self.max_progress:
      self.progress_label.config(text=f"{self.progress} / {self.max_progress}")
    else:
      self.progress_label.config(text="ダウンロード完了")


  #ダウンロード中のウィンドウを開く
  def open_downloading_window(self, mode):

    #ダウンロード中のウィンドウがすでにある場合
    if self.downloading_window != None:

      #非表示にしていたウィンドウを表示する
      self.downloading_window.deiconify()

    #ない場合は作る
    else:
      self.create_downloading_window(mode)

    #プログレスバーを動かす
    self.progressbar.start(10)

  #ダウンロード成功時の処理
  def succeeded_download(self, filename):

    #ダウンロード中のウィンドウを消す
    self.downloading_window.destroy()
    self.downloading_window = None

    #成功メッセージを出す
    messagebox.showinfo(
      title="ダウンロード成功",
      message=f"{filename}という名前で保存しました"
    )

  #ダウンロード失敗時の処理
  def failed_download(self, title, message):

    #ダウンロード中のウィンドウがある場合は消す
    if self.downloading_window != None:
      self.downloading_window.destroy()
      self.downloading_window = None

    #失敗理由のメッセージを出す
    messagebox.showerror(
      title=title,
      message=message
    )

  #api.pyに渡すパラメータの辞書を作る
  def create_params(self, widgets, api_info):

    #パラメータの辞書
    params = {}

    for param_name, widget in widgets.items():

      #ウィジェットのパラメータ名がapi_infoになければスキップ
      if not param_name in api_info["params"]:
        continue

      #パラメータごとの情報を取り出す
      param_info = api_info["params"][param_name]

      #選択式について
      if param_info["type"] == "select":

        #表示が日本語化されているなら対応する値に戻す
        if "trans_values" in param_info:
          display_val = widget.get()
          display_index = param_info["trans_values"].index(display_val)
          params[param_name] = param_info["options"][display_index]

        #日本語化されていないならそのまま辞書に入れる
        else:
          params[param_name] = widget.get()

      #入力式はそのまま辞書に入れる
      else:
        params[param_name] = widget.get()

    print(f"params = {params}")

    return params

  #年を数字に変換する
  def get_year_num(self, element):

    #長さ3のリストの場合
    if type(element) == list:
      if element[0] == "this_year":
        num = self.dt.year
      else:
        num = int(element[0])

      if element[1] == "+":
        num += int(element[2])

      elif element[1] == "-":
        num -= int(element[2])

    #長さ1の文字の場合
    if type(element) is str :
      if not element.isdigit():
        if element == "this_year":
          num = self.dt.year

      else:
        num = int(element)

    #整数ならそのまま返す
    if type(element) is int:
      num = element

    return num

  #バリデーションチェック
  def check_validate(self, params, api_id, add_message=None):

    #api_idに対応するAPIの辞書を取得する
    api_info = self.api_ids[api_id]

    invalid_params = self.validate_params(params, api_info)
    if invalid_params:
      print("バリデーションに引っかかった")
      print(f"invalid_params = {invalid_params}")

      #バリエーデーションに引っかかった項目を表示する
      message = f"以下の{len(invalid_params)}個のパラメータを確認してください\n"

      #追加のメッセージがあるなら先に表示する
      if add_message:
        message = f"{add_message}\n{message}"

      for invalid_param in invalid_params:
        message += f"・{api_info["params"][invalid_param]["trans_name"]}\n"

      #エラーならFalseを返す
      self.failed_download("パラメータエラー", message)
      return False

    #エラー出なければTrueを返す
    else:
      return True

#入力されたパラメータの範囲がOKかを検証する
  def validate_params(self, params, api_info):

    #間違っているパラメータの名前の集合
    invalid_params = set()

    #input型のパラメータごとのバリデーションが正しいかどうか調べる
    for param_name, param_info in api_info["params"].items():

      print(f"param_name = {param_name}")
      print(f"param_info = {param_info}")

      #パラメータがparamsになければスキップ
      if not param_name in params:
        continue

      print(f"データ = {params[param_name]}")

      #input型以外はスキップ
      if param_info["type"] != "input":
        continue

      #空欄が許されているならスキップ
      if not param_info["required"] and params[param_name] == "":
        continue

      #バリデーションの辞書があれば受け取り、なければスキップ
      if not "input_validation" in param_info:
        continue
      else:
        input_validation = param_info["input_validation"]

      #入力型が指定されているなら調べる
      if "data_type" in input_validation:

        if input_validation["data_type"] == "int" :
          if not params[param_name].isdigit():
            invalid_params.add(param_name)
            continue #すぐ下でValueErrorが起きるのを防ぐ
        
      #入力桁数が決まっている場合、あっているか確かめる
      if "digits" in input_validation:
        if len(params[param_name]) != input_validation["digits"]:
          invalid_params.add(param_name)

      #大小関係が決まっている場合、比較する
      if "min" in input_validation:
        min_val = self.get_year_num(input_validation["min"])

        if not (min_val <= int(params[param_name])):
          invalid_params.add(param_name)
          continue

      if "max" in input_validation:
        max_val = self.get_year_num(input_validation["max"])

        if not (int(params[param_name]) <= max_val):
          invalid_params.add(param_name)
          continue

    #複数項目についてのバリデーションの条件の辞書を作る
    validation = self.api_info.get("validation", {})
    print(f"validation = {validation}")

    #少なくとも1つは選択する
    at_least_one = validation.get("at_least_one", [])

    is_ok = False

    if at_least_one:
      for param_name in at_least_one:
        if params[param_name] != "":
          is_ok = True
          break

    if not is_ok:
      for param_name in at_least_one:
        invalid_params.add(param_name)

    #入力範囲
    scope = validation.get("scope", {})

    #親パラメータごとに見る
    if scope:
      for parent_param, parent_values in scope.items():

        #親パラメータがparamsになければスキップ
        if not parent_param in params:
          continue

        #親パラメータの入力値
        parent_val = params[parent_param]

        #親パラメータの入力値に対する条件
        if parent_val in parent_values:
          conditions = parent_values[parent_val]

          print(f"parent_param = {parent_param}")
          print(f"parent_values = {parent_values}")
          print(f"parent_val = {parent_val}")
          print(f"conditions = {conditions}")

          #パラメータの名前と取りうる値
          for param_name, scope_range in conditions.items():

            #パラメータがparamsになければスキップ
            if not param_name in params:
              continue

            #パラメータの入力値
            try:
              param_val = int(params[param_name])

            except ValueError:
              invalid_params.add(param_name)
              continue

            #a以上という範囲指定の場合
            if len(scope_range) == 1:
              min_val = self.get_year_num(scope_range[0])

              if not min_val <= param_val:
                invalid_params.add(param_name)
                continue

            #a以上b以下という範囲指定の場合
            elif len(scope_range) == 2:
              min_val = self.get_year_num(scope_range[0])
              max_val = self.get_year_num(scope_range[1])

              if not (min_val <= param_val <= max_val):
                invalid_params.add(param_name)
                continue

    #バリデーションに引っかかったパラメータ名のリストを返す
    return invalid_params

  #保存形式周りの処理
  def get_ext_options(self):

    #保存形式を取得
    ext_name = self.ext_options_combobox.get()
    ext_index = self.ext_options["ext_names"].index(ext_name)
    ext_option = self.ext_options["ext_val"][ext_index]
    print(f'ext_option = {ext_option}')

    #csv保存の時、１行目を日本語にするかチェック
    if ext_option == ".csv":
      is_trans = self.save_check_var.get()
    else:
      is_trans = False

    return ext_option, is_trans

  #レスポンスがエラーかどうかを判定する
  def is_response_error(self, data):

    #エラーメッセージを受け取った場合はメッセージボックスで表示
    if type(data) == str:
      self.root.after(
        0,
        self.failed_download,
        "パラメータエラー", #afterで渡す引数は１つずつカンマで区切る
        f"{data}"
      )

      #エラーならTrueを返す
      return True

    #エラーでないならFalseを返す
    else:
      return False

  #同名ファイルが存在する場合の確認を表示する
  def confirm_overwrite(self, save_dir, filename, ext_option, is_bundle=False):

    #同名ファイルが存在する場合
    if save_utils.is_dupulicate_file(save_dir, filename, ext_option, is_bundle):

      #ウィンドウの位置を取得
      x, y = self.get_widget_pos(self.root)

      #ウィンドウのサイズなどの設定
      confirm_window = tk.Toplevel(self.root, bg="#d9d9d9")
      confirm_window.geometry(f"400x130+{x+200}+{y+100}")
      confirm_window.title("同名ファイルの上書き保存")
      confirm_window.resizable(width=False, height=False)

      #このウィンドウを閉じるまでルートウィンドウを触れないようにする
      confirm_window.grab_set()

      #ウィンドウをxで閉じられないように
      confirm_window.protocol(
        "WM_DELETE_WINDOW",
        lambda: "break"
      )

      #フレーム
      confirm_frame = ttk.Frame(confirm_window)
      confirm_frame.pack()

      #確認文のラベル
      message_label = ttk.Label(
        confirm_frame,
        text="同名のファイルがすでに存在します。上書きしてもよろしいですか？"
      )
      message_label.pack(pady=20, padx=10)

      #上書きするかどうか
      is_overwrite = None

      def ask(ans):
        nonlocal is_overwrite
  
        confirm_window.destroy()

        if ans == "yes":
          is_overwrite = True

        else:
          is_overwrite = False

      #はいのボタン
      yes_button = ttk.Button(
        confirm_frame,
        text="はい",
        command=lambda ans="yes": ask(ans)
      )
      yes_button.pack(anchor="w", side="left", pady=20, padx=(30, 0))

      #いいえのボタン
      no_button = ttk.Button(
        confirm_frame,
        text="いいえ",
        command=lambda ans="no": ask(ans)
      )
      no_button.pack(anchor="w", side="right", pady=20, padx=(0, 30))

      #確認のウィンドウを出すまでルートウィンドウを止める
      self.root.wait_window(confirm_window)

      #上書き保存するかどうかを返す
      return is_overwrite

    else:
      return True
