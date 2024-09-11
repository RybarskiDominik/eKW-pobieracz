from selenium.webdriver.chrome.service import Service
from selenium import webdriver


def get_driver(main_browser="Edge", img: bool = False):
    match main_browser:
        case "Chrome":  # Chrome
            try:
                options = webdriver.ChromeOptions()

                if img is not True:
                    prefs = {"profile.managed_default_content_settings.images": 2}
                    options.add_experimental_option("prefs", prefs)

                options.add_argument("--disable-search-engine-choice-screen")

                service = Service()
                browser = webdriver.Chrome(service=service, options=options)

                return browser
            except:
                return get_driver(main_browser="Edge")
        case "Edge":  # Edge
            try:
                options = webdriver.EdgeOptions()

                if img is not True:
                    prefs = {"profile.managed_default_content_settings.images": 2}
                    options.add_experimental_option("prefs", prefs)

                service = Service()
                browser = webdriver.Edge(service=service, options=options)

                return browser
            except:
                return get_driver(main_browser="Chrome")
        case _:
            return None


if __name__ == "__main__":
    pass