# !/usr/bin/python3
# -*- coding: utf-8 -*-

import re
from ai import ai
from pwn import sleep
from random import randint
from selenium.webdriver import Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement


class Answers:
    """a class to get and fill answers"""
    def __init__(self, driver: Edge, time_lim):
        self.driver = driver
        self.time_lim = time_lim
        self.ai = ai()
     
    def __hold(self, sec: float):
        for i in range(0, int(sec) + 1, 1):
            
            try:
                cont = self.driver.find_element(By.CSS_SELECTOR,'p[class="continue-button"]')
                self.driver.execute_script("arguments[0].click();", cont)
            except Exception:
                pass
            
            sleep(1)

    def __wait(self):
        sleep(2)
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def __get_questions(self, block: WebElement):
        """get all the questions on the block"""
        blocks = block.find_elements(By.XPATH,"../*")
            
        processed = {}
        
        for m in ([i.text for i in blocks]):
            questions = re.sub(r'  ', ' [____] ', m) # match blanks
            labels = re.findall(r'\n([0-9~]+)(?=\n|$)', m) # match question labels
            
            if labels:
                if len(labels) == 1:
                    processed.update({labels[0]:questions})
                else:
                    processed.update({f"{labels[0]}~{labels[-1]}":questions})
        
        return processed

    def __fetch_all_input(self, page: WebElement):
        """find all places that needs to be filled"""
        
        types = '''
        div[class="multiplechoice cell "][data-type="1"],
        div[class="multiplechoices cell"][data-type="2"],
        div[class="multiplechoice cell "][data-type="4"],
        input[data-num_name="small_question_num"],
        div[class="writing cell"][data-type="6"]
        '''
        
        inputs = page.find_elements(By.CSS_SELECTOR, types)
        return inputs

    def __type(self, index, block: WebElement):
        """return the type of the question"""
        cell = block.find_element(By.CSS_SELECTOR, f"[data-order_num='{index}']")
        
        if cell.tag_name == "input":
            return "5"
        
        parent_element = cell.find_element(By.XPATH, '../..')
        return parent_element.get_attribute("data-type")

    def __get_choice_ab(self, cell: WebElement) -> dict:
        assert cell.get_attribute('data-type') == "1"        
        ans = cell.find_element(By.CSS_SELECTOR,'span[class="answer"]')
        label = cell.find_element(By.CSS_SELECTOR,'font[data-num_name="small_question_num"]')
        
        return {("1",label.get_attribute('data-order_num')):ans.text}

    def __get_choice_tick(self, cell: WebElement) -> dict:
        assert cell.get_attribute('data-type') == "2"        
        ans = cell.find_element(By.CSS_SELECTOR,'span[class="answer"]')
        label = cell.find_element(By.CSS_SELECTOR,'font[data-num_name="small_question_num"]')
        
        return {("2",label.get_attribute('data-order_num')):ans.text}

    def __get_choice_tf(self, cell: WebElement) -> dict:
        assert cell.get_attribute('data-type') == "4"
        ans = cell.find_element(By.CSS_SELECTOR,'span[class="answer"]')
        label = cell.find_element(By.CSS_SELECTOR,'font[data-num_name="small_question_num"]')
        
        return {("4",label.get_attribute('data-order_num')):ans.text}

    def __get_write_blank(self, cell: WebElement) -> dict:
        assert cell.get_attribute('data-type') == "5"
        ans = cell.find_elements(By.CSS_SELECTOR,'span[class="answer"]')
        question_num = cell.find_element(By.CSS_SELECTOR,'font[data-type="5"]')
        
        answers = {}
        bonds = re.findall(r'\b(\d+)~(\d+)\b', question_num.text)[0]
        labels = range(int(bonds[0]),int(bonds[1])+1)
        for index in range(0,len(labels)):
            answers.update({("5",labels[index]):ans[index].text})
        
        return answers

    def __get_write_cell(self, cell: WebElement) -> dict:
        assert cell.get_attribute('data-type') == "6"
        tex = cell.find_element(By.CSS_SELECTOR,'textarea[data-name="Answer_bearing"]')
        label = cell.find_element(By.CSS_SELECTOR,'font[data-num_name="small_question_num"]')
        
        return {("6",label.get_attribute('data-order_num')):tex.get_attribute('value')}
    
    def __get_block_ans(self, block: WebElement) -> dict:
        
        answers = {}
        
        # ABCD
        choice_cells = block.find_elements(By.CSS_SELECTOR,'div[class="multiplechoice cell "][data-type="1"]')
        for cell in choice_cells:
            answers.update(self.__get_choice_ab(cell))
        # tick
        tick_cells = block.find_elements(By.CSS_SELECTOR,'div[class="multiplechoices cell"][data-type="2"]')
        for cell in tick_cells:
            answers.update(self.__get_choice_tick(cell))
        # TF
        tf_cells = block.find_elements(By.CSS_SELECTOR,'div[class="multiplechoice cell "][data-type="4"]')
        for cell in tf_cells:
            answers.update(self.__get_choice_tf(cell))
        # blanks
        blank_cell = block.find_elements(By.CSS_SELECTOR,'div[class="cloze cell"][data-type="5"]')
        for cell in blank_cell:
            answers.update(self.__get_write_blank(cell))
        # write
        write_cell = block.find_elements(By.CSS_SELECTOR,'div[class="writing cell"][data-type="6"]')
        for cell in write_cell:
            answers.update(self.__get_write_cell(cell))
        
        return answers

    def __choose_tf(self, index, answer, block: WebElement):
        label = block.find_element(By.CSS_SELECTOR, f"[data-order_num='{index}']")
        parent_element = label.find_element(By.XPATH, '../..')
        assert parent_element.get_attribute('class') == "multiplechoice cell "
        assert parent_element.get_attribute('data-type') == "4"
        
        if answer == "T":
            data_val = "1"
        elif answer == "F":
            data_val = "2"
        
        button = parent_element.find_element(By.CSS_SELECTOR, f"div[data-name='Answer_bearing'][data-val='{data_val}']")
        
        self.driver.execute_script("arguments[0].click();", button)
        
        pass

    def __choose_ab(self, index, answer: str, block: WebElement):
        label = block.find_element(By.CSS_SELECTOR, f"[data-order_num='{index}']")
        parent_element = label.find_element(By.XPATH, '../..')
        assert parent_element.get_attribute('class') == "multiplechoice cell "
        assert parent_element.get_attribute('data-type') == "1"
    
        ans = answer[0].upper()
        data_val = ord(ans) - 64
            
        button = parent_element.find_element(By.CSS_SELECTOR, f"div[data-name='Answer_bearing'][data-val='{data_val}']")
        
        self.driver.execute_script("arguments[0].click();", button)
        pass
    
    def __choose_tick(self, index, answer: list, block: WebElement):
        label = block.find_element(By.CSS_SELECTOR, f"[data-order_num='{index}']")
        parent_element = label.find_element(By.XPATH, '../..')
        assert parent_element.get_attribute('class') == "multiplechoices cell"
        assert parent_element.get_attribute('data-type') == "2"
        
        for ans in answer:
            ans = ans[0].upper()
            data_val = ord(ans) - 64
            
            button = parent_element.find_element(By.CSS_SELECTOR,f"div[data-name='Answer_bearing'][data-val='{data_val}']")
            
            self.driver.execute_script("arguments[0].click();", button)
            
        pass
     
    def __write_cell(self, index, answer, block: WebElement):
        label = block.find_element(By.CSS_SELECTOR, f"[data-order_num='{index}']")
        parent_element = label.find_element(By.XPATH, '../..')
        assert parent_element.get_attribute('class') == "writing cell"
        assert parent_element.get_attribute('data-type') == "6"

        cell = parent_element.find_element(By.CSS_SELECTOR,'textarea[data-name="Answer_bearing"]')

        # print(cell.tag_name, cell.get_attribute('outerHTML'))
        cell.send_keys(answer)
        
        pass

    def __write_blank(self, index, answer, block: WebElement):
        blank = block.find_element(By.CSS_SELECTOR, f"[data-order_num='{index}']")
        assert blank.tag_name == "input"
        
        self.driver.execute_script(f'arguments[0].value = "{answer}";', blank)
        
        pass

    def __fill_ai_answer(self, block: WebElement, pre_answers: dict={}, time_lim: int = 0):
        """fill ai generated answer int blocks"""
        answers = [(label,ans) for label, ans in pre_answers.items()]

        while(len(answers) < len(self.__fetch_all_input(block))):
            answers.append(answers[-1])
            
        inputs = self.__fetch_all_input(block)
            
        for index in range(0,len(answers)):
            # try:
                print(f"Working on question No.{answers[index][0]}")
                print(f"Answer: {answers[index][1]}")
                
                type = inputs[0].get_attribute('data-type')
                if inputs[index].tag_name == "input":
                    ans_index = inputs[index].get_attribute("data-order_num")
                else:
                    inp = inputs[index].find_element(By.CSS_SELECTOR,'font[data-num_name="small_question_num"]')
                    ans_index = inp.get_attribute("data-order_num")
                    
                if type == "1": #ABCD
                    self.__choose_ab(ans_index,answers[index][1],block)
                elif type == "2": #tick
                    self.__choose_tick(ans_index,list(answers[index][1]),block)
                elif type == "4": #TF
                    self.__choose_tf(ans_index,answers[index][1],block)
                elif type == "5": #blanks
                    self.__write_blank(ans_index,answers[index][1],block)
                elif type == "6": #cell
                    self.__write_cell(ans_index,answers[index][1],block)
                    
                if time_lim:                        
                    self.__hold(time_lim//len(answers) + 1)
            # except Exception:
            #     continue
        
        pass

    def __fill_get_answer(self, pre_answers: dict={}):
        """fill the answer gotten from get_answer"""
        answers = [(label,ans) for label, ans in pre_answers.items()]
    
        for ans in answers:
            # try:
                print(f"Working on question No.{ans[0][1]}")
                print(f"Answer: {ans[1]}")
                
                type = ans[0][0]
                if type == "1": #ABCD
                    self.__choose_ab(ans[0][1],ans[1],self.driver)
                elif type == "2": #tick
                    self.__choose_tick(ans[0][1],list(ans[1]),self.driver)
                elif type == "4": #TF
                    self.__choose_tf(ans[0][1],ans[1],self.driver)
                elif type == "5": #blanks
                    self.__write_blank(ans[0][1],ans[1],self.driver)
                elif type == "6": #cell
                    self.__write_cell(ans[0][1],ans[1],self.driver)
                    
                sleep(10)
            # except Exception:
            #     continue

    def __get_answer(self):
        """get all answer from website"""
        # reveal answer page
        but_review = self.driver.find_element(By.CSS_SELECTOR,'input[data-name="last_result"]')
        self.driver.execute_script("arguments[0].click();", but_review)
        self.__wait()

        but_last = self.driver.find_elements(By.CSS_SELECTOR, "#view_last_vue_dom a")[0]
        self.driver.execute_script("arguments[0].click();", but_last)
        self.__wait()
        
        # check if already correct
        accuracy = self.driver.find_element(By.CSS_SELECTOR,'span[class="correct_rate"]').text
        if accuracy == 100:
            return {}
        
        # deal with it block wise
        blocks = self.driver.find_elements(By.CSS_SELECTOR,'div[class="question-detail"]')
        answers = {}
        for block in blocks:
            ans = self.__get_block_ans(block)
            answers.update(ans)
            
        # return to start page
        self.driver.execute_script("window.history.back();")
        self.__wait()
        
        return answers

    def answerby_ai(self):
        """finish the questions by ai"""
        blocks = self.driver.find_elements(By.CSS_SELECTOR, 'div[class="question-detail"]')
        
        # randomize time
        time = self.time_lim + randint(-120, 120) if self.time_lim != 0 else 0
        print(f"Time limit set: {time}")
        print(f"Total questions: {len(self.__fetch_all_input(self.driver))}")
        
        for block in blocks:
            questions = [(label,ans) for label, ans in self.__get_questions(block).items()]
            
            answers = {}
            summarize = ""
            for question in questions:
                if summarize:
                    question = list(question)
                    question[1] += f" {summarize}"
                
                # print(question)
                answer, summarize = self.ai.get_response(question)
                answers.update(answer)
                
            self.__fill_ai_answer(block,answers,time//len(blocks))

    def answerby_past(self):
        """get answer from site and answer"""
        print(f"Total questions: {len(self.__fetch_all_input(self.driver))}")
        
        ans = self.__get_answer()
        if ans:
            self.__fill_get_answer(ans)

        
        
        
        
        
        
        