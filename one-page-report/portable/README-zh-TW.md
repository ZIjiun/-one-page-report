# 通用版：給 ChatGPT、Copilot、Gemini、公司自建 AI 使用

`one-page-report-instructions.md` 是同一套方法的**單一指令檔**（約 7,970 字元，在多數平台 8,000 字的限制內）。
指令用英文寫，因為各家 AI 對英文指令的遵守度最穩定；它會用繁體中文跟你對話。

## 怎麼設定

| 平台 | 放在哪裡 |
|---|---|
| ChatGPT | 建立自訂 GPT → Configure → Instructions 貼上全文；或建立 Project → Instructions |
| Microsoft Copilot | Copilot Studio 建立代理程式 → Instructions 貼上全文 |
| Gemini | 建立 Gem → 指示 貼上全文 |
| 公司自建 AI | 放進系統提示詞（system prompt）或「角色設定」欄位 |

想要更穩定的結果，可以把這幾個檔案當作**參考檔（Knowledge／Files）**一起上傳：

- `../references/report-types.md`（各類報告的骨架與提問）
- `../references/storyline.md`（提煉邏輯的方法）
- `../references/review-checklist.md`（審稿清單）
- `../references/diagrams.md`（哪種資訊畫哪種示意圖）
- `../references/imagery.md`（圖片、主題配色、明暗主題）
- `../examples/*.json`（五組報告的完整範例，每組中英兩份）

## 和 Claude 完整版的差別

| 功能 | 完整版（Claude） | 通用版 |
|---|---|---|
| 需求訪談、提煉邏輯、選骨架 | ✓ | ✓ |
| 產出 HTML | ✓ 用腳本產生，版面穩定 | ✓ 由 AI 直接寫，品質看 AI |
| PNG、PDF | ✓ 自動輸出 | 你用瀏覽器開 HTML → 列印 → 另存 PDF，或截圖 |
| 可編輯 PPT | ✓ | 看平台能不能執行程式（ChatGPT 的進階資料分析可以） |
| 色盲檢查、自動審稿 | ✓ 腳本 | 文字規則，由 AI 自評 |
| 示意圖（路線、算式、決策樹、選項對照、步驟） | ✓ 腳本自動排版 | 由 AI 直接畫 SVG，品質看 AI |
| 明暗主題 | ✓ 每種風格都有淺色、深色 | 依指令由 AI 配色 |
| 陌生人測試 | ✓ 另開審稿 AI | AI 給你一段提示詞，你貼到新對話 |
| 手寫字體 | ✓ 內嵌 | 用系統字體（例如微軟正黑體） |

## 第一次試用

設定好之後，直接說：

> 我要做一份專案成果報告，給部門主管看，內容是……（貼上你的資料）

它應該會**先問你問題、一次一題**，最後把需求整理一遍請你確認。如果它直接開始做圖，請提醒它「先依照核心規則訪談」。

## 測試狀態

這份通用版只在 Claude 上檢查過字數與內容完整性，**沒有在 ChatGPT、Copilot、Gemini 上實測**。帶進公司後請先用一份不機密的資料試做一次。
