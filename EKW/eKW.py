from PySide6.QtWidgets import (QApplication, QMainWindow, QCheckBox,
                               QApplication, QMainWindow, QLabel,
                               QFrame, QGroupBox, QVBoxLayout, QWidget,
                               QPushButton, QHBoxLayout, QLineEdit,
                               QComboBox, QRadioButton, QFileDialog)
from PySide6.QtCore import Qt,QRect, QSettings, QCoreApplication, QThread, Signal, QMutex, QWaitCondition
from PySide6.QtGui import QIcon, QFont, QIntValidator
from PySide6 import QtWidgets

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup as BS
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import unicodedata
import subprocess
import logging
import time
import sys
import os


from KW import kw_generator

from Lista_kw import lista_items_kw
from Lista_kw import city_names


@dataclass
class data:
    lista_kw: list = None


class WorkerMain(QThread):
    update_progress = Signal(int)
    def __init__(self, lista=False, początek=None, Koniec=None, key=None, turbo=False, img=None, max_workers=3):
        super().__init__()
        self.lista = lista

        self.kill = False
        self.pause = False

        self.img = img
        self.key = key

        self.początek = początek
        self.Koniec = Koniec
        self.max_workers = max_workers

        self.turbo = turbo 

    def run(self):
        self.kill = False
        self.pause = False

        if self.lista is not False:
            if not data.lista_kw:
                print("Import list")
                return
            else:
                kw_list = data.lista_kw
                df = self.main_list(kw_list)

        else:
            if self.turbo:
                kw_list = lista_kw(self.początek, self.Koniec, self.key)
                df = self.main_turbo(kw_list, self.max_workers)
            else:
                df = self.main(self.początek, self.Koniec, self.key)

        df.to_excel(os.path.join(os.path.expanduser("~/Desktop"), 'KW.xlsx'), index=True)

        print("END")

    def main(self, początek, Koniec, key):
        self.key = key
        self.początek = początek
        self.Koniec = Koniec
        a = []
        if self.Koniec is None:
            self.Koniec = self.początek

        while self.początek<self.Koniec+1:
            while self.pause:
                time.sleep(1)
                print("Paused...")
                if self.kill:
                    print("Killed during pause")
                    return pd.DataFrame(a)

            if self.kill:
                print("Process killed")
                break
            i = kw_generator(self.key, str(self.początek))
            self.początek += 1
            id_kw = f"{i[0]}/{i[1]}/{i[2]}"
            result, id = open_kw(id_kw, i)
            if result:
                a.extend(result)  # Extending the list with the result to flatten the structure
            else:
                a.append({'id': f"{id_kw}", 'Numer działki': 'Not found', 'Identyfikator działki': 'Not found'})

        return pd.DataFrame(a)

    def main_list(self, kw_list):
        a = []
        i = []

        for line in kw_list:
            i = line.split("/")
            if len(i) < 3:  # Upewnij się, że lista ma co najmniej 3 elementy
                apend = kw_generator(i[0], str(i[1]))
                i.append(apend[2])
            if i[2] == "":
                apend = kw_generator(i[0], str(i[1]))
                i[2]= apend[2]
            if len(i) > 3:
                continue
            
            id_kw = f"{i[0]}/{i[1]}/{i[2]}"
            #print(id_kw)
            result, id = open_kw(i[0], i)
            if result:
                a.extend(result)  # Extending the list with the result to flatten the structure
            else:
                a.append({'id': f"{id_kw}", 'Numer działki': 'Not found', 'Identyfikator działki': 'Not found'})

        return pd.DataFrame(a)

    def main_turbo(self, kw_list, max_workers):
        results = []
        with ThreadPoolExecutor(max_workers) as executor:
            futures = [executor.submit(open_kw, id_kw, kw) for id_kw, kw in kw_list]
                        
            for future in as_completed(futures):
                result, id_kw = future.result()
                if result:
                    results.extend(result)
                else:
                    results.append({'id': f"{id_kw}", 'Numer działki': 'Not found', 'Identyfikator działki': 'Not found'})

        return pd.DataFrame(results)

    def kill_main(self):
        self.kill = True

    def pause_main(self):
        if self.pause:
            self.pause = False
        else:
            self.pause = True

    def export_to_excel(self, data=None):
        data.to_excel(os.path.expanduser("~/Desktop"), index=True)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.settings = QSettings('eKW', 'Księgi Wieczyste')
        self.last = None
        #dark_mode_enabled = self.settings.value('DarkMode', False, type=bool) == True:

        '''
        self.setStyleSheet("""
        QCheckBox {
            color: #ffffff;
            }
        QGroupBox {
            color: #ffffff;
            }
        """)
        '''
        self.setFixedSize(300, 400)
        self.setWindowTitle('eKW')

        self.init_UI()

    def init_UI(self):

        # Widget LIST

        def widget_LIST(self):
            self.list_widget = QWidget(self)
            self.list_widget.setHidden(True)
            self.list_widget.setGeometry(5, 36, 295, 200)

            self.button_import_lista= QtWidgets.QPushButton(self.list_widget)
            self.button_import_lista.setGeometry(40, 2, 80, 28)
            self.button_import_lista.setText("Importuj liste")
            self.button_import_lista.clicked.connect(import_kw)

            self.button_import_reset= QtWidgets.QLineEdit(self.list_widget)
            self.button_import_reset.setGeometry(120, 4, 80, 24)
            self.button_import_reset.setText("---")
            self.button_import_reset.setAlignment(Qt.AlignCenter)
            #self.button_import_reset.clicked.connect(self.reset)s

            self.button_import_reset= QtWidgets.QPushButton(self.list_widget)
            self.button_import_reset.setGeometry(200, 2, 60, 28)
            self.button_import_reset.setText("Reset")
            #self.button_import_reset.clicked.connect(self.reset)
        widget_LIST(self)

        font = QFont()
        font.setPointSize(18)
        int_validator = QIntValidator(0, 99999999)

        # Widget GEN

        def widget_GEN(self):
            self.gen_widget = QWidget(self)  # Create and set the central widget
            self.gen_widget.setHidden(False)
            self.gen_widget.setGeometry(0, 36, 350, 100)

            # Manually set the positions of the widgets
            self.button_gen_kod = QComboBox(self.gen_widget)
            self.button_gen_kod.setGeometry(QRect(5, 0, 75, 26))
            self.button_gen_kod.addItem("kod sądu", None)
            for item_id, code in lista_items_kw:
                self.button_gen_kod.addItem(code, item_id)
            self.button_gen_kod.setToolTip("Tutaj można sprawdzić kod sądu.")
            self.button_gen_kod.currentIndexChanged.connect(self.update_tooltip)
            saved_kod_sadu = self.settings.value('KodSądu', None)
            if saved_kod_sadu is not None:
                index = self.button_gen_kod.findData(saved_kod_sadu)
                if index != -1:
                    self.button_gen_kod.setCurrentIndex(index)

            self.label = QLabel(self.gen_widget)
            self.label.setText("/")
            self.label.setFont(font)
            self.label.setGeometry(QRect(82, 0, 30, 22))

            self.button_gen_text_kw = QLineEdit(self.gen_widget)
            self.button_gen_text_kw.setGeometry(QRect(95, 0, 70, 26))
            self.button_gen_text_kw.setPlaceholderText("1-8")
            self.button_gen_text_kw.setMaxLength(8)
            self.button_gen_text_kw.setValidator(int_validator)
            #self.button_gen_text_kw.setClearButtonEnabled(True)
            self.button_gen_text_kw.setAlignment(Qt.AlignCenter)

            self.label_2 = QLabel(self.gen_widget)
            self.label_2.setText("/")
            self.label_2.setFont(font)
            self.label_2.setGeometry(QRect(167, 0, 30, 22))

            self.gen_liczba_kontrolna_1 = QLineEdit(self.gen_widget)
            self.gen_liczba_kontrolna_1.setGeometry(QRect(180, 0, 20, 26))
            self.gen_liczba_kontrolna_1.setPlaceholderText("-")
            self.gen_liczba_kontrolna_1.setMaxLength(1)
            self.gen_liczba_kontrolna_1.setValidator(int_validator)
            #self.gen_liczba_kontrolna_1.setClearButtonEnabled(True)
            self.gen_liczba_kontrolna_1.setAlignment(Qt.AlignCenter)

            self.button_gen_generuj = QPushButton(self.gen_widget)
            self.button_gen_generuj.setGeometry(QRect(205, 0, 90, 28))
            self.button_gen_generuj.setText("Generuj")
            self.button_gen_generuj.clicked.connect(self.generuj_kw)

            # Kolumna 

            # Manually set the positions of the widgets
            self.line_edit_szukaj = QLineEdit(self.gen_widget)
            self.line_edit_szukaj.setGeometry(QRect(5, 28, 75, 26))
            self.line_edit_szukaj.setPlaceholderText("Wyszukaj")
            self.line_edit_szukaj.textChanged.connect(self.find_best_match)

            self.label_3 = QLabel(self.gen_widget)
            self.label_3.setText("/")
            self.label_3.setFont(font)
            self.label_3.setGeometry(QRect(82, 28, 30, 22))

            self.button_gen_text_kw2 = QLineEdit(self.gen_widget)
            self.button_gen_text_kw2.setGeometry(QRect(95, 28, 70, 26))
            self.button_gen_text_kw2.setValidator(int_validator)
            self.button_gen_text_kw2.setDisabled(True)
            self.button_gen_text_kw2.setPlaceholderText("1-8")
            self.button_gen_text_kw2.setMaxLength(8)
            #self.button_gen_text_kw2.setClearButtonEnabled(True)
            self.button_gen_text_kw2.setAlignment(Qt.AlignCenter)

            self.label_4 = QLabel(self.gen_widget)
            self.label_4.setText("/")
            self.label_4.setFont(font)
            self.label_4.setGeometry(QRect(167, 28, 30, 22))

            self.gen_liczba_kontrolna_2 = QLineEdit(self.gen_widget)
            self.gen_liczba_kontrolna_2.setGeometry(QRect(180, 28, 20, 26))
            self.gen_liczba_kontrolna_2.setValidator(int_validator)
            self.gen_liczba_kontrolna_2.setDisabled(True)
            self.gen_liczba_kontrolna_2.setPlaceholderText("-")
            self.gen_liczba_kontrolna_2.setMaxLength(1)
            #self.gen_liczba_kontrolna_2.setClearButtonEnabled(True)
            self.gen_liczba_kontrolna_2.setAlignment(Qt.AlignCenter)

            self.button_gen_Lista = QCheckBox(self.gen_widget)
            self.button_gen_Lista.setGeometry(QRect(205, 28, 90, 28))
            self.button_gen_Lista.setText("Lista")
            self.button_gen_Lista.clicked.connect(lambda state: self.list_disable(False) if state == 1 else self.list_disable(True))

            self.button_gen_copy = QPushButton(self.gen_widget)
            self.button_gen_copy.setGeometry(QRect(250, 28, 45, 28))
            self.button_gen_copy.setText("Kopiuj")
            self.button_gen_copy.clicked.connect(self.kopiuj_kw)
            self.button_gen_copy.setToolTip("Przycisk kopiuje pierwszą KW do schowka.")

        widget_GEN(self)

        self.button_Lista = QtWidgets.QPushButton(self)
        self.button_Lista.setText("Lista")
        self.button_Lista.setGeometry(20, 5, 80, 28)
        self.button_Lista.clicked.connect(lambda: self.hide_widget(self.list_widget))
        self.button_Lista.clicked.connect(lambda: self.set_bottom_border(self.button_Lista))
        self.button_Lista.clicked.connect(lambda: self.last_widget("LISTA"))
        
        self.button_Generuj = QtWidgets.QPushButton(self)
        self.button_Generuj.setText("Generuj")
        self.set_bottom_border(self.button_Generuj)
        self.button_Generuj.setGeometry(110, 5, 80, 28)
        self.button_Generuj.clicked.connect(lambda: self.hide_widget(self.gen_widget))
        self.button_Generuj.clicked.connect(lambda: self.set_bottom_border(self.button_Generuj))
        self.button_Generuj.clicked.connect(lambda: self.last_widget("MAIN"))

        self.button_Ustawienia = QtWidgets.QPushButton(self)
        self.button_Ustawienia.setText("Ustawienia")
        self.button_Ustawienia.setGeometry(200, 5, 80, 28)
        self.button_Ustawienia.clicked.connect(lambda: self.hide_widget(self.settings_widget))
        self.button_Ustawienia.clicked.connect(lambda: self.set_bottom_border(self.button_Ustawienia))
        self.button_Ustawienia.clicked.connect(lambda: self.last_widget("PASS"))

        self.set_button_styles(self.button_Lista, self.button_Ustawienia)

        self.settings_widget = QWidget(self)  # Create and set the central widget
        self.settings_widget.setHidden(True)
        self.settings_widget.setGeometry(5, 36, 350, 100)
    
        self.settings_Turbo = QCheckBox(self.settings_widget)
        self.settings_Turbo.setGeometry(QRect(10, 00, 90, 28))
        self.settings_Turbo.setText("Turbo")
        if self.settings.value("Turbo", None, type=bool) == True:
            self.settings_Turbo.setChecked(True)
        self.settings_Turbo.clicked.connect(lambda: self.save_state(self.settings_Turbo, "Turbo"))

        self.settings_img = QCheckBox(self.settings_widget)
        self.settings_img.setGeometry(QRect(10, 14, 90, 28))
        self.settings_img.setText("Blokuj obrazy.")
        if self.settings.value("IMG", None, type=bool) == True:
            self.settings_img.setChecked(True)
        self.settings_img.clicked.connect(lambda: self.save_state(self.settings_img, "IMG"))

        self.settings_dark_mode = QCheckBox(self.settings_widget)
        self.settings_dark_mode.setGeometry(QRect(10, 28, 90, 28))
        self.settings_dark_mode.setText("Dark mode")
        if self.settings.value("DarkMode", None, type=bool) == True:
            self.settings_dark_mode.setChecked(True)
        self.settings_dark_mode.clicked.connect(lambda: self.save_state(self.settings_dark_mode, "DarkMode"))
        self.settings_dark_mode.setDisabled(True)

        # Widget ...

        self.info = QtWidgets.QPushButton(self)
        self.info.setText("...")
        self.info.setGeometry(5, 365, 110, 28)
        #self.info.clicked.connect(self.reset)

        self.button_start= QtWidgets.QPushButton(self)
        #self.button_start.setGeometry(165, 365, 50, 28)
        self.button_start.setGeometry(195, 365, 50, 28)
        self.button_start.setText("Stop")
        self.button_start.clicked.connect(lambda: self.worker.pause_main())

        self.button_start= QtWidgets.QPushButton(self)
        #self.button_start.setGeometry(115, 365, 50, 28)
        self.button_start.setGeometry(245, 365, 50, 28)
        self.button_start.setText("Anuluj")
        self.button_start.clicked.connect(lambda: self.worker.kill_main())

        self.button_start= QtWidgets.QPushButton(self)
        self.button_start.setGeometry(115, 365, 80, 28)
        #self.button_start.setGeometry(215, 365, 80, 28)
        self.button_start.setText("Start")
        self.button_start.clicked.connect(self.start_main)

    def save_state(self, check_box, key):
        self.settings.setValue(key, check_box.isChecked())

    def generuj_kw(self):
        góra = self.button_gen_text_kw.text()
        if not góra:
            self.info.setText("Brak numeru KW.")
            return
        
        current_index = self.button_gen_kod.currentIndex()
        key_id = self.button_gen_kod.itemData(current_index)
        key = self.button_gen_kod.currentText()
        if key_id is None:
            self.info.setText("Brak kodu.")
            return

        k1 = kw_generator(key, góra)
        self.gen_liczba_kontrolna_1.setText(k1[2])

        dół = self.button_gen_text_kw2.text()
        if not dół or self.button_gen_Lista.checkState() == Qt.Unchecked:
            pass
        else:
            k2 = kw_generator(key, dół)
            self.gen_liczba_kontrolna_2.setText(k2[2])

    def kopiuj_kw(self):
        def setClipboardData(txt):
            cmd='echo '+txt.strip()+'|clip'
            return subprocess.check_call(cmd, shell=True)
        
        góra = self.button_gen_text_kw.text()
        if not góra:
            self.info.setText("Brak numeru KW.")
            return
        
        current_index = self.button_gen_kod.currentIndex()
        key_id = self.button_gen_kod.itemData(current_index)
        key = self.button_gen_kod.currentText()
        if key_id is None:
            self.info.setText("Brak kodu.")
            return

        i = kw_generator(key, góra)
        kw = f"{i[0]}/{i[1]}/{i[2]}"
        setClipboardData(kw)

    def set_button_styles(self, *buttons):
        for button in buttons:
            button.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-bottom: none;
                }
            """)

    def set_bottom_border(self, button):
        button.setStyleSheet("""
            QPushButton {
                border: none;
                border-bottom: 2px solid red;
            }
        """)

    def hide_widget(self, widget):
        self.set_button_styles(self.button_Lista, self.button_Generuj, self.button_Ustawienia)
        
        self.list_widget.setHidden(True)
        self.gen_widget.setHidden(True)
        self.settings_widget.setHidden(True)

        widget.setHidden(False)

    def last_widget(self, widget=None):
        self.last = widget

    def update_tooltip(self):
        current_index = self.button_gen_kod.currentIndex()
        id = self.button_gen_kod.itemData(current_index)
        for item_id, city_name in city_names:
            if id is None:
                self.button_gen_kod.setToolTip("Tutaj można sprawdzić kod sądu.")
                self.setWindowTitle('eKW')
            elif id in item_id:
                self.button_gen_kod.setToolTip(city_name)
                self.setWindowTitle(f"eKW {city_name}")
                self.settings.setValue("KodSądu", id)

    def normalize_text(self, text):
        # Normalize Unicode text and convert to lowercase
        normalized_text = unicodedata.normalize('NFKD', text)
        return normalized_text.encode('ASCII', 'ignore').decode('ASCII').lower()

    def find_best_match(self, text):
        best_match_id = None

        for item_id, city_name in city_names:
            city_name = self.normalize_text(city_name)
            if self.normalize_text(text) in self.normalize_text(city_name):  # if text.lower() in city_name.lower():
                best_match_id = item_id
                break

        # If a match is found, set the QComboBox to the corresponding item
        if best_match_id:
            index = self.button_gen_kod.findData(best_match_id)
            if index != -1:
                self.button_gen_kod.setCurrentIndex(index)

    def list_disable(self, disable):
        if disable:
            self.button_gen_text_kw2.setDisabled(True)
            self.gen_liczba_kontrolna_2.setDisabled(True)
        else:
            self.button_gen_text_kw2.setDisabled(False)
            self.gen_liczba_kontrolna_2.setDisabled(False)

    def start_old(self):
        img = False
        key = "GL1R"

        start = 1
        Koniec = 1
        max_workers = 3  # defoult = 3
   
        kw_list = lista_kw(start, Koniec, key)
        run_concurrent_open_kw(kw_list, max_workers)

    def start_main(self):
        lista = False
        początek = None
        Koniec = None
        key = None
        if self.last == "PASS":
            return
        elif self.last == "LISTA":
            if not data.lista_kw:
                import_kw()
                if not data.lista_kw:
                    return
            lista = True
        else:
            początek = self.button_gen_text_kw.text()
            if not początek:
                self.info.setText("Brak numeru KW.")
                return
            początek = int(początek)
            
            Koniec = self.button_gen_text_kw2.text()
            if not Koniec or self.button_gen_Lista.checkState() == Qt.Unchecked:
                Koniec = początek
            Koniec = int(Koniec)

            if Koniec < początek:
                self.info.setText("KW2 < KW1")
                return
            
            current_index = self.button_gen_kod.currentIndex()
            key_id = self.button_gen_kod.itemData(current_index)
            key = self.button_gen_kod.currentText()
            if key_id is None:
                self.info.setText("Brak kodu.")
                return

        if self.settings_Turbo.checkState() == Qt.Checked:
            turbo = True
        else:
            turbo = False

        if self.settings_img.checkState() == Qt.Checked:
            img = True
        else:
            img = None

        max_workers = 3

        #print(początek, Koniec, key, turbo, img, max_workers)

        self.worker = WorkerMain(lista, początek, Koniec, key, turbo, img, max_workers)
        self.worker.start()


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

def open_kw(id_kw, kw):
    browser = get_driver()
    browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')

    time.sleep(3)

    ### insert KW number

    elem = browser.find_element(By.ID, 'kodWydzialuInput')  # Find the search box
    elem.send_keys(kw[0])

    elem = browser.find_element(By.NAME, 'numerKw')  # Find the search box
    elem.send_keys(kw[1])

    elem = browser.find_element(By.NAME, 'cyfraKontrolna')  # Find the search box
    elem.send_keys(kw[2])

    elem = browser.find_element(By.NAME, 'wyszukaj')  # Find the search box
    elem.send_keys(Keys.RETURN)

    time.sleep(1)
    try:
        elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')  # Find the search box
        elem.send_keys(Keys.RETURN)
    except:
        return None, id_kw

    time.sleep(1)

    data = dz_from_page(id_kw, browser.page_source)

    return data, id_kw

def dz_from_page(id_value=None, page_source=None):

    soup = BS(page_source, 'html.parser')

    elem = soup.findAll('td', separator='')

    my_data = []

    temp = []
    for el in elem:

        if el.text != '':
            if el.text == '\n\n\n\n\n':
                continue
            temp.append(el.text)
        else:
            my_data.append(temp)
            temp = []

    element = []  # {}
    new_data = {}
    next = False
    last_name = ''
    i = 1

    valid_tags = ["Numer działki", "Identyfikator działki"]
    for md in my_data:
        if 'Numer działki' in md:
            for m in md:
                if next:
                    next = False
                    new_data[last_name] = m.strip()
                if m.strip() in valid_tags:
                    last_name = m
                    next = True
                else:
                    pass

            new_data_with_id = {'id': id_value}
            new_data_with_id.update(new_data)

            element.append(new_data_with_id)

            i += 1
            new_data = {}
    return element

def main_old(start=1, Koniec=None, key=None):
    a = []
    if Koniec is None:
        Koniec = start
    while start<Koniec+1:
        i = kw_generator(key, str(start))
        start += 1
        id_kw = f"{i[0]}/{i[1]}/{i[2]}"
        result, id = open_kw(id_kw, i)
        if result:
            a.extend(result)
        else:
            a.append({'id': f"{id_kw}", 'Numer działki': 'Not found', 'Identyfikator działki': 'Not found'})
    df = pd.DataFrame(a)
    return df

def run_concurrent_open_kw(kw_list, max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers) as executor:
        futures = [executor.submit(open_kw, id_kw, kw) for id_kw, kw in kw_list]
        
        for future in as_completed(futures):
            result, id_kw = future.result()
            if result:
                results.extend(result)
            else:
                results.append({'id': f"{id_kw}", 'Numer działki': 'Not found', 'Identyfikator działki': 'Not found'})

    df = pd.DataFrame(results)
    return df

def lista_kw(start, Koniec, key):
    kw_list = []
    while start <= Koniec:
        kw = kw_generator(key, str(start))
        kw_list.append((f"{kw[0]}/{kw[1]}/{kw[2]}", kw))
        start += 1
    return kw_list

def import_kw():
    fname = QFileDialog.getOpenFileName(None, 'open file', os.path.expanduser("~/Desktop"), 'TXT File(*.txt)')
    if not fname or fname == ('', ''):
        print("File selection canceled.")
        return
    with open(fname[0], "r") as f:
        kw_list = [line.rstrip() for line in f]
    data.lista_kw = kw_list

if __name__ == "__main__":
    def run_mein():
        app = QApplication( sys.argv )
        Window = MainWindow()
        Window.show()
        sys.exit(app.exec())
    run_mein()

    img = False
    key = "GL1R"

    start = 1
    Koniec = 1
    max_workers = 3