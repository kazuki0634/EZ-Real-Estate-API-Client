from pathlib import Path
import sys

"""
PyInstallerでビルドするとsysのfrozen属性がTrueになる
sys.executableで実行中のファイルのパスを得られる

exe化前はPathlibのPath(__file__)で実行中のファイルのパスを得られる
"""

#ルートディレクトリ
#exe化した後はこっち
if getattr(sys, "frozen", False):
  ROOT_DIR = Path(sys.executable).resolve().parent #resolveで絶対パスに変換

#exe化前はこっち
else:
  ROOT_DIR = Path(__file__).resolve().parent.parent #resolveで絶対パスに変換

#デスクトップ
DESKTOP_DIR = Path.home() / "Desktop"

#データファイル
DATA_DIR = ROOT_DIR / "data"

#データファイル直下の各ファイル
SETTINGS_FILE = DATA_DIR / "settings.json"
API_CATALOG_FILE = DATA_DIR / "api_catalog.json"
LINKS_FILE = DATA_DIR / "links.json"
HELPS_FILE = DATA_DIR / "helps.json"
HELP_IMAGES =  DATA_DIR / "help_images"

#help用の画像のパスを返す
def get_help_images(path):

  image_path = HELP_IMAGES / path

  return image_path