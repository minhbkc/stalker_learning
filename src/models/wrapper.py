from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from .rule_convertor import RuleConvertor

class Stalker:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.proxies = {}
        self.rule_name_to_func = {
            "skipTo": self.skip_to,
            "backTo": self.back_to,
            "backUntil": self.back_until
        }
        
    def _run_end_rule(self, end_rule, web_content):
        tag_index = -1
        tag = ""
        
        for sub_rule in end_rule:
            rule_name, tag = RuleConvertor.get_rule_info(sub_rule)
            tag_index = self.rule_name_to_func[rule_name](
                tag=tag,
                content=web_content
            )
            
            if tag_index != -1:
                break
                
        return tag_index, len(tag)
        
    def run_end_rule(self, end_rules, web_content):
        tag_index = -1
        tag_length = 0
        
        for start_rule in end_rules:
            new_tag_index, tag_length = self._run_end_rule(start_rule, web_content)
            if tag_index == -1:
                tag_index = new_tag_index
            else:
                if tag_index < new_tag_index:
                    tag_index = new_tag_index
                else:
                    tag_index = -1
            
            if tag_index == -1:
                return tag_index, tag_length
            
        return tag_index, tag_length
        
    def _run_start_rule(self, start_rule, web_content):
        """
        This function is used to run `or` rule
        """
        tag_index = -1
        
        for sub_rule in start_rule:
            rule_name, tag = RuleConvertor.get_rule_info(sub_rule)
            tag_index = self.rule_name_to_func[rule_name](
                tag=tag,
                content=web_content
            )
            
            if tag_index != -1:
                break
                
        return tag_index
        
    def run_start_rule(self, start_rules, web_content):
        tag_index = -1
        
        for start_rule in start_rules:
            new_tag_index = self._run_start_rule(start_rule, web_content)
            
            if new_tag_index == -1:
                return new_tag_index
            else:
                if tag_index == -1:
                    tag_index = new_tag_index
                else:
                    tag_index = new_tag_index + tag_index
                    
            web_content = web_content[tag_index:]
            
        return tag_index
        
    def get_elements_by_rule(self, start_rule: str, end_rule: str, web_content: str):
        start_rules = RuleConvertor.convert_str_to_rule(start_rule)
        end_rules = RuleConvertor.convert_str_to_rule(end_rule)
        results = []
        
        while True:
            start_index = self.run_start_rule(start_rules, web_content)
            print("s", start_index)
            if start_index == -1:
                break
            
            end_index, tag_length = self.run_end_rule(
                end_rules, 
                web_content[start_index:]
            )
            print("e", end_index)
            if end_index == -1:
                break
            else:
                end_index = end_index + start_index
                
            print(start_index, end_index)
            
            if end_index < start_index:
                break
                
            results.append(web_content[start_index:end_index])
            web_content = web_content[end_index + tag_length:]
            
            if web_content == "":
                break
            
        return [result.strip() for result in results]
        
    def scrape_web_content(self, url):
        base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
        response = requests.get(
            url,
            headers=self.headers,
            proxies=self.proxies,
            timeout=3
        )
        soup = BeautifulSoup(response.content, "html.parser")
        return str(soup)
    
    def skip_to(self, tag, content):
        tag_index = content.find(tag)
        return tag_index + len(tag) if tag_index != -1 else tag_index
    
    def back_to(self, tag, content):
        tag_index = content.find(tag)
        return tag_index
    
    def back_until(self, tag, content):
        tag_index = content.rfind(tag)
        return tag_index