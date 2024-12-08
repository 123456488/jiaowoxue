# !/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
from pwn import sleep
from answers import Answers
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains



class Readoor():
    """a class to automate operations in app.readoor.cn"""
    def __init__(self) -> None:
        self.driver = None
        self.sub_proc = None
        self.finished = None
        self.unfinished = None
        self.answer = None
        self.base_lim = None
        self.by_sec = None

    def __wait(self):
        sleep(2)
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def __hold(self, sec: float):
        for i in range(0, int(sec) + 1, 1):
            
            try:
                cont = self.driver.find_element(By.CSS_SELECTOR,'p[class="continue-button"]')
                self.driver.execute_script("arguments[0].click();", cont)
            except Exception:
                pass
            
            sleep(1)

    def __switch_window(self):
        """switch to latest window"""
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])

    def __get_title(self, element: WebElement):
        """print the title of a element"""
        title = element.find_element(By.CLASS_NAME,value='model-mooc-courseware-title')
        
        return title.text

    def __fetch_unfinished(self):
        xpath='//*[@id="vue-mooc-catalog"]/div/div/div[2]'
        tree = self.driver.find_element(By.XPATH,value=xpath)
        element = tree.find_elements(By.XPATH, './*')
        
        processed = []
        for i in element:
            if i.text[:7] == "新核心大学英语":
                try:
                    status = i.find_element(By.CLASS_NAME,value='courseware-info-progress')
                    title = i.find_element(By.CLASS_NAME,value='model-mooc-courseware-title')
                except Exception:
                    continue
                
                if status.text == "未开始" and title.text[-7:] != "Part II" and title.text[-7:] != "Part IV" and title.text[-6:] != "Part V":
                    processed.append(i)
                else:
                    continue
            else:
                continue
            
        self.unfinished = processed
        
    def __fetch_finished(self):
        xpath='//*[@id="vue-mooc-catalog"]/div/div/div[2]'
        tree = self.driver.find_element(By.XPATH,value=xpath)
        element = tree.find_elements(By.XPATH, './*')
        
        processed = []
        for i in element:
            if i.text[:7] == "新核心大学英语":
                try:
                    status = i.find_element(By.CLASS_NAME,value='courseware-info-progress')
                    title = i.find_element(By.CLASS_NAME,value='model-mooc-courseware-title')
                except Exception:
                    continue
                
                if status.text == "已完成" and title.text[-7:] != "Part II" and title.text[-7:] != "Part IV" and title.text[-6:] != "Part V":
                    processed.append(i)
                else:
                    continue
            else:
                continue
            
        self.finished = processed

    def __submit(self):
        
        try:
            cont = self.driver.find_element(By.CSS_SELECTOR,'p[class="continue-button"]')
            self.driver.execute_script("arguments[0].click();", cont)
        except Exception:
            pass

        button = self.driver.find_element(By.CSS_SELECTOR, "input[type='button'][data-name='save']")
        self.driver.execute_script("arguments[0].click();", button)
        self.__wait()
        
        try:
            warn = self.driver.find_element(By.CSS_SELECTOR, 'div[class="m-dialog-view m-dialog-confirm-warning"]')
        except Exception:
            pass
        else:
            if warn.is_displayed():
                sub = warn.find_element(By.CSS_SELECTOR,'button[class="m-btn m-btn-primary"]')
                self.driver.execute_script("arguments[0].click();", sub)
                # warn.click()
                # ActionChains(self.driver).move_to_element(warn).click().perform()
                return
            
    def __save_screenshot(self, name: str):
        width = self.driver.execute_script("return document.body.scrollWidth")
        height = self.driver.execute_script("return document.body.scrollHeight")
        
        self.driver.set_window_size(width, height)
        sleep(1)
        
        # format name
        name = name.replace(" ","_").replace("-","_")
        name.replace("Unit_","U").replace("Part_","P").replace("Section_","Sec")
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d_%H%M")
        
        print(f"Result saved to {self.path}\\screenshots\\{name[13:]}~{formatted_time}.png")
        self.driver.save_screenshot(f"{self.path}\\screenshots\\{name[13:]}~{formatted_time}.png")

    def start(self, headless: bool=False, time_lim: int=0, sec_by_sec: bool=0, pic_path = "", path_to_browser = "") -> None:
        """open website and initialize"""
        self.base_lim = time_lim
        self.by_sec = sec_by_sec
        self.ptb = path_to_browser if path_to_browser else "C:\\Program Files (x86)\\Microsoft\\Edge\\Application"
        self.path = pic_path if pic_path else os.path.dirname(os.path.abspath(__file__))
        
        opt = webdriver.EdgeOptions()
        opt.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        if (headless):
            opt.add_argument("--headless") 
            sub_opt = '.\\msedge.exe --remote-debugging-port=9222 --user-data-dir="D:\\chrome\\seleniumEdge" --disable-gpu --headless'
        else:
            sub_opt = '.\\msedge.exe --remote-debugging-port=9222 --user-data-dir="D:\\chrome\\seleniumEdge" --disable-gpu'
            
        os.chdir(self.ptb)
        self.sub_proc = subprocess.Popen(sub_opt)
        
        self.driver = webdriver.Edge(options=opt)
        opt.add_argument('--disable-gpu')

        self.driver.get(r'https://app.readoor.cn/app/cs/bi/1628762066?course=Mjg4MDg2&pid=323294&tid=12379&tgid=13644')

        self.answer = Answers(self.driver,self.base_lim)
        self.__wait()

    def stop(self):
        """Close edge window and driver"""
        self.driver.quit()        
        self.sub_proc.kill()

    def finish_unfinished(self):
        if not self.unfinished:
            self.__fetch_unfinished()

        for unfinished in self.unfinished:  
            # start timer
            start_time = time.time()
            
            # prepare window
            title = self.__get_title(element=unfinished)
            print(f"Completing {title}")
            
            if self.by_sec:
                sig = ""
                while sig not in ["q", "s", "n"]:
                    print("'q' for quit, 's' for skip, 'n' for proceed on: ")
                    sig = input()
                    
                if sig == "q":
                    return
                elif sig == "s":
                    continue
            
            unfinished.click()
            self.__wait()
            self.__switch_window()
            
            # finish questions
            self.answer.answerby_ai()
            self.__wait()
            
            # check if meet time requirements
            remain = time.time() - start_time - self.base_lim
            if remain > 0:
                self.__hold(remain + 1)
            
            input()
            # submit answer
            self.__submit()
            self.__wait()
            self.__save_screenshot(title)
            
            # close and return
            self.driver.close()
            self.__switch_window()
        
    def redo_finished(self):
        if not self.finished:
            self.__fetch_finished()

        for finished in self.finished:  
            # prepare window
            title = self.__get_title(element=finished)
            print(f"Redoing {title}")
            
            if self.by_sec:
                sig = ""
                while sig != "q" or "s" or "n":
                    print("'q' for quit, 's' for skip, 'n' for proceed on: ")
                    sig = input()
                    
                if sig == "q":
                    return
                elif sig == "s":
                    continue
            
            finished.click()
            self.__wait()
            self.__switch_window()
            
            # finish questions
            self.answer.answerby_past()
            self.__wait()

            # submit answer
            try:
                self.__submit()
            except Exception:
                pass
            self.__wait()
            self.__save_screenshot(title + "_Fin")
            
            # close and return
            self.driver.close()
            self.__switch_window()

