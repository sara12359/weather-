from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.void_elements = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}

    def handle_starttag(self, tag, attrs):
        if tag not in self.void_elements:
            self.stack.append(tag)
            
    def handle_endtag(self, tag):
        if tag in self.void_elements:
            return
        if not self.stack:
            print(f"Error: Unmatched closing tag </{tag}>")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        else:
            print(f"Error: Mismatched tag: expected </{self.stack[-1]}>, got </{tag}>")
            # Try to recover by finding the tag
            if tag in self.stack:
                while self.stack[-1] != tag:
                    self.stack.pop()
                self.stack.pop()

with open('c:/Users/Admin/Desktop/weather/weather-/weather_app/templates/weather_app/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# remove django template tags just for parsing roughly
import re
content = re.sub(r'\{%[^\%]+\%\}', '', content)
content = re.sub(r'\{\{[^\}]+\}\}', '', content)

parser = MyHTMLParser()
parser.feed(content)
if parser.stack:
    print(f"Unclosed tags: {parser.stack}")
else:
    print("HTML seems well-formed.")
