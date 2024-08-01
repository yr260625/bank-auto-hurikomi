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


def create_driver_headless(config: Dict[str, Any]) -> WebDriver:
    """
    WebDriver作成

    Args:
        config (Dict[str, Any]): driver設定

    Returns:
        WebDriver
    """
    # オプション設定
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--user-agent=" + random.choice(config["ua_list"]))
    options.binary_location = "/opt/chrome/chrome"
    # Chromeドライバーのサービスを設定
    service = Service(executable_path="/opt/chromedriver")

    return webdriver.Chrome(service=service, options=options)


def create_driver_headfull(config: Dict[str, Any]) -> WebDriver:
    """
    WebDriver作成

    Args:
        config (Dict[str, Any]): driver設定

    Returns:
        WebDriver
    """
    # オプション設定
    options = Options()
    options.add_argument("--user-agent=" + random.choice(config["ua_list"]))
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # 最新バージョンのChromeドライバを返却
    service = Service()

    return webdriver.Chrome(service=service, options=options)


def main(config: Dict[str, Any], driver: WebDriver):
    """メインロジック"""

    # BankTransferAutomation生成
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

        # 振込実行
        for transfer in config["transfers"]:
            bank, amount = transfer["bank"], transfer["amount"]
            print(f"{bank}: {amount}")
            bta.move_to_hurikomi()
            bta.execute_hurikomi(bank, amount)
            if not os.getenv("MODE_TEST") == "1":
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
        print(tb)
    finally:
        driver.quit()


def handler(event, context):
    """Lambda関数ハンドラー"""
    config = load_config("config.json")
    driver = create_driver_headless(config["driver"])
    main(config, driver)


def execute_headfull():
    """ヘッドフルモード"""
    print("execute_headfull")
    config = load_config("config.json")
    driver = create_driver_headfull(config["driver"])
    main(config, driver)


def execute_headless():
    """ヘッドレスモード"""
    print("execute_headless")
    config = load_config("config.json")
    driver = create_driver_headless(config["driver"])
    main(config, driver)


if __name__ == "__main__":
    load_dotenv()
    if os.getenv("LAMBDA_RUNTIME_DIR") is not None:
        execute_headless()
    else:
        execute_headfull()
