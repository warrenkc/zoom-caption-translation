# zoom-caption-translation
利用google 翻譯和提供zoom 視訊會議字幕
# 想法：    
## 方法1：   
首先，使用google speech to text api將audio stream輸入成文字。接著，將輸入好的文字送入 google translate api進行翻譯。翻譯完成後，把結果傳送到zoom。    
## 方法2：
直接使用google media translate api 將audio stream翻譯成文字。翻譯完成後，把結果傳送到zoom。    

# API 成本：
考慮費用時，我們考慮以下情境：    
>>講者發表為時60分鐘的演講，每5秒鐘講1句話，每句話包含10個字元。每月有4次演講。按照這個想法，使用api的時間是240分鐘，共有28800字元。    
>>按照上述情境，以下是各個方法的成本(每月)計算，結論來說：**方法1比較便宜**  
## 方法1：    
google speech to text 共花費 (240-60)*60/15*0.006=4.32美元.   
google translate 免費（前 500,000 個字元 免費） 
## 方法2:
google media translate 共花費 (240-60)*60/15*0.068=48.96   
## reference 
google speech to text pricing doc：https://cloud.google.com/speech-to-text/pricing#enhanced_models   
google translate pricing doc：https://cloud.google.com/translate/pricing   
google media translate pricing：https://cloud.google.com/translate/media/pricing?hl=zh-TW   
# 已知問題：
## zoom api問題：
1. 在呼叫zoom caption api時，response 的時間太長，平均來說超過1.5秒 
2. zoom呼叫完成後，zoom caption 沒有馬上出現，有延遲的狀況（時間不一定，有時甚至好幾個caption同時出現） 
## 方法1問題：
1. 無法看到翻譯的過程，只有等待speech recognize 完成後，才傳送給google translate  

## 方法2問題：
1. google media translate 只有提供少數語言的翻譯（請詳見 language support https://cloud.google.com/translate/media/docs/languages?hl=zh-TW）
2. google media translate 屬於beta版本，物件有改變的可能
3. google media translate 無法提供原文的辨識結果
