from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv
from playwright.async_api import  async_playwright
from playwright.sync_api import  sync_playwright
from bs4 import BeautifulSoup
from schemas import Payload
import os
import sys
import time
import re

load_dotenv()

GEMINI_CAPTCHA_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
    "gemini-flash-latest",
]
RETRYABLE_GEMINI_CODES = {429, 500, 503, 504}
GEMINI_MAX_RETRIES = 3

async def launch_browser(playwright):
    launch_kwargs = {"headless": True}
    if sys.platform == "darwin":
        launch_kwargs["channel"] = "chrome"
    try:
        return await playwright.chromium.launch(**launch_kwargs)
    except Exception:
        launch_kwargs.pop("channel", None)
        return await playwright.chromium.launch(**launch_kwargs)

def launch_browser_sync(playwright):
    launch_kwargs = {"headless": True}
    if sys.platform == "darwin":
        launch_kwargs["channel"] = "chrome"
    try:
        return playwright.chromium.launch(**launch_kwargs)
    except Exception:
        launch_kwargs.pop("channel", None)
        return playwright.chromium.launch(**launch_kwargs)

def gemini_text_extraction(captcha_image_path):
    with open(captcha_image_path, "rb") as f:
        image_bytes = f.read()

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    contents = [
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        "What is shown in this image?",
    ]
    config = types.GenerateContentConfig(
        system_instruction="Extract the text content from the provided image and return it in plain text format.",
    )

    models = GEMINI_CAPTCHA_MODELS
    if os.getenv("GEMINI_MODEL"):
        models = [os.environ["GEMINI_MODEL"], *GEMINI_CAPTCHA_MODELS]

    last_error = None
    for model in dict.fromkeys(models):
        for attempt in range(GEMINI_MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
                captcha_value = ''.join(re.findall(r'\d+', response.text))
                return captcha_value
            except APIError as error:
                last_error = error
                if error.code == 404:
                    break
                if error.code in RETRYABLE_GEMINI_CODES and attempt < GEMINI_MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                if error.code in RETRYABLE_GEMINI_CODES:
                    break
                raise

    raise last_error

def extract_table_data(content):
    soup = BeautifulSoup(content, "html.parser")
    table = soup.find('table')
    
    extract_details = {}
    rows = table.find_all('tr') if table else []
    
    for row in rows:
        header = row.find('b').text.strip() if row.find('b') else ''
        value = row.find('span').text.strip() if row.find('span') else ''
        extract_details[header] = value
    
    return extract_details

async def crawler(payload: Payload):
    captcha_image_path = "captcha.png"
    async with async_playwright() as p:
        browser = await launch_browser(p)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto('https://passport.immigration.gov.ng/')
        
        continue_button = page.locator('//button[@class="btn"]')
        await continue_button.click()


        apply_for_fresh_passport_button = page.locator('//div[@class="card_box_pass h-1"]').nth(0)
        await apply_for_fresh_passport_button.click()


        nin = page.locator('//input[@name="nin"]')
        await nin.fill(payload.nin)

        day = page.locator('//input[@name="dateOfBirthDay"]')
        await day.fill(payload.day)

        month = page.locator('//select[@name="dateOfBirthMonth"]')
        await month.select_option(label=payload.month)

        year = page.locator('//input[@name="dateOfBirthYear"]')
        await year.fill(payload.year)

        time.sleep(1.5)
        
        captcha_image = page.locator('//canvas[@id="captcahCanvas"]')
        await captcha_image.screenshot(path=captcha_image_path)

        captcha_value = gemini_text_extraction(captcha_image_path)
        print(captcha_value)
        
        captcha = page.locator('//input[@name="inputText"]')
        await captcha.fill(captcha_value)
    
        verify = page.locator('//input[@value="Verify"]')
        await verify.click()
        
        time.sleep(1)

        if not await page.is_visible('//span[@class="alert captcha-alert"]'): #captcha is solved
            time.sleep(2)

            if not await page.is_visible('//div[@class="ngx-dialog-body"]'): #nin is correct
                content = await page.content() 
                extract_details = extract_table_data(content)
        
            else: #nin is incorrect
                extract_details = await page.locator('//div[@class="ngx-dialog-body"]').inner_text() + ' or Date of Birth is incorrect'

        else: #captcha is not solved
            print('captcha not solved')

            while await page.is_visible('//span[@class="alert captcha-alert"]'):
                reload_captcha = page.locator('//a[@class="cpt-btn reload"]')
                await reload_captcha.click()
                
                time.sleep(1)

                captcha_image = page.locator('//canvas[@id="captcahCanvas"]')
                await captcha_image.screenshot(path=captcha_image_path)
                
                captcha_value = gemini_text_extraction(captcha_image_path)
                print(captcha_value)

                captcha = page.locator('//input[@name="inputText"]')
                await captcha.fill(captcha_value)

                verify = page.locator('//input[@value="Verify"]')
                await verify.click()
            
            time.sleep(3)

            if not await page.is_visible('//div[@class="ngx-dialog-body"]'): #nin is correct
                content = await page.content() 
                extract_details = extract_table_data(content)
            
            else: #nin is incorrect
                extract_details = await page.locator('//div[@class="ngx-dialog-body"]').inner_text() + ' or Date of Birth is incorrect'
        
        await browser.close()

    print(extract_details)
    return extract_details

def crawler_sync(payload: Payload):
    captcha_image_path = "captcha.png"
    with sync_playwright() as p:
        browser = launch_browser_sync(p)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto('https://passport.immigration.gov.ng/')
        
        continue_button = page.locator('//button[@class="btn"]')
        continue_button.click()


        apply_for_fresh_passport_button = page.locator('//div[@class="card_box_pass h-1"]').nth(0)
        apply_for_fresh_passport_button.click()


        nin = page.locator('//input[@name="nin"]')
        nin.fill(payload.nin)

        day = page.locator('//input[@name="dateOfBirthDay"]')
        day.fill(payload.day)

        month = page.locator('//select[@name="dateOfBirthMonth"]')
        month.select_option(label=payload.month)

        year = page.locator('//input[@name="dateOfBirthYear"]')
        year.fill(payload.year)

        time.sleep(1.5)
        
        captcha_image = page.locator('//canvas[@id="captcahCanvas"]')
        captcha_image.screenshot(path=captcha_image_path)

        captcha_value = gemini_text_extraction(captcha_image_path)
        print(captcha_value)
        
        captcha = page.locator('//input[@name="inputText"]')
        captcha.fill(captcha_value)
    
        verify = page.locator('//input[@value="Verify"]')
        verify.click()
        
        time.sleep(1)

        if not page.is_visible('//span[@class="alert captcha-alert"]'): #captcha is solved
            time.sleep(2)

            if not page.is_visible('//div[@class="ngx-dialog-body"]'): #nin is correct
                content = page.content() 
                extract_details = extract_table_data(content)
        
            else: #nin is incorrect
                extract_details = page.locator('//div[@class="ngx-dialog-body"]').inner_text() + ' or Date of Birth is incorrect'

        else: #captcha is not solved
            print('captcha not solved')

            while page.is_visible('//span[@class="alert captcha-alert"]'):
                reload_captcha = page.locator('//a[@class="cpt-btn reload"]')
                reload_captcha.click()
                
                time.sleep(1)

                captcha_image = page.locator('//canvas[@id="captcahCanvas"]')
                captcha_image.screenshot(path=captcha_image_path)
                
                captcha_value = gemini_text_extraction(captcha_image_path)
                print(captcha_value)

                captcha = page.locator('//input[@name="inputText"]')
                captcha.fill(captcha_value)

                verify = page.locator('//input[@value="Verify"]')
                verify.click()
            
            time.sleep(3)

            if not page.is_visible('//div[@class="ngx-dialog-body"]'): #nin is correct
                content = page.content() 
                extract_details = extract_table_data(content)
            
            else: #nin is incorrect
                extract_details = page.locator('//div[@class="ngx-dialog-body"]').inner_text() + ' or Date of Birth is incorrect'
        
        browser.close()

    print(extract_details)
    return extract_details
