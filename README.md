# TNEB Outage Notifier

A Python script to automatically scrape the TNEB website for scheduled power outages and send notifications to a Telegram channel. It solves the website's CAPTCHA, fetches data for a specific area, and runs on a daily schedule.

## Features

* **Automated Scraping:** Fetches the latest power outage data from the TNEB website.
* **CAPTCHA Solving:** Uses Tesseract OCR to bypass the CAPTCHA.
* **Telegram Notifications:** Sends clean, formatted outage alerts to a Telegram chat.
* **Scheduled & Configurable:** Runs at a set time each day and is configured via a `.env` file.

## Prerequisites

* **Python 3.x**
* **Tesseract OCR Engine:**
    * **Windows:** [Download here](https://github.com/UB-Mannheim/tesseract/wiki). Remember to add to `PATH`.
    * **macOS:** `brew install tesseract`
    * **Linux:** `sudo apt-get install tesseract-ocr`
* **A Telegram Bot Token** from [BotFather](https://t.me/botfather).
* **A Telegram Chat ID** for the destination channel/group.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Install dependencies:**
    Run `pip install -r requirements.txt`.

3.  **Create a `.env` file:**
    Create a `.env` file and populate it with your configuration. Use the table below to find your `APPCAT_CODE`.
    ```env
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"
    APPCAT_CODE="0463,0401" # Example: Madurai-Metro, Chennai-south 1
    ```
4.  **Run with GitHub Actions:**
    - Add your secrets (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `APPCAT_CODE`) in your repository's GitHub settings under **Settings > Secrets and variables > Actions > Repository secrets**.
    - The script will run automatically at the scheduled time or when triggered manually.
    
## Available Circle Codes (`APPCAT_CODE`)

| Code | Circle Name       |
| :--- | :---------------- |
| 0435 | CBE/METRO         |
| 0430 | CBE/NORTH         |
| 0432 | CBE/SOUTH         |
| 0400 | CHENNAI SOUTH I   |
| 0401 | CHENNAI SOUTH II  |
| 0418 | CUDDALORE         |
| 0411 | CHENGALPATTU      |
| 0402 | CHENNAI - CENTRAL |
| 0404 | CHENNAI - NORTH   |
| 0406 | CHENNAI - WEST    |
| 0420 | DHARMAPURI        |
| 0450 | DINDIGUL          |
| 0426 | ERODE             |
| 0436 | GOBI              |
| 0417 | KALLAKURICHI      |
| 0410 | KANCHEEPURAM      |
| 0474 | KANYAKUMARI       |
| 0443 | KARUR             |
| 0421 | KRISHNAGIRI       |
| 0452 | MADURAI           |
| 0463 | MADURAI-METRO     |
| 0422 | METTUR            |
| 0445 | NAGAPATTINAM      |
| 0437 | NAMAKKAL          |
| 0482 | NILGIRIS          |
| 0439 | PALLADAM          |
| 0440 | PERAMBALUR        |
| 0446 | PUDUKKOTTAI       |
| 0478 | RAMNAD            |
| 0424 | SALEM             |
| 0460 | SIVAGANGAI        |
| 0444 | THANJAVUR         |
| 0476 | THENI             |
| 0447 | THIRUVARUR        |
| 0472 | TIRUNELVELI       |
| 0413 | TIRUPATTUR        |
| 0408 | TIRUVALLUR        |
| 0414 | TIRUVANNAMALAI    |
| 0442 | TRICHY METRO      |
| 0470 | TUTICORIN         |
| 0438 | TIRUPPUR          |
| 0434 | UDUMALPET         |
| 0412 | VELLORE           |
| 0416 | VILLUPURAM        |
| 0462 | VIRUDUNAGAR       |

## Usage

Run the script from your terminal. It will schedule the job and run automatically at the specified time.
```bash
python power-alert.py