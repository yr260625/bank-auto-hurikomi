from .bank_transfer_automation import BankTransferAutomation
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
import random
import traceback
import sys


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


def create_driver() -> WebDriver:
    """
    WebDriver作成

    Returns:
        WebDriver
    """

    # User Agentをランダムに指定
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    ]
    user_agent = random.choice(ua_list)

    # オプション設定
    options = Options()
    options.add_argument("--user-agent=" + user_agent)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("detach", True)

    # chrome最新バージョンのドライバを返却
    service = Service(executable_path=ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def create_bta() -> BankTransferAutomation:
    """
    BankTransferAutomation生成

    Returns:
        BankTransferAutomation
    """

    load_dotenv()
    env_var = {
        "wait_time": str(os.getenv("WAIT_TIME")),
        "kaiin_no": str(os.getenv("KAIIN_NO")),
        "password": str(os.getenv("PASSWORD")),
        "key_map": json.loads(str(os.getenv("KEY_MAP_STR"))),
        "login_url": str(os.getenv("LOGIN_URL")),
    }

    driver = create_driver()
    bta = BankTransferAutomation(env_var, driver)
    return bta


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python -m src.main config.json")
        sys.exit(1)

    try:
        print("-------------------------------------------")
        print("bank auto hurikomi start")
        bta = create_bta()

        # ログイン後、取引ページに遷移
        bta.login()
        bta.move_to_torihiki()

        # 設定ファイルから振り込み対象、振込金額を取得
        config_file = sys.argv[1]
        config = load_config(config_file)

        # 振込実行
        for transfer in config["transfers"]:
            bank, amount = transfer["bank"], transfer["amount"]
            print(f"{bank}: {amount}")
            bta.move_to_hurikomi()
            bta.execute_hurikomi(bank, amount)
            bta.execute_ninsyo()
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
