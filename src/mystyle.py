from tkinter import ttk

def create_style():
  s = ttk.Style()

  #プルダウン
  s.theme_settings("default",{
    "TCombobox":{
      "map":{
        "fieldbackground":[
          ("readonly", "#FFFFFF"),
          ("disabled", "#d9d9d9")
        ],
        "selectbackground":[
          ("readonly", "#FFFFFF"),
          ("disabled", "#d9d9d9")
        ],
        "selectforeground":[
          ("readonly", "#000000"),
          ("disabled", "#d9d9d9")
        ],    
      }
    }
  }
  )

  #入力欄
  s.theme_settings("default",{
    "TEntry":{
      "map":{
        "fieldbackground":[
          ("readonly", "#FFFFFF"),
          ("disabled", "#d9d9d9")
        ],
      "selectbackground":[
          ("!disabled", "#0078d7"),
          ("disabled", "#d9d9d9")
        ],
      "selectforeground":[
          ("!disabled", "#FFFFFF"),
          ("disabled", "#d9d9d9")
        ],    
      }
    }
  }
  )

  #選択前のチェックボックスの色を固定する必要がある
  s.theme_settings("default", { 
    "TCheckbutton": {
      "map": {
          "indicatorcolor": [
            ("selected", "#0078d7"),
            ("!selected", "#FFFFFF")
        ]
      }
    }
  }
  )

  #ツリー
  s.theme_settings("default", { 
    "Treeview": {
      "map": {
          "background": [
            ("selected", "#0078d7"),
            ("!selected", "#FFFFFF")
        ]
      }
    }
  }
  )


  return s