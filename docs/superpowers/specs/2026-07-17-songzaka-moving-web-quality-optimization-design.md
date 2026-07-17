# 松坂搬家網站品質最佳化 — 設計規格

- 日期：2026-07-17
- 專案：松坂搬家一頁式官方網站
- 正式網址：`https://songzaka-moving.pages.dev/`
- 狀態：設計已核准，待使用者審閱正式規格

## 1. 背景與目標

目前網站是由 Cloudflare Pages 直接發布 `public/` 的純靜態一頁式網站。網站沒有套件相依、建置工具或後端，主要轉換行為是撥打 `0916383872` 與開啟 LINE `https://lin.ee/VOLz2Qq`。

2026-07-17 的 Lighthouse v13.4.0 基準如下：

- 行動版三次 Performance 為 72、68、73，中位數 72。
- 行動版 LCP 為 16.1、14.7、10.4 秒，中位數 14.7 秒。
- 行動版 Accessibility 95、SEO 92。
- 行動版總傳輸量約 5.17 MB，其中圖片約 4.01 MB、Google Fonts 約 1.02 MB。
- Hero 是 CSS 背景圖，瀏覽器無法從初始 HTML 優先發現；圖片交付估計可減少約 3.06 MB。
- 橘色與 LINE 綠色 CTA 使用白字時，對比分別約 2.73:1 與 2.25:1。
- `robots.txt`、`sitemap.xml` 與不存在的路徑都回傳首頁 HTML 與 `200 OK`。
- 缺少 canonical、完整 Open Graph、結構化資料與多項安全標頭。
- Gallery 燈箱缺少對話框語意、焦點限制與關閉後焦點回復。

本次目標是完整處理效能、Core Web Vitals、無障礙、SEO、安全與程式品質問題，同時保留既有品牌外觀、服務內容和轉換路徑。

## 2. 已確認的產品與內容資料

- 品牌：松坂搬家。
- 電話：`0916383872`；結構化資料使用國際格式 `+886916383872`。
- LINE：`https://lin.ee/VOLz2Qq`。
- 服務範圍：新竹以北。
- 客服時間：24 小時客服、全年無休。
- 服務：住家搬家、公司／辦公室搬遷、家具／重物搬運、廢棄物清運。
- 語言：繁體中文；文件語言標記使用 `zh-Hant-TW`。

結構化資料不得加入未確認的地址、價格、評分、評論或正式 logo。

本節的已確認資料取代 2026-07-02 原始設計文件中「雙北・桃園」與「08:00–20:00」等示意內容；後續實作與驗收一律以本規格為準。

## 3. 範圍與非目標

### 3.1 本次範圍

- 響應式圖片、LCP 與傳輸量最佳化。
- 系統字型、可讀對比、鍵盤操作、焦點管理與減少動態效果。
- 技術 SEO、Open Graph、JSON-LD、robots、sitemap、404 與 `llms.txt`。
- Cloudflare Pages 安全標頭與分層快取。
- 靜態程式品質、錯誤處理及部署前後驗證。

### 3.2 非目標

- 不加入 Node、Vite、前端框架、CMS、後端或正式建置流程。
- 不新增詢價表單、分析追蹤、多語系或新頁面內容策略。
- 不改品牌名稱、主要版面順序、電話、LINE 或已確認服務資訊。
- 不使用 Cloudflare Image Transformations 或外部圖片 CDN。
- 不重寫與本次網站品質無關的檔案。

## 4. 技術架構與檔案責任

Cloudflare Pages 繼續直接發布 `public/`，圖片衍生工作在開發階段執行，產物提交到版本控制；部署時不需要 Python 或 Pillow。

- `public/index.html`：語意結構、SEO metadata、響應式 `<picture>`、原生 `<dialog>` 與可見內容。
- `public/styles.v2.css`：系統字型、CTA 對比、焦點、減少動態、響應式圖片及 Dialog 樣式。
- `public/main.v2.js`：Dialog 開關、焦點回復、圖片錯誤狀態與 FAQ 單一展開。
- `scripts/blur.py`：讀取原始照片、依 EXIF 轉正、遮蔽敏感區域、裁切、縮放、編碼及驗證。
- `public/images/web/`：只放網站使用的衍生圖片，不放原始照片。
- `public/_headers`：安全標頭、HTML 重新驗證與版本化資源長快取。
- `public/robots.txt`、`public/sitemap.xml`、`public/404.html`、`public/llms.txt`：搜尋索引與錯誤處理。

原始 `images/` 永遠只讀。若要更新照片，必須從原始檔重新產生，不可對已壓縮產物反覆編碼。

## 5. 圖片資料流與效能設計

### 5.1 處理順序

每張圖片依以下固定順序處理：

1. 讀取來源並套用 EXIF orientation。
2. 在完整解析度上套用既有的人臉、車牌與他牌招牌遮蔽座標。
3. 依顯示用途裁切或保留原始比例。
4. 產生 WebP 與 JPEG fallback。
5. 驗證來源存在、座標在範圍內、輸出尺寸與格式正確，且檔案大小不為零。

任一工作失敗時，腳本須顯示來源與輸出名稱、停止處理並回傳非零狀態，不得留下看似成功的不完整產物。

### 5.2 尺寸與檔名

靜態資源採版本檔名；本次使用 `v2`。未來只要內容改變，就必須提高版本，不能覆寫仍設定 immutable 的檔案。

- Hero：16:9，寬度 640、1280、1600；例如 `hero-v2-1280.webp` 與同名 `.jpg`。
- 服務卡：4:3，寬度 480、800；例如 `svc-home-v2-800.webp`。
- Gallery 縮圖：4:3，寬度 320、640；例如 `g01-v2-640.webp`。
- Gallery 燈箱：保留原始比例，最大寬度 1280；例如 `g01-v2-1280.webp`。
- 社群分享圖：1200 × 630 JPEG，檔名 `og-songzaka-v2-1200x630.jpg`。

JPEG 是不支援 WebP 時的 fallback；現代瀏覽器只下載 `<picture>` 選中的一種格式。

### 5.3 載入策略

Hero 從 CSS 背景改為初始 HTML 中的 `<picture>`，圖片置於文字與漸層遮罩後方。Hero 圖為裝飾用途，使用空 `alt`，但仍保留實際 `<img>` 以成為可優先發現的 LCP 候選；設定 `fetchpriority="high"`、`loading="eager"`、`srcset`、`sizes`、`width` 與 `height`。

服務與 Gallery 縮圖使用 `<picture>`、明確尺寸、`loading="lazy"` 與 `decoding="async"`。Gallery 的 1280 圖只有在開啟 Dialog 時才載入。圖片替代文字必須描述可見的搬運工作、物品或場景，不得只寫「實績照片 1」等編號。

效能預算如下：

- 行動裝置選中的 Hero 資源不超過 250 KB。
- 首次行動版頁面傳輸量目標不超過 1.5 MB。
- 燈箱圖片不計入首次載入，僅在使用者操作後請求。

## 6. 視覺、互動與無障礙設計

### 6.1 字型、對比與焦點

移除 Google Fonts、preconnect 與第三方字型請求。全站使用：

`system-ui, -apple-system, "PingFang TC", "Microsoft JhengHei", sans-serif`

保留亮橘 `#F5793B` 與 LINE 綠 `#06C755` 背景，CTA 文字改成深藍 `#0F2A4A`。預估對比分別為 5.30:1 與 6.42:1，符合一般文字 WCAG AA。

所有互動元件至少 44 × 44 CSS px，並提供不依賴色彩的 `:focus-visible` 外框。Hover 效果要有等效 Focus 狀態。Sticky header 與固定手機 CTA 不得遮住錨點或鍵盤焦點；手機 CTA 納入 `env(safe-area-inset-bottom)`，頁面底部保留等高空間。

### 6.2 文件與鍵盤導覽

- `<body>` 第一個可聚焦元件是「跳到主要內容」連結，指向 `<main id="main-content" tabindex="-1">`。
- 維持單一 H1 與依序的 H2、H3 階層。
- Emoji 包在 `aria-hidden="true"` 的元素中，螢幕閱讀器只朗讀文字。
- LINE 新分頁連結保留 `rel="noopener"`，可讀名稱說明會開啟 LINE。
- 在 `prefers-reduced-motion: reduce` 下停用平滑捲動、Gallery 放大與非必要 transition。
- 頁面在 320px 寬度及 200% 放大時不得產生內容型水平捲動。

### 6.3 Gallery Dialog

現有自製 `.lightbox` 攝影遮罩改為原生 `<dialog>` 並透過 `showModal()` 開啟；以 `aria-labelledby` 連結標題、`aria-describedby` 連結實績說明。Dialog 包含：

- 一個供輔助科技使用的標題。
- 響應式 `<picture>` 與實績說明文字。
- 至少 44 × 44 px、具明確名稱的關閉按鈕。
- 一個預設隱藏、圖片載入失敗時顯示且可朗讀的錯誤訊息。

每個 Gallery 縮圖都是 `<button>`，可讀名稱採「放大檢視：＋具體場景描述」。開啟後焦點移到關閉按鈕；Escape、關閉按鈕或真正的 backdrop 點擊皆可關閉；關閉後焦點回到原縮圖。錯誤狀態不得移除關閉能力。程式使用 `textContent`、屬性更新及 class 切換，不使用 `innerHTML` 或 inline style。

FAQ 繼續使用原生 `<details>/<summary>`；JavaScript 只維持一次開啟一題，不覆寫原生鍵盤行為。

## 7. SEO 與搜尋索引

### 7.1 首頁 metadata

- Canonical：`https://songzaka-moving.pages.dev/`
- Title：`新竹以北搬家公司｜搬家與廢棄物清運｜松坂搬家`
- Description：`松坂搬家提供新竹以北住家搬家、公司搬遷、家具重物搬運與廢棄物清運服務。24 小時客服、全年無休，歡迎致電 0916383872 或加 LINE 免費估價。`
- Robots：`index, follow, max-image-preview:large`
- Open Graph：`og:type=website`、`og:locale=zh_TW`、title、description、canonical `og:url`、絕對 `og:image`、1200 × 630 尺寸與圖片描述。
- Twitter Card：`summary_large_image`，沿用相同標題、描述與絕對圖片網址；不虛構社群帳號。

所有 metadata 必須與可見內容一致。

### 7.2 JSON-LD

首頁加入兩組 JSON-LD：

1. `MovingCompany`：包含穩定 `@id`、名稱、正式網址、國際格式電話、社群圖片、`areaServed`「新竹以北」與 24 小時全年無休的客服 `ContactPoint`。
2. `FAQPage`：逐字對應頁面可見的四個問題與答案，不加入未顯示的問答。

不加入 postal address、priceRange、aggregateRating、review、logo 或其他未確認資料。

### 7.3 robots、sitemap、404 與 llms

`robots.txt` 允許所有一般爬蟲存取並以絕對網址指向 Sitemap，不額外封鎖 AI 搜尋爬蟲：

```text
User-agent: *
Allow: /

Sitemap: https://songzaka-moving.pages.dev/sitemap.xml
```

`sitemap.xml` 只列 canonical 首頁。`lastmod` 使用實際修改可見內容或 metadata 的日期；不加入無法準確維護的 `changefreq` 與 `priority`。

新增頂層 `404.html`，包含 `noindex, follow`、錯誤說明、返回首頁、撥電話與 LINE 入口。Cloudflare Pages 部署後必須確認任意不存在路徑回傳真正 `404`，而非首頁 `200`。

`llms.txt` 只提供網站名稱、首頁、主要服務、服務範圍與聯絡方式的簡短 Markdown 索引。它是低成本實驗性檔案，不宣稱能改善排名或 AI 引用。

## 8. 安全標頭與快取

### 8.1 安全標頭

`public/_headers` 對所有路徑加入：

```text
Content-Security-Policy: default-src 'self'; base-uri 'self'; object-src 'none'; frame-src 'none'; frame-ancestors 'none'; form-action 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; media-src 'none'; manifest-src 'self'; upgrade-insecure-requests; require-trusted-types-for 'script'; trusted-types 'none'
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Cross-Origin-Opener-Policy: same-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
```

不加入 COEP，因網站不需要 cross-origin isolation。CSP 不使用萬用來源、`unsafe-inline` 或 `unsafe-eval`。若預覽部署發現相容問題，只加入實際需要的最小來源。

### 8.2 快取

- `/`、HTML、`robots.txt`、`sitemap.xml` 與 `llms.txt`：`public, max-age=0, must-revalidate`。
- `styles.v2.css`、`main.v2.js`、`favicon-v2.svg` 與 `images/web/*-v2-*`：`public, max-age=31536000, immutable`。

版本化檔案一旦發布不得原地替換；內容變更時提高版本並同步更新 HTML 引用。

## 9. 錯誤處理與回復策略

- 圖片產生錯誤：腳本停止、清楚列出失敗項目、不覆寫原始照片。
- 燈箱圖片錯誤：顯示可朗讀訊息並保留關閉與焦點回復。
- JavaScript 不可用：電話、LINE、主要內容與 FAQ 原生展開仍可使用，Gallery 縮圖仍可見；只有放大 Dialog 與 FAQ 單一展開功能停用。
- CSP 問題：先在預覽部署檢查瀏覽器 console，再最小化放寬；不得為了消除錯誤直接取消 CSP。
- 視覺回復：舊 `styles.css`、`main.js` 與舊 `public/images/web/*.jpg` 在切換完成前保留；本機驗收通過後移除未引用的舊產物，必要時可由 Git 回復。原始 `images/` 永不刪除。

## 10. 驗證與完成標準

### 10.1 靜態與資產檢查

- 圖片腳本對全部工作成功執行兩次，第二次結果具決定性，且所有輸出通過尺寸、格式與非空檢查。
- 沒有 Google Fonts、`console.log`、失效內部連結、重複 ID、泛用 Gallery alt 或未設定尺寸的內容圖片。
- HTML、CSS、JavaScript 與 JSON-LD 通過適用的語法／結構驗證。
- canonical、Open Graph、Twitter Card 與 Sitemap 全部使用正式 HTTPS 網址。
- 行動裝置選中的 Hero 不超過 250 KB，首次頁面傳輸量不超過 1.5 MB。

### 10.2 手動無障礙與互動檢查

- 純鍵盤完成 Skip Link、Header CTA、Gallery Dialog、FAQ 與手機固定 CTA 操作。
- 驗證 Dialog 焦點進入、Escape、backdrop、關閉後焦點回復及圖片錯誤訊息。
- 用 VoiceOver 檢查頁面標題、地標、圖片、按鈕名稱與 Dialog 語意。
- 在 320、375、768 與 1440 px 視窗檢查版面；另測試 200% 放大與 reduced motion。
- CTA 文字與背景至少達 4.5:1；焦點指示至少達 3:1。

### 10.3 Lighthouse 驗收

在相同 Lighthouse v13.x 行動裝置設定執行三次並採中位數：

- Performance ≥ 90。
- Accessibility、SEO、Best Practices 目標 100，且不得保留已知高嚴重度問題。
- LCP ≤ 2.5 秒。
- CLS ≤ 0.1。
- TBT ≤ 200 毫秒。

另執行一次桌面 Lighthouse 與瀏覽器視覺檢查。若分數因網路或執行環境波動，優先以三次中位數、LCP、CLS、TBT、請求鏈與資源大小判斷，不以單次低分直接結案或任意降低門檻。

### 10.4 部署後驗收

- `robots.txt` 與 `sitemap.xml` 回傳預期內容與合適 Content-Type。
- 不存在路徑回傳 `404`；首頁、CSS、JS 與圖片回傳預期快取標頭。
- CSP、HSTS、COOP、frame control、Trusted Types、Referrer Policy 與 Permissions Policy 實際出現在回應。
- 正式網址沒有混合內容、CSP 錯誤、console error 或失敗資源。
- 使用 Schema.org Validator 或 Google Rich Results Test 驗證 JSON-LD。
- 重新掃描正式網址並保存與本文件基準可比較的 Lighthouse 報告。

若實作階段沒有 Cloudflare Pages 預覽或部署權限，須明確將部署後項目列為待驗收，不能把本機結果宣稱為線上完成。

## 11. 建議實作順序

1. 擴充並驗證圖片腳本，產生 `v2` 衍生圖片。
2. 建立 `styles.v2.css` 與 `main.v2.js`，更新 HTML 結構、圖片與互動。
3. 加入 SEO metadata、JSON-LD、robots、sitemap、404 與 llms。
4. 更新 `_headers`，完成本機靜態、視覺、鍵盤與 Lighthouse 驗證。
5. 在 Cloudflare Pages 預覽或正式部署後驗證狀態碼、安全標頭與線上 Lighthouse。

每一步都應保持網站可開啟、電話與 LINE 可使用，並在進入下一步前修正該階段的失敗。
