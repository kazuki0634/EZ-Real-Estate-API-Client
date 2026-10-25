import json
import tkinter as tk
from tkinter import ttk
from tkinter import font
from PIL import Image, ImageTk
import webbrowser


import mystyle  #tkinterのスタイル設定
import paths    #頻出するパスをここから得る
import settings #ユーザ設定用のjsonに読み書きするためのもの
from individual_tab import IndividualTab #個別ダウンロード用タブのクラス
from bundle_tab import BundleTab #複数ダウンロード用タブのクラス

#定数
#横幅と高さのデフォルト値
def_width, def_height = 850, 650

#main関数から呼ぶ
def run():
  application = Application()

#アプリケーション全体のクラス
class Application:
  def __init__(self):

    #ルートウィンドウの作成
    self.root = self.create_root()

    #スタイルの作成
    style = mystyle.create_style()
    style.theme_use("default")

    #マウス位置
    self.mouse_x = None
    self.mouse_y = None

    #APIキーの自動取得
    self.api_key = tk.StringVar(
      value=settings.get_from_settings("api_key")
    )

    #api_catalogの読み込み
    self.api_catalog = self.load_json(paths.API_CATALOG_FILE)

    #初回起動時の保存先ディレクトリの設定
    self.initialize_save_directory()

    #メニューの作成
    self.create_menu()

    #入力用フレーム、ヘルプフレームの作成
    self.create_root_frames()

    #常時画面に出す
    self.root.mainloop()

  #jsonファイルを読み込む
  def load_json(self, file_dir):

    #ファイルを開く
    with open(file_dir, "r", encoding="utf-8") as f:
      loaded_file = json.load(f)

    return loaded_file

  #保存先ディレクトリがない場合は設定する
  def initialize_save_directory(self):

    #現在の保存先ディレクトリを取得
    save_dir = settings.get_from_settings("save_dir")

    if not save_dir:
      save_dir = str(paths.ROOT_DIR.resolve())

      settings.save_to_settings("save_dir", save_dir)

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

  #ルートウィンドウを作成して渡す
  def create_root(self):

    #ルートウィンドウの作成
    root = tk.Tk()
    root.config(bg="#D9D9D9", padx=10, pady=10)
    root.geometry(f"{def_width}x{def_height}") #サイズ調整
    root.title("EZ Real Estate API Client") #タイトル表示
    root.resizable(width=False, height=False) #一旦画面サイズ固定で

    #プルダウンの上でマウスホイールが動いても値を変えないようにする
    #（マウスホイールイベントが起こったときに、"break"で停止させる）
    # root.bind_class("TCombobox", "<MouseWheel>", lambda event: "break")

    #サブウィンドウもここで変数名だけ作っておく
    self.api_key_window = None
    self.links_window = None

    return root

  #メニューの作成
  def create_menu(self):
    #メニューの作成
    self.menu = tk.Menu(
      self.root
      )
    self.root.config(menu=self.menu)

    ##APIキー設定
    self.menu.add_command(
      label="APIキー認証",
      command=lambda: self.open_api_key_window()
    )

    ##リンク集
    #linksの読み込み
    self.links = self.load_json(paths.LINKS_FILE)
    self.link_font = font.Font(size=10, underline=True)
    self.menu.add_command(
      label="リンク集",
      command=lambda: self.open_links_window()
    )

    ##入力用画面への遷移
    self.menu.add_command(
      label="API利用",
      command=lambda frame="content_frame": self.switch_frame(frame)
    )

    ##ヘルプ画面への遷移
    self.menu.add_command(
      label="ヘルプ",
      command=lambda frame="helps_frame": self.switch_frame(frame)
    )
      
  #入力用とヘルプのフレーム切り替え
  def switch_frame(self, frame):
    print(f"{frame}を表示")

    if frame == "content_frame":
      self.helps_frame.pack_forget()
      self.content_frame.pack(anchor="w")

    elif frame == "helps_frame":
      self.content_frame.pack_forget()
      self.helps_frame.pack(anchor="w")

  #×を押して消したウィンドウをNoneにして新しく作れるようにする
  def delete_window(self, attr_name):

    #属性名からウィジェットそのものを探し出す
    widget = getattr(self, attr_name)

    #ウィジェットを消す
    widget.destroy()

    #ウィジェットに対応する属性をNoneにする
    setattr(self, attr_name, None)

  #APIキー設定画面
  def open_api_key_window(self):

    #すでに開いている場合は開かない
    if self.api_key_window is not None:
      return

    #メニューの位置を取得
    x, y = self.get_widget_pos(self.root)

    #サブウィンドウの作成
    self.api_key_window = tk.Toplevel(self.root, bg="#d9d9d9") 
    self.api_key_window.geometry(f"400x200+{x}+{y}") 
    self.api_key_window.title("APIキー認証") 
    self.api_key_window.resizable(width=False, height=False) #Falseでリサイズを防ぐ
    self.api_key_window.attributes("-topmost", True) #常に手前

    #×を押して消した場合に新しいウィンドウが作れるようにする
    self.api_key_window.protocol(
      "WM_DELETE_WINDOW",
      lambda: self.delete_window("api_key_window") #属性名にselfは要らない
    ) 

    #APIキー
    api_key_label = ttk.Label(
      self.api_key_window,
      text="APIキーを入力してください"
      )
    api_key_label.pack(pady=(30, 5))

    #入力欄
    self.api_key_entry = ttk.Entry( #変数名をつけることで呼び出せるようになる
      self.api_key_window,
      width=40,
      textvariable=self.api_key
    )
    self.api_key_entry.pack()

    #保存ボタン
    api_key_entry_button = ttk.Button(
      self.api_key_window,
      text="保存",
      command=lambda: self.save_api_key()
    )
    api_key_entry_button.pack(pady=20)

  #APIキーの取得→保存→ウィンドウ縮小を行う
  def save_api_key(self):
    new_api_key = self.api_key_entry.get() #getメソッドでAPIキーの取得

    settings.save_to_settings("api_key", new_api_key) #新しいAPIキーをsettings.pyに渡す

    self.api_key.set(new_api_key) #新しいAPIキーをwidget変数のapi_keyにも反映する

    self.delete_window("api_key_window") #APIキー設定画面を閉じる

  #都道府県コードなどのリンク集のウィンドウを開く
  def open_links_window(self):

    #すでに開いている場合は開かない
    if self.links_window is not None:
      return

    #メニューの位置を取得
    x, y = self.get_widget_pos(self.root)

    #サブウィンドウの作成
    self.links_window = tk.Toplevel(self.root, bg="#d9d9d9")
    self.links_window.title("リンク集（左クリックでリンクが開きます）")
    self.links_window.resizable(width=False, height=False)
    self.links_window.attributes("-topmost", True)

    #×を押して消した場合のみ新しいウィンドウが作れるようにする
    self.links_window.protocol(
      "WM_DELETE_WINDOW",
      lambda: self.delete_window("links_window")) #属性名にselfは要らない

    #リンクの数だけウィンドウを伸ばす
    self.links_window.geometry(f"400x{26*len(self.links["links_window"])}+{x}+{y}")

    for title, url in self.links["links_window"]:

      #リンクのラベル
      link_label = ttk.Label(
        self.links_window,
        text=f"・{title}",
        font=self.link_font,
        foreground="#0000EE",
        background="#d9d9d9",
      )
      link_label.bind(
        "<1>",
        lambda event,
        u=url: self.label_click(event, u))
      link_label.pack(anchor="nw", pady=(0, 10))

  #リンクのラベルをクリックしたときにサイトを開く
  def label_click(self, event, url):
    webbrowser.open(url)

  #入力画面の作成
  def create_root_frames(self):

    #入力フレーム作成
    self.content_frame = ttk.Frame(
      self.root, 
      width=def_width, 
      height=def_height
      )
    self.content_frame.pack_propagate(False) #子フレームのサイズをこれに固定
    self.content_frame.pack(anchor="w")

    #作成した入力フレームにタブを作成
    self.create_Notebooks()

    #ヘルプフレーム
    self.helps_frame = ttk.Frame(
      self.root, 
      width=def_width, 
      height=def_height
      )
    self.helps_frame.pack_propagate(False) #子フレームのサイズをこれに固定

    #ヘルプの内容を書く
    self.describe_helps()

  #タブの作成
  def create_Notebooks(self):
    notebook = ttk.Notebook(
      self.content_frame,
      width=def_width, 
      height=def_height
      )

    #タブごとの基礎フレーム作成
    individual_frame = tk.Frame( #bg設定のためtkの方
      notebook, 
      background="#D9D9D9"
      )
    
    bundle_frame = tk.Frame(
      notebook, 
      background="#D9D9D9"
      )

    #タブに基礎フレームを設定する
    notebook.add(individual_frame, text="個別ダウンロード")
    notebook.add(bundle_frame, text="複数ダウンロード")

    #タブの配置
    notebook.pack(anchor="nw")

    #タブごとの入力フレーム作成とクラス作成
    #個別ダウンロードタブ
    individual_input_frame = ttk.Frame(individual_frame)
    individual_input_frame.pack(anchor="nw")

    individual_tab = IndividualTab(def_width, def_height, self.root, self.api_key, self.api_catalog, individual_input_frame)

    individual_tab.create_choose_api()

    #複数ダウンロードタブ
    bundle_input_frame = ttk.Frame(bundle_frame)
    bundle_input_frame.pack(anchor="nw")

    bundle_tab = BundleTab(def_width, def_height, self.root, self.api_key, self.api_catalog, bundle_input_frame)

    bundle_tab.create_choose_usage()

  #ヘルプを書く
  def describe_helps(self):

    #メニュー用ツリーのフレーム
    tree_frame = ttk.Frame(self.helps_frame)
    tree_frame.pack(anchor="nw",side="left")

    #ツリーと本文の区切り
    separator = ttk.Separator(
      self.helps_frame,
      orient="vertical",
    )
    separator.pack(fill="both", side="left", padx=5)

    #本文用フレーム
    content_frame = ttk.Frame(self.helps_frame)
    content_frame.pack(anchor="nw", side="left", padx=10)

    #目次のラベル
    table_label = ttk.Label(
      tree_frame,
      text="目次"
    )
    table_label.pack()

    #メニュー用のツリー
    self.tree = ttk.Treeview(tree_frame)
    self.tree.pack(side="left")

    #列の追加
    self.tree["columns"] = ("title")

    #列の設定
    self.tree.column("#0", anchor="nw", width=2) #ツリーのアイコンの列、デフォルトで作られている
    self.tree.column("title", anchor="nw")

    #ツリーをクリックしたときに対応したページを開く
    self.tree.bind(
      "<<TreeviewSelect>>",
      lambda event: self.open_help_page(event)
    )

    #ヘルプのページが入った辞書
    self.content_pages = {}

    #今のページの番号
    self.content_index = "iid_0_0"

    #ページごとのウィジェットが入った辞書
    self.content_widgets = {}

    #ヘルプ用のjsonを読み込む
    helps = self.load_json(paths.HELPS_FILE)
    topics = helps["topics"]

    for i, topic in  enumerate(topics):

      topic_id = topic["id"]
      topic_title = topic["title"]
      topic_items = topic["items"]

      #項目ごとの見出し
      parent_title = self.tree.insert(
        parent="", #parent（親要素）を空白にすることで最上位として配置できる
        index="end", #挿入位置
        iid=f"iid_{i}",
        values=topic_title
      )

      for j, topic_item in enumerate(topic_items):

        item_id = topic_item["id"]
        item_title = topic_item["title"]
        contents = topic_item["contents"]

        child_title = self.tree.insert(
          parent=parent_title,
          index="end",
          iid=f"iid_{i}_{j}",
          values=item_title
        )

        #ページを作る
        page_frame = ttk.Frame(content_frame)

        #ページの辞書にフレームを追加する
        self.content_pages[f"iid_{i}_{j}"] = page_frame

        #ウィジェットの辞書に空のリストを追加する
        self.content_widgets[f"iid_{i}_{j}"] = []

        #ページ名のラベル
        page_title_label = ttk.Label(
          page_frame,
          text=item_title,
          font=("MSゴシック", "20")
        )
        page_title_label.pack(pady=(10, 0))

        #ページ名の下の区切り
        separator = ttk.Separator(
          page_frame,
          orient="horizontal",
        )
        separator.pack(fill="both")

        for k, content in enumerate(contents):

          #ウィジェットの形式、ウィジェットの目的、本文
          widget_type, content_type, row, content_value = content

          #ラベルの場合
          if widget_type == "label":

            #タイトルラベル
            if content_type == "title":

              label = ttk.Label(
                page_frame,
                text=content_value,
                font=("MSゴシック", "10", "bold")
              )
              label.pack(pady=(10, 0))

            #本文ラベル
            if content_type == "body":

              label = ttk.Label(
                page_frame,
                text=content_value,
                font=("MSゴシック", "10")
              )
              label.pack(pady=(10, 0))

            #リンクラベル
            if content_type == "link":

              #リンク先URL
              url = self.links["helps_frame"][content_value]

              #リンクのラベル
              label = ttk.Label(
                page_frame,
                text=f"・{content_value}",
                font=self.link_font,
                foreground="#0000EE",
                background="#d9d9d9",
              )
              label.bind(
                "<1>",
                lambda event,
                u=url: self.label_click(event, u))
              label.pack(anchor="nw", pady=10)
              
            #ラベルをウィジェットの辞書に追加する
            self.content_widgets[f"iid_{i}_{j}"].append(label)

          #テキストの場合
          if widget_type == "text":

            text = tk.Text(
              page_frame,
              height=row+1
              )
            text.insert("1.0", content_value)
            text.config(state="disabled")

            text.pack(fill="both", pady=(0, 5))

            #テキストをウィジェットの辞書に追加する
            self.content_widgets[f"iid_{i}_{j}"].append(text)

          #画像の場合
          if widget_type == "image":

            #画像を貼るキャンバス
            canvas_width, canvas_height = content_type[0], content_type[1]

            canvas = tk.Canvas(page_frame, width=canvas_width, height=canvas_height)
            canvas.pack(pady=(5, 25))

            #パスから画像を開く
            img = Image.open(paths.get_help_images(content_value))

            #サイズ変更
            resized_img = img.resize((canvas_width, canvas_height))

            #キャンバスで使える形に変更
            tk_resized_img = ImageTk.PhotoImage(resized_img)

            #キャンバスに画像の属性を保存する
            canvas.image = tk_resized_img

            #キャンバスに画像を反映
            canvas.create_image(0, 0, image=canvas.image, anchor="nw", )

            #キャンバスをウィジェットの辞書に追加する
            self.content_widgets[f"iid_{i}_{j}"].append(canvas)

    #一番最初のページを表示する
    self.content_pages[self.content_index].pack()

  #ツリーメニューのページ名をクリックして開く
  def open_help_page(self, event):

    #クリックした行のiidを取得
    focused_iid = self.tree.focus()

    print(f"focused_iid = {focused_iid}")

    #iidがページの辞書にない場合は終了
    if not focused_iid in self.content_pages:
      return

    #今表示しているページを非表示にする
    self.content_pages[self.content_index].pack_forget()

    #取得したiidに対応するページを表示する
    self.content_pages[focused_iid].pack()

    #現在のページ番号にiidを反映
    self.content_index = focused_iid

    print(self.content_widgets)

    print(self.content_widgets["iid_1_0"][1].winfo_width())
    print(self.content_widgets["iid_1_0"][1].winfo_height())

    

