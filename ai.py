#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import json
import os
import re
import simplejson as json
from openai import OpenAI


class ai:
    """github ai"""
    def __init__(self):
        self.get_key()
        
    def get_key(self):
        path = os.path.dirname(os.path.abspath(__file__))
        
        try:
            with open(f"{path}/key.json","r") as fd:
                data = json.load(fd)
                self.api_key = data['api_key']
                self.base_url = data['base_url']
        except Exception:
            print("api key not found")
            self.api_key = input("please input api key: ")
            self.base_url = input("please input base url: ")
            with open(f"{path}/key.json","w") as fd:
                json.dump({
                    "api_key":self.api_key,
                    "base_url":self.base_url
                },fd)
        
    def get_summarization(self,context: str) -> str:
        client = OpenAI(
            api_key = self.api_key,
            base_url = self.base_url
        )
        
        completion = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {"role": "system", "content": "You are an intelligent assistant skilled in English who can conduct online searches for accurate answers. Summarize just the topic of the following conversations."
                },
                {"role": "user", "content": f"{context}"}
            ],
            temperature = 0.3,
        )
        
        response = completion.choices[0].message.content
        
        return response

    def get_response(self, question: tuple) -> dict:
        client = OpenAI(
            api_key = self.api_key,
            base_url = self.base_url
        )
        
        completion = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {
                "role": "system",
                "content": "You are an intelligent and highly proficient assistant skilled in English, capable of conducting online searches and providing accurate, well-researched answers. Your task is to respond to each question in **JSON format**, ensuring that every question is answered individually and labeled correctly. No questions should be omitted under any circumstances. Follow these improved guidelines to ensure precision and completeness:\n\n1. **Answer Format and Question Types**: Match each answer exactly to the type of question being asked. Strictly adhere to the following conventions:\n   - **True/False (T/F)**: Respond with 'T' or 'F' only.\n   - **Multiple-Choice (A/B/C/D)**: Provide the correct option (e.g., 'A', 'B', etc.).\n   - **Fill-in-the-Blank**: Directly complete the blank with the most accurate word(s) from the context, without adding summaries, interpretations, or unrelated text. Ensure the answer fits grammatically and logically into the blank.\n   - **Discussion/Opinion-Based**: Provide a detailed and reasoned explanation or opinion, ensuring it is relevant to the question.\n   - **Numerical or Short Answers**: Provide the exact number, value, or short response as required without elaboration unless the question explicitly asks for justification.\n\n2. **Completeness**: \n- Address **every single question**. Do not skip or omit any question, even if the input is unclear or complex.\n- If a question cannot be answered due to insufficient context, explicitly state: \"I don't know\" However, this should only be used as a last resort.\n\n3. **Context Handling**: \n- If prior context is provided, integrate it carefully and ensure all responses align with it.\n- Avoid summarizing or paraphrasing the context unless explicitly instructed. For fill-in-the-blank questions, use the context directly to complete the blank accurately.\n\n4. **Formatting Requirements**: \n- Respond in strict JSON format, ensuring all brackets, commas, and quotation marks are properly placed.\n- Use the question number as the key (e.g., \"3\") and the answer as the value (e.g., \"answer3\").\n- Example response: {\"3\": \"answer3\", \"4\": \"T\", \"5\": \"A\", \"6\": \"Your(NOT the user's) detailed opinion.\", \"7\": \"completed blank\"}.\n- Each answer must be a **direct match** to the type of question, with no extraneous text or deviations.\n\n5. **Error Prevention**:\n- Double-check that each question is answered exactly once and matches the type of question.\n- Avoid inserting summaries, interpretations, or unrelated text into answers, especially for fill-in-the-blank or short-answer questions.\n- Ensure strict adherence to JSON syntax to avoid formatting errors.\n\nYour primary goal is to provide **accurate, context-aware, type-specific, and well-formatted responses** for every question. If the input contains a numbered list of questions (e.g., '[question No.3~13]: ...'), respond to each systematically and confirm that no answers are missed. If clarification is needed, prioritize consistency, clarity, and accuracy in your responses."
                },
                {"role": "user", "content": f"[question No.{question[0]}]:\n{question[1]}"}
            ],
            temperature = 0.3,
        )
        
        response = completion.choices[0].message.content
        summarize = self.get_summarization(question[1])
        # print(response)
        
        # convert into json
        answers = re.findall(r'(\{.*\})', response, re.DOTALL)[0]
        # answers = answers.replace("'", '"')
        # print(repr(answers))
        
        ans_dict = json.loads(answers)

        return ans_dict, summarize
