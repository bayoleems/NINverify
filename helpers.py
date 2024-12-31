
from vertexai.generative_models import GenerativeModel, Part
from playwright.async_api import  async_playwright
from playwright.sync_api import  sync_playwright
from bs4 import BeautifulSoup
from PIL import Image
from schemas import Payload
import io
import os
import time
import re

def convert_image_to_bytes(image_path):
    """
    Converts an image to a byte array and determines the correct MIME type based on the file extension.

    Args:
        image_path (str): The file path to the image.

    Returns:
        tuple: A tuple containing the byte array of the image and its MIME type.
    """
    # Load the image
    img = Image.open(image_path)
    
    # Extract the file extension and map it to a MIME type
    ext = os.path.splitext(image_path)[1].lower()
    mime_type = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff'
    }.get(ext) 

    # Convert the image to bytes
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format=img.format)
    img_byte_array = img_byte_array.getvalue()

    return img_byte_array, mime_type

def gemini_text_extraction(captcha_image_path):
    model = GenerativeModel(
    "gemini-1.5-flash-001",
    system_instruction=[
        """
        Extract the text content from the provided image and return it in plain text format.
        """
    ]
    )

    img_byte_array, mime_type = convert_image_to_bytes(captcha_image_path)
    chat = model.generate_content([Part.from_data(data=img_byte_array, mime_type=mime_type),"What is shown in this image?"])
    captcha_value = chat.to_dict()['candidates'][0]['content']['parts'][0]['text']
    
    captcha_value = ''.join(re.findall(r'\d+', captcha_value))

    return captcha_value

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
        browser = await p.chromium.launch(headless=True)
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
        browser = p.chromium.launch(headless=True)
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
