import tkinter as tk


root = tk.Tk()

print(type(root))

if type(root) == "tkinter.Tk":
  print("1")

elif type(root) == tk.Tk:
  print("2")

#この場合だと2と表示される

root.mainloop()

