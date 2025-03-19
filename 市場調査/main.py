from fastapi import FastAPI
from pydantic import BaseModel

from fastapi import FastAPI
from pydantic import BaseModel
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = FastAPI()

class Item(BaseModel):
    text: str

@app.post("/item")
def item_text(input_data: Item):
    return {"item": input_data.text}

app = FastAPI()

class MarketQuery(BaseModel):
    market_name: str

def search_market_trends(query):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://felo.ai/ja/search")

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "m-3.mr-0.w-full.bg-inherit.outline-none.resize-none.transition-height.custom-scrollbar"))
        )

        search_box.send_keys(query)
        search_box.submit()
        time.sleep(10)

        result = driver.page_source


        return result

    except Exception as e:
        return {"Error": str(e)}

    finally:
        driver.quit()

@app.post("/market_trend")
def get_market_trend(input_data: MarketQuery):
    query = f"{input_data.market_name}における2024年現在の市場規模を教えてください．結果は市場名，市場規模の金額をコンマ区切りで表示してください．桁区切り記号はなしで表示してください．単位は米ドルで表示してください．"

    result_html = search_market_trends(query)
    soup = BeautifulSoup(result_html, 'html.parser')

    result_p = soup.find('p', attrs={"node": "[object Object]", "dir": "auto"})
    
    if result_p:
        market_data = result_p.get_text(strip=True).split(',')
    
    #return {"market_name":market_data}

    #return {"market_name": market_data[0], "market_value": market_data[1]} # 名前を省略される
    return {"market_name": input_data.market_name, "market_value": market_data[1]} #こっちが良いかも
    #return {"market_name": market_data[0], "market_value": market_data[1]} # テスト用
