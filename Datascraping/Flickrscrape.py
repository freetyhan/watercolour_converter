import requests, re, time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('.driver/chromedriver.exe',chrome_options=chrome_options)
driver.implicitly_wait(10)

def scrollDown(driver):
  # click on the load more results button to load more images if it is there
    if len(driver.find_elements(By.CSS_SELECTOR, ".infinite-scroll-load-more")) != 0:
      button = driver.find_element_by_css_selector(".infinite-scroll-load-more")
      driver.execute_script("arguments[0].click();", button)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


# retreive all image urls from flickr and put into list
def retreiveAllImages(driver, numImgs):
  img_lst = []
  for i in range(1, numImgs):
    elem = None
    # try to get next image, if it failed, scroll down to get it into view
    try:
      elem = driver.find_element_by_xpath(f"/html/body/div[1]/div/main/div[2]/div/div[2]/div[{i}]/div/div/a")
    except NoSuchElementException:
      scrollDown(driver)
      time.sleep(5)
      try:
        elem = driver.find_element_by_xpath(f"/html/body/div[1]/div/main/div[2]/div/div[2]/div[{i}]/div/div/a")
      except NoSuchElementException:
        continue     # this picture does not exist, try the next
    source = elem.get_attribute("href")
    if source is not None and "/photos" in source:
      img_lst.append(source)
    if i % 50 == 0:
      print(f"Read {i} images")
  return img_lst

def extractImages(driver, img_list):
  img_links = []
  num = 1
  for link in img_list:
    driver.get(link)
    time.sleep(1)
    try:
      elem = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div[1]/img[2]')
      source = elem.get_attribute("src")
      img_links.append(source)
      num += 1
    except NoSuchElementException:
      continue
    if num % 50 == 0:
      print(f"extracted {num} images")
  return img_links


# download all image urls into the path specified /html/body/div[1]/div/main/div[2]/div/div[2]/div[299]/div/div/a
def downloadImages(links, path, namePrefix):
  # list of user agents that the request will randomly use
  user_agent_list = [
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'
      'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240'
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
  ]
  numPic = 0
  for link in links:
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    if numPic % 10 == 0:
      time.sleep(5)
      print(f"Downloaded: {numPic} out of {len(links)}. {numPic / len(links)*100}%")
    time.sleep(1)
    resp = requests.get(link, headers=headers)
    if resp.status_code == 200:
      with open(f"{path}/{namePrefix}_{numPic}.jpg", "wb") as f:
        f.write(resp.content)
      numPic = numPic + 1

# load the image search page and load the images for the mazda rx7
driver.get("https://www.flickr.com/search/?text=watercolor&view_all=1")
time.sleep(2)
input("Press enter to continue...")
img_list = retreiveAllImages(driver, 2450)

img_links = extractImages(driver, img_list)
# save the links to a txt file to avoid having to scrape them again
with open("img_links.txt", "w") as output:
    output.write(str(img_links))

downloadImages(img_links, "Images", "wc")

driver.quit()
