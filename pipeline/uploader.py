"""
Upload de vídeos no YouTube via automação de navegador (Selenium + Chrome).
Não usa a YouTube Data API — sem cota, sem cobrança.

Fluxo:
  1. Abre o YouTube Studio no Chrome
  2. Na primeira execução: usuário faz login manualmente
  3. Sessão é salva no perfil do Chrome para execuções futuras
  4. Script faz o upload, preenche título/descrição e publica
"""

import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys          # ✅ FIX 1: import no topo, fora do bloco
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

STUDIO_URL = "https://studio.youtube.com"
PROFILE_DIR = Path(__file__).parent.parent / "browser_profile"


def _build_driver(headless: bool = False) -> webdriver.Chrome:
    """Create a Chrome WebDriver with a persistent profile (saves login session)."""
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--profile-directory=YouTubeAgent")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if headless:
        options.add_argument("--headless=new")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def upload_to_youtube(
    video_path: Path,
    title: str,
    description: str,
    tags: list,
    headless: bool = False,
) -> bool:
    """
    Upload a video to YouTube Studio via browser automation.
    Returns True if upload was initiated successfully.
    """
    driver = _build_driver(headless)
    wait = WebDriverWait(driver, 90)

    try:
        driver.get(STUDIO_URL)
        time.sleep(3)

        # ── Check if login is needed ─────────────────────────────────────────
        if "accounts.google.com" in driver.current_url or "signin" in driver.current_url:
            print("\n🔐 LOGIN NECESSÁRIO")
            print("   O Chrome abriu. Faça login no YouTube Studio.")
            print("   Após o login, volte aqui e pressione ENTER.")
            input("   [ENTER para continuar] ")
            time.sleep(2)

        # ── Click upload button ──────────────────────────────────────────────
        upload_selectors = [
            "ytcp-button#upload-icon",
            "[aria-label='Upload videos']",
            "#upload-button",
        ]
        upload_btn = None
        for sel in upload_selectors:
            try:
                upload_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
                break
            except Exception:
                continue

        if not upload_btn:
            print("❌ Botão de upload não encontrado. Verifique se está logado.")
            return False

        upload_btn.click()
        time.sleep(2)

        # ── Select the video file ────────────────────────────────────────────
        file_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        file_input.send_keys(str(video_path.resolve()))
        print(f"   📤 Arquivo enviado: {video_path.name}")

        # ── Fill in title ────────────────────────────────────────────────────
        title_field = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='title-textarea']//div[@contenteditable='true']")
            )
        )
        title_field.click()
        time.sleep(0.5)
        title_field.send_keys(Keys.CONTROL + "a")   # ✅ FIX 2: removido import duplicado/bugado
        title_field.send_keys(title)
        print(f"   📝 Título: {title}")

        # ── Fill in description ──────────────────────────────────────────────
        try:
            desc_field = driver.find_element(
                By.XPATH,
                "//div[@id='description-textarea']//div[@contenteditable='true']",
            )
            desc_field.click()
            desc_field.send_keys(description)
        except Exception:
            pass

        # ── Navigate wizard (3x Next) ────────────────────────────────────────
        for step in range(3):
            time.sleep(2)
            try:
                next_btn = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//ytcp-button[@id='next-button']")
                    )
                )
                next_btn.click()
                print(f"   ➡️  Etapa {step + 1}/3")
            except Exception:
                break

        time.sleep(2)

        # ── Set visibility to Public and click Publish ───────────────────────
        try:
            public_radio = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//tp-yt-paper-radio-button[@name='PUBLIC']")
                )
            )
            public_radio.click()
            time.sleep(1)

            publish_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//ytcp-button[@id='done-button']")
                )
            )
            publish_btn.click()
            time.sleep(5)
            print("   ✅ Vídeo publicado!")
            return True

        except Exception as e:
            print(f"   ⚠️  Não foi possível publicar automaticamente: {e}")
            print("   O vídeo pode estar no YouTube Studio como rascunho.")
            print("   Verifique em: https://studio.youtube.com")
            input("   [ENTER para fechar o navegador] ")
            return False

    finally:
        driver.quit()