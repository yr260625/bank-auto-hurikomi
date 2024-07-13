from typing import Any, Callable
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functools import wraps
import time
import random


def wait_random_time(func: Callable) -> Callable:
    """
    ランダム秒待機デコレータ

    Args:
        func (Callable): デコレータされる関数
    Returns:
        Callable: ランダムな待機時間(1~3秒)の後に元の関数を実行する新しい関数
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        wait_time = round(random.uniform(1, 3), 1)
        print(f"Calling {func.__name__}...")
        time.sleep(wait_time)
        return func(*args, **kwargs)

    return wrapper


class BankTransferAutomation:
    def __init__(self, driver: WebDriver, wait_time: int) -> None:
        """コンストラクタ

        Args:
            env_var (dict[str, str]): 環境変数一覧
            driver (WebDriver): WebDriver
        """
        self.driver = driver
        self.wait_time = wait_time

    @wait_random_time
    def login(self, login_url: str, kaiin_no: str, password: str) -> None:
        """ログイン"""

        # ログインページにアクセス
        self.driver.get(login_url)

        # 会員番号
        kaiin_no_element = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.NAME, "kaiinNo"))
        )
        kaiin_no_element.send_keys(kaiin_no)

        # ログインパスワード
        password_element = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.NAME, "ibpassword"))
        )
        password_element.send_keys(password)

        # ログイン実行
        login_button_element = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@type="button" and contains(@value, "ログイン")]')
            )
        )
        login_button_element.click()

    @wait_random_time
    def move_to_torihiki(self) -> None:
        """取引ページに遷移"""

        # インターネットバンキングメニューから「お取引・残高照会」を選択
        menu_button_element = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[img[@alt="お取引き・残高照会"]]')
            )
        )
        menu_button_element.click()

    @wait_random_time
    def move_to_meisai(self) -> None:
        """取引明細ページに遷移"""

        # 戻るボタン押下
        transit_button_element = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//input[@type="button" and contains(@value, "入出金明細")]',
                )
            )
        )
        transit_button_element.click()

    @wait_random_time
    def move_to_hurikomi(self) -> None:
        """振込ページに遷移"""

        # 振込ページに遷移
        transit_button_element = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//input[@type="button" and contains(@value, "この口座から振り込み")]',
                )
            )
        )
        transit_button_element.click()

    @wait_random_time
    def execute_hurikomi(self, bank_name: str, amount: str) -> None:
        """振込実行

        Args:
            payee (int): 振込先インデックス
        """

        # 振込先選択
        rows = self.driver.find_elements(
            By.XPATH, "//tr[td/input[@type='radio' and @name='selectedIdx']]"
        )
        for row in rows:
            if bank_name in row.text:
                radio_button = row.find_element(
                    By.XPATH, ".//input[@type='radio' and @name='selectedIdx']"
                )
                radio_button.click()
                break

        # 振込金額を入力
        money_element = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.NAME, "kingakuDisp"))
        )
        money_element.send_keys(amount)

        # 認証ページに遷移
        transit_button_element = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@type="button" and contains(@value, "次へ")]')
            )
        )
        transit_button_element.click()

    @wait_random_time
    def execute_ninsyo(self, key_map: dict[str, str]) -> None:
        """認証実行"""

        # 確認番号のキー一覧取得
        key_list = []
        span_elements = self.driver.find_elements(
            By.XPATH, '//span[@class="kakunin-no-label"]/nobr'
        )
        for span in span_elements:
            key_list.append(span.text)

        # 確認番号入力
        input_elements = self.driver.find_elements(
            By.CSS_SELECTOR, "input.kakunin-no-field"
        )
        for i, input_element in enumerate(input_elements, start=0):
            input_element.clear()
            input_element.send_keys(key_map[key_list[i]])

        # 確定ボタン押下
        transit_button_element = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@type="button" and contains(@value, "確定")]')
            )
        )
        transit_button_element.click()
