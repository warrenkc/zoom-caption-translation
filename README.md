# zoom-caption-translation
利用google 翻譯和提供zoom 視訊會議字幕
# 方法：    
## 方法1：   
首先，使用google speech to text api將audio stream輸入成文字。接著，將輸入好的文字送入 google translate api進行翻譯。翻譯完成後，把結果傳送到zoom。    
## 方法2：
直接使用google media translate api 將audio stream翻譯成文字。翻譯完成後，把結果傳送到zoom。    

# API 成本：
考慮費用時，我們考慮以下情境：    
講者發表為時60分鐘的演講，每5秒鐘講1句話，每句話包含10個字元。每月有4次演講。按照這個想法，使用api的時間是240分鐘，共有28800字元。    
按照上述情境，以下是各個方法的成本(每月)計算，結論來說：**方法1比較便宜**  
## 方法1：    
google speech to text 共花費 (240-60)*60/15*0.006=4.32美元.   
google translate 免費（前 500,000 個字元 免費） 
## 方法2:
google media translate 共花費 (240-60)*60/15*0.068=48.96   
## google api pricing documents
google speech to text pricing doc：https://cloud.google.com/speech-to-text/pricing#enhanced_models   
google translate pricing doc：https://cloud.google.com/translate/pricing   
google media translate pricing：https://cloud.google.com/translate/media/pricing?hl=zh-TW   
