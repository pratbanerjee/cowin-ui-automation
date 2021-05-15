import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from retrying import retry

if platform.system() == 'Windows':
    from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()

wait_fixed = 500


def launch_browser():
    if platform.system() == 'Windows':
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    else:
        browser = webdriver.Chrome('/usr/bin/chromedriver', options=chrome_options)

    return browser


@retry(wait_fixed=wait_fixed)
def retry_till_find_element_by_tag_name(browser, tag_name):
    return browser.find_element_by_tag_name(tag_name)


@retry(wait_fixed=wait_fixed)
def retry_till_find_element_by_class_name(browser, class_name):
    return browser.find_element_by_class_name(class_name)


@retry(wait_fixed=wait_fixed)
def retry_till_find_elements_by_class_name(browser, class_name):
    elements = browser.find_elements_by_class_name(class_name)
    if len(elements) > 0:
        return elements
    else:
        raise Exception


@retry(wait_fixed=wait_fixed)
def retry_till_find_elements_by_tag_name(browser, tag_name):
    elements = browser.find_elements_by_tag_name(tag_name)
    if len(elements) > 0:
        return elements
    else:
        raise Exception


@retry(wait_fixed=wait_fixed)
def find_first_schedule_button(browser):
    return next(iter([i for i in retry_till_find_elements_by_class_name(browser, 'btnlist') if 'Schedule' in i.text]))


@retry(wait_fixed=wait_fixed)
def retry_click(element):
    element.click()
