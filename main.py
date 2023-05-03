from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time, re
import os, requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def getVideoTags(pagenumber):
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Executa o Chrome em modo headless (sem interface gráfica)
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=chrome_options)

    url = f"https://www.ahnegao.com.br/c/gifs/pag/{pagenumber}"
    driver.get(url)

    # Role a página até o final para forçar o carregamento de todas as tags de vídeo
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # saveLogAsHtml(soup)
    video_tags = []

    # Encontre a tag <video> e obtenha sua URL
    for video_tag in soup.find_all('video'):
        video_url = video_tag.get('src')
        video_tags.append((None, video_url, None, None))

    iframe_tags = soup.find_all('iframe')

    for iframe_tag in iframe_tags:
        src = iframe_tag.get('src')
        if 'videopress.com' in src:
            h2_tag = iframe_tag.find_previous('h2')
            title = h2_tag.text if h2_tag else None
            # Esperar até que o iframe seja carregado completamente
            iframe_element = driver.find_element(By.XPATH, f"//iframe[@src='{src}']")
            driver.switch_to.frame(iframe_element)

            html_element = driver.find_element(By.TAG_NAME, 'html')

            # Encontre as tags de vídeo na tag html
            video_elements = BeautifulSoup(html_element.get_attribute('innerHTML'), 'html.parser').find_all('video')
            # saveLogAsHtml(video_elements)
            for video_element in video_elements:
                poster_url = video_element.get('poster')
                if poster_url:
                    direct_url = poster_url.split("_mp4")[0] + ".mp4"
                    video_tags.append((title, src, poster_url, direct_url))

            driver.switch_to.default_content()

    driver.quit()
    return video_tags

def saveVideoFile(pagenumber, video_list):
    # Cria a pasta videos se ela não existe
    if not os.path.exists("videos"):
        os.makedirs("videos")
    for title, url, posterUrl, directLink in video_list:
        # Gera o nome do arquivo
        # regex for title to remove special characters
        title = re.sub(r'[^\w\s]', '', title)
        filename = f"page{pagenumber}_{title}.mp4"
        # Faz o download do arquivo e salva na pasta videos
        with open(os.path.join("videos", filename), "wb") as f:
            response = requests.get(directLink)
            f.write(response.content)

        print(f"Arquivo {filename} salvo com sucesso na pasta videos!")

def saveLogFile(video_list):
    # Cria a pasta logs se ela não existe
    if not os.path.exists("logs"):
        os.makedirs("logs")
    # Gera o nome do arquivo com base no timestamp
    filename = f"log_{int(time.time())}.txt"
    # Salva os dados em um arquivo de log
    with open(os.path.join("logs", filename), "w", encoding='utf-8') as f:
        for title, url, posterUrl, directLink in video_list:
            f.write(f"Título: {title} \nEmbed link: {url} \nLink Poster: {posterUrl}\nLink Direto: {directLink}\n\n")

        print(f"Arquivo {filename} salvo com sucesso na pasta logs!")

def saveLogAsHtml(pageHtml):
    filename = f"pageLog.html"
    with open(os.path.join("logs", filename), "w", encoding='utf-8') as f:
        f.write(str(pageHtml))
        print(f"Arquivo {filename} salvo com sucesso na pasta logs!")

for pagenumber in range(1, 10):
    video_list = getVideoTags(pagenumber)
    # saveLogFile(video_list)
    for title, url, posterUrl, directLink in video_list:
        print(f"Titulo: {title}")
        print(f"url de video: {url}")
        print(f"url de poster: {posterUrl}")
        print(f"url direta: {directLink}")
    saveVideoFile(pagenumber, video_list)