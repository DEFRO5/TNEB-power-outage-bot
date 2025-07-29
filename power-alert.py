import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import pytesseract
import re
import logging
import schedule
# from dotenv import load_dotenv
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TNEBOutageCrawler:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.appcat_code = os.getenv('APPCAT_CODE')
        self.base_url = 'https://www.tnebltd.gov.in/outages/viewshutdown.xhtml'

        if not self.bot_token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def get_viewstate(self):
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            viewstate_input = soup.find("input", {"name": "javax.faces.ViewState"})
            appcat_input = soup.find("input", {"name": lambda x: x and x.endswith(":appcat_focus")})
            if not viewstate_input:
                raise Exception("ViewState not found")
            
            if not appcat_input:
                raise Exception("AppCat input not found")
            
            return viewstate_input["value"], appcat_input['name'].split(':')[0]
        except Exception as e:
            logger.error(f"Failed to get ViewState: {e}")
            raise

    def solve_captcha(self):
        try:
            captcha_url = f"{self.base_url.replace('viewshutdown.xhtml', 'captcha.jpg')}?pfdrid_c=true"
            response = self.session.get(captcha_url, timeout=30)
            response.raise_for_status()
            
            image = Image.open(BytesIO(response.content))
            captcha_text = pytesseract.image_to_string(
                image, 
                config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            ).strip()
            
            captcha_text = re.sub(r'\W+', '', captcha_text)
            logger.info(f"CAPTCHA solved: {captcha_text}")
            return captcha_text
        except Exception as e:
            logger.error(f"CAPTCHA solving failed: {e}")
            raise
    
    def submit_form(self, viewstate, appcat, captcha_text):
        try:
            payload = {
                f'{appcat}': f'{appcat}',
                f'{appcat}:appcat_focus': '',
                f'{appcat}:appcat_input': self.appcat_code,
                f'{appcat}:cap': captcha_text,
                f'{appcat}:submit3': '',
                'javax.faces.ViewState': viewstate
            }
            
            response = self.session.post(self.base_url, data=payload, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Form submission failed: {e}")
            raise

    def parse_outages(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'id': 'j_idt6:j_idt8'})
            
            if not table:
                logger.warning("Outage table not found")
                raise Exception("Outage table not found")
            
            rows = table.find_all('tr')[1:]
            outages = []
            
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cols) >= 8:
                    date, town, substation, feeder, location, work_type, from_time, to_time = cols
                    outages.append({
                        'date': date,
                        'town': town,
                        'substation': substation,
                        'feeder': feeder,
                        'location': location,
                        'work_type': work_type,
                        'from_time': from_time,
                        'to_time': to_time
                    })
            
            logger.info(f"Parsed {len(outages)} outages")
            return outages
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            raise
    def format_message(self, outages):
        if not outages:
            return "No power outages currently scheduled."
        
        messages = []
        for outage in outages:
            message = (
                f"📅 {outage['date']}\n"
                f"⚡ {outage['substation']}\n"
                f"Town: {outage['town']}\n"
                f"Feeder: {outage['feeder']}\n"
                f"Location: {outage['location']}\n"
                f"Work: {outage['work_type']}\n"
                f"Time: {outage['from_time']} - {outage['to_time']}"
            )
            messages.append(message)
        
        return "\n\n".join(messages)

    def send_telegram(self, message):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            # Split message if too long
            max_length = 4000
            if len(message) > max_length:
                parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]
                for i, part in enumerate(parts):
                    response = requests.post(url, data={
                        "chat_id": self.chat_id,
                        "text": f"Part {i+1}/{len(parts)}:\n\n{part}",
                        "parse_mode": "HTML"
                    }, timeout=30)
                    response.raise_for_status()
            else:
                response = requests.post(url, data={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }, timeout=30)
                response.raise_for_status()
            
            logger.info("Message sent to Telegram successfully")
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            raise

    def run(self, max_captcha_retries=5):
        try:
            logger.info("Starting TNEB outage crawler")
            viewstate, appcat = self.get_viewstate()
            for attempt in range(max_captcha_retries):
              try:
                captcha_text = self.solve_captcha()
                html = self.submit_form(viewstate, appcat, captcha_text)
                outages = self.parse_outages(html)
                message = self.format_message(outages)
                self.send_telegram(message)
                
                logger.info("Crawler completed successfully")
                return True
              except Exception as captcha_e:
                logger.warning(f"Captcha attempt {attempt+1} failed: {captcha_e}")
                if attempt == max_captcha_retries - 1:
                    raise
                time.sleep(2)
        except Exception as e:
            error_msg = f"Crawler failed: {e}"
            logger.error(error_msg)
            try:
                self.send_telegram(f"Error: {error_msg}")
            except:
                pass
            return False
        
if __name__ == "__main__":
    # load_dotenv()
    TNEBOutageCrawler().run()