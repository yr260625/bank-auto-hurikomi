from typing import Any, Dict
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


def create_driver(config: Dict[str, Any]) -> WebDriver:
    """
    WebDriver作成

    Args:
        config (Dict[str, Any]): driver設定

    Returns:
        WebDriver
    """

    # User Agentをランダムに指定
    user_agent = random.choice(config["ua_list"])

    # オプション設定
    options = Options()
    options.add_argument("--user-agent=" + user_agent)
    options.add_experimental_option("excludeSwitches", config["excludeSwitches"])
    options.add_experimental_option("detach", config["detach"])

    # chrome最新バージョンのドライバを返却
    return webdriver.Chrome(service=Service(), options=options)


if __name__ == "__main__":

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python -m src.main config.json <TEST>")
        sys.exit(1)

    # 設定ファイルから振り込み対象、振込金額を取得
    config_file = sys.argv[1]
    config = load_config(config_file)

    driver = create_driver(config["driver"])
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
    finally:
        driver.quit()
