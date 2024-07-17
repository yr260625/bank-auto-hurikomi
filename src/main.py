from .bank_transfer_automation import BankTransferAutomation
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
import json
import os
import random
import traceback
import sys

load_dotenv()


def load_config(config_file: str):
    """設定ファイルJSON読み込み

    Args:
        config_file (str): 設定ファイルパス

    Returns:
        dict: 読み込んだ設定ファイルの内容
    """
    with open(config_file, "r", encoding="utf-8") as file:
        config = json.load(file)
    return config


def create_driver(ua_list: list[str]) -> WebDriver:
    """
    WebDriver作成

    Args:
        ua_list (list[str]): user-agent一覧

    Returns:
        WebDriver
    """

    # User Agentをランダムに指定
    user_agent = random.choice(ua_list)

    # オプション設定
    options = Options()
    options.add_argument("--user-agent=" + user_agent)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("detach", True)

    # chrome最新バージョンのドライバを返却
    return webdriver.Chrome(service=Service(), options=options)


if __name__ == "__main__":

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python -m src.main config.json <TEST>")
        sys.exit(1)

    # 設定ファイルから振り込み対象、振込金額を取得
    config_file = sys.argv[1]
    config = load_config(config_file)

    driver = create_driver(config["user_agent_list"])
    bta = BankTransferAutomation(driver, int(str(os.getenv("WAIT_TIME"))))

    try:
        print("-------------------------------------------")
        print("bank auto hurikomi start")

        # ログイン後、取引ページに遷移
        bta.login(
            str(os.getenv("LOGIN_URL")),
            str(os.getenv("KAIIN_NO")),
            str(os.getenv("PASSWORD")),
        )
        bta.move_to_torihiki()

        # テストモード
        is_test = True if len(sys.argv) == 3 else False

        # 振込実行
        for transfer in config["transfers"]:
            bank, amount = transfer["bank"], transfer["amount"]
            print(f"{bank}: {amount}")
            bta.move_to_hurikomi()
            bta.execute_hurikomi(bank, amount)
            if not is_test:
                bta.execute_ninsyo(json.loads(str(os.getenv("KEY_MAP_STR"))))
            bta.move_to_torihiki()

        # 結果参照
        bta.move_to_meisai()

        print("bank auto hurikomi end")
        print("-------------------------------------------")
    except Exception as e:
        tb = traceback.format_exc()
        print(
            f"Exception occurred in function: {traceback.extract_tb(e.__traceback__)[-1].name}"
        )
        print(f"Exception details: {str(e)}")
        print("Full traceback:")
        print(tb)
