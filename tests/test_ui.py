import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_page_url() -> str:
    """Return file:// URL to index.html, works both locally and in CI."""
    base = os.environ.get("PAGE_URL")
    if base:
        return base
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return "file:///" + root.replace("\\", "/") + "/index.html"


@pytest.fixture(scope="module")
def driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,800")

    # In CI chromedriver is on PATH; locally webdriver-manager is used as fallback.
    try:
        drv = webdriver.Chrome(options=opts)
    except Exception:
        from webdriver_manager.chrome import ChromeDriverManager
        drv = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=opts
        )

    drv.get(get_page_url())
    yield drv
    drv.quit()


# ---------------------------------------------------------------------------
# Test 1 – page loads and title is correct
# ---------------------------------------------------------------------------
def test_page_title(driver):
    assert driver.title == "Форма регистрации", (
        f"Unexpected title: '{driver.title}'"
    )


# ---------------------------------------------------------------------------
# Test 2 – submit button exists on the page
# ---------------------------------------------------------------------------
def test_submit_button_exists(driver):
    btn = driver.find_element(By.ID, "submit-btn")
    assert btn is not None
    assert btn.text == "Отправить"


# ---------------------------------------------------------------------------
# Test 3 – empty fields → error message
# ---------------------------------------------------------------------------
def test_empty_fields_show_error(driver):
    driver.find_element(By.ID, "name").clear()
    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "submit-btn").click()

    result = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "result"))
    )
    assert result.text == "Заполните все поля", (
        f"Expected error message, got: '{result.text}'"
    )


# ---------------------------------------------------------------------------
# Test 4 – filled fields → success message
# ---------------------------------------------------------------------------
def test_filled_fields_show_success(driver):
    driver.find_element(By.ID, "name").clear()
    driver.find_element(By.ID, "name").send_keys("Иван Иванов")

    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "email").send_keys("ivan@example.com")

    driver.find_element(By.ID, "submit-btn").click()

    result = WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.ID, "result"), "Форма отправлена!")
    )
    assert result, "Success message 'Форма отправлена!' was not shown"
