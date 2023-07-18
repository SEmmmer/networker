import concurrent.futures
import os


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv


def request_web(url):
    while True:
        # 设置ChromeDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 配置浏览器为静默模式
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service)

        start_time = time.time()
        # 打开指定的URL
        driver.get(url)

        # 等待页面加载完成
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//body')))
        except Exception as e:
            print(f"Exception occurred: {str(e)}")

        end_time = time.time()

        driver.quit()
        return end_time - start_time


if __name__ == '__main__':
    urls = ["https://www.bilibili.com/",
            "https://www.baidu.com/",
            "https://www.google.com/",
            "https://www.youtube.com/",
            "https://github.com/"]

    current_unix_time = int(time.time())
    file = open(str(current_unix_time) + '_load_times.csv', 'w', newline='')

    writer = csv.writer(file)
    writer.writerow(["Timestamp",
                     "Bilibili Load Time",
                     "baidu Load Time",
                     "Google Load Time",
                     "YouTube Load Time",
                     "GitHub Load Time"])
    while True:
        current_unix_time = int(time.time())
        load_times = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(request_web, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
                    data = -1  # 如果发生异常，加载时间记为-1
                load_times.append(data)

        writer.writerow([current_unix_time] + load_times)
        file.flush()  # 清空缓冲区
        os.fsync(file.fileno())  # 强制写入磁盘
        time.sleep(5)

    file.close()
