# 松坂搬家 一頁式介紹網站 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page, mobile-first static marketing website for 松坂搬家 (moving & waste-removal) with services, gallery, FAQ, and one-tap phone/LINE contact.

**Architecture:** Pure static site — one `index.html`, one `styles.css`, one `main.js`, plus a one-off Python/Pillow script (`scripts/blur.py`) that produces privacy-masked photos into `images/web/`. No framework, no build step, no backend. Deployable to Netlify / Cloudflare Pages / GitHub Pages.

**Tech Stack:** HTML5, CSS3 (custom properties, flexbox, grid, mobile-first), vanilla JS (ES6), Python 3 + Pillow (image masking only), Google Fonts "Noto Sans TC".

## Global Constraints

- **Language:** Traditional Chinese (zh-Hant) only. `<html lang="zh-Hant">`.
- **Brand (single):** 「松坂搬家」only. Do NOT display 松和環保有限公司 anywhere.
- **Phone:** `0916383872` — links use `tel:0916383872`.
- **LINE official:** `https://lin.ee/VOLz2Qq` — opens in new tab (`target="_blank" rel="noopener"`).
- **Placeholder copy (editable, marked in HTML comments):** service area = 「雙北・桃園」; business hours = 「週一至週日 08:00–20:00」.
- **Color tokens (CSS custom properties):**
  - `--navy: #0F2A4A` (deep blue, primary dark)
  - `--blue: #1E5AA8` (primary)
  - `--blue-bright: #2E7BD6` (accent)
  - `--phone: #F5793B` (phone CTA, high-contrast orange)
  - `--line: #06C755` (LINE brand green)
  - `--bg: #F5F7FA` (light section bg)
  - `--ink: #1A2230` (body text)
  - `--muted: #667085` (secondary text)
  - `--white: #FFFFFF`
- **Images:** originals in `images/` are READ-ONLY (never modify). Site references only `images/web/`.
- **Accessibility:** every `<img>` has meaningful `alt`; icon-only buttons have `aria-label`; images use `loading="lazy"` except the hero; keyboard-operable lightbox and FAQ.
- **No form / no backend / no analytics / no multi-page.** Contact is click-to-call and LINE only.

---

## File Structure

```
/
├─ index.html          # entire page markup (all sections)
├─ styles.css          # all styles, mobile-first + tokens
├─ main.js             # nav toggle, lightbox, FAQ accordion, smooth scroll
├─ scripts/blur.py     # one-off: mask faces/plates/logos → images/web/
├─ images/             # 25 original JPGs (read-only)
├─ images/web/         # processed/masked JPGs the site uses
├─ netlify.toml        # optional deploy config (static root)
└─ docs/superpowers/…  # spec + this plan
```

**Verification model:** This is a static site with no unit-test runtime. Each task's "test" is a concrete, observable check: serve locally with `python3 -m http.server 8000` and open `http://localhost:8000`, confirm the described element renders and the browser console is error-free. Where a Python script is written, it has a real assertion-based check.

---

### Task 1: Project scaffold + local preview

**Files:**
- Create: `index.html`
- Create: `styles.css`
- Create: `main.js`
- Create: `.gitignore`

**Interfaces:**
- Produces: base HTML document with `<html lang="zh-Hant">`, linked `styles.css` and `main.js`, a `<main>` with empty anchored `<section>` stubs (`#hero`, `#services`, `#why`, `#gallery`, `#faq`, `#contact`), and the CSS `:root` token block from Global Constraints. Later tasks fill each section.

- [ ] **Step 1: Create `.gitignore`**

```
.DS_Store
scratchpad/
__pycache__/
*.pyc
```

- [ ] **Step 2: Create `index.html` skeleton**

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>松坂搬家 ｜ 專業搬家・廢棄物清運</title>
  <meta name="description" content="松坂搬家提供住家搬家、公司辦公室搬遷、家具重物搬運與廢棄物清運。細心包裝、準時到府、透明報價。電話 0916383872 或加 LINE 詢價。">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <!-- header injected in Task 3 -->
  <main>
    <section id="hero"></section>
    <section id="services"></section>
    <section id="why"></section>
    <section id="gallery"></section>
    <section id="faq"></section>
    <section id="contact"></section>
  </main>
  <!-- floating mobile bar injected in Task 8 -->
  <script src="main.js"></script>
</body>
</html>
```

- [ ] **Step 3: Create `styles.css` with token block + reset**

```css
:root {
  --navy: #0F2A4A; --blue: #1E5AA8; --blue-bright: #2E7BD6;
  --phone: #F5793B; --line: #06C755; --bg: #F5F7FA;
  --ink: #1A2230; --muted: #667085; --white: #FFFFFF;
  --maxw: 1120px; --radius: 14px; --shadow: 0 6px 24px rgba(15,42,74,.10);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; scroll-padding-top: 72px; }
body { font-family: "Noto Sans TC", system-ui, -apple-system, "PingFang TC", sans-serif;
  color: var(--ink); line-height: 1.7; background: var(--white); }
img { max-width: 100%; display: block; }
a { color: inherit; text-decoration: none; }
.container { width: min(100% - 32px, var(--maxw)); margin-inline: auto; }
.section { padding: 56px 0; }
.section-title { font-size: clamp(24px, 5vw, 34px); font-weight: 900;
  color: var(--navy); text-align: center; margin-bottom: 8px; }
.section-sub { text-align: center; color: var(--muted); margin-bottom: 32px; }
```

- [ ] **Step 4: Create `main.js` stub**

```js
// main.js — interactions wired up in later tasks
document.addEventListener('DOMContentLoaded', () => {
  console.log('松坂搬家 site loaded');
});
```

- [ ] **Step 5: Serve and verify**

Run: `python3 -m http.server 8000`
Open `http://localhost:8000` — Expected: blank page, no console errors, console shows "松坂搬家 site loaded", `<html lang="zh-Hant">` present in Elements.

- [ ] **Step 6: Commit**

```bash
git add .gitignore index.html styles.css main.js
git commit -m "chore: scaffold static site with tokens and section stubs"
```

---

### Task 2: Photo masking script → images/web/

**Files:**
- Create: `scripts/blur.py`

**Interfaces:**
- Produces: masked/optimized JPGs in `images/web/` for every image the site uses. Site tasks reference these filenames: `hero.jpg`, `svc-home.jpg`, `svc-office.jpg`, `svc-heavy.jpg`, `svc-waste.jpg`, plus `g01.jpg … gNN.jpg` for the gallery. `blur.py` maps source → output name and applies rectangular Gaussian-blur regions.

**Reference (from photo inventory / spec §6):**
- Hero source: `S__52854819_0.jpg` → `hero.jpg` (no face; keep as-is aside from optional light crop).
- Service cards: `S__52854796_0.jpg`→`svc-home.jpg`; `S__52854810_0.jpg`→`svc-office.jpg` (blur masked worker's face); `S__52854811_0.jpg`→`svc-heavy.jpg` (no person); `S__52854812_0.jpg`→`svc-waste.jpg` (blur plate).
- Gallery sources (blur where noted): 796, 797(plate), 798, 800(plate), 803, 804, 806(face), 810(face), 811, 812(plate), 816, 819, 822(KFC/台新 signage). → `g01.jpg`…
- Do NOT use: 802 (skewed), 815 (low-res), 823 (bare-chest/face), 801/820/821 (heavy face/other-brand — exclude to keep masking simple).

- [ ] **Step 1: Install Pillow**

Run: `python3 -m pip install Pillow`
Expected: "Successfully installed pillow-…"

- [ ] **Step 2: Write `scripts/blur.py`**

Regions are expressed as fractions of width/height so they're resolution-independent. The `REGIONS` dict is filled by viewing each flagged source once (see Step 3).

```python
#!/usr/bin/env python3
"""Mask faces / plates / other-brand signage and export web images.
Originals in images/ are never modified; outputs go to images/web/."""
import os
from PIL import Image, ImageFilter

SRC = "images"
OUT = "images/web"
MAXW = 1600  # cap width for web

# output_name: (source_file, [ (x, y, w, h) as fractions of image w/h ])
# empty list = no masking, just re-encode/resize.
JOBS = {
    "hero.jpg":      ("S__52854819_0.jpg", []),
    "svc-home.jpg":  ("S__52854796_0.jpg", []),
    "svc-office.jpg":("S__52854810_0.jpg", []),  # + face region below
    "svc-heavy.jpg": ("S__52854811_0.jpg", []),
    "svc-waste.jpg": ("S__52854812_0.jpg", []),   # + plate region below
    "g01.jpg": ("S__52854819_0.jpg", []),
    "g02.jpg": ("S__52854797_0.jpg", []),         # + plate
    "g03.jpg": ("S__52854798_0.jpg", []),
    "g04.jpg": ("S__52854800_0.jpg", []),         # + plate
    "g05.jpg": ("S__52854803_0.jpg", []),
    "g06.jpg": ("S__52854804_0.jpg", []),
    "g07.jpg": ("S__52854806_0.jpg", []),         # + face
    "g08.jpg": ("S__52854811_0.jpg", []),
    "g09.jpg": ("S__52854812_0.jpg", []),         # + plate
    "g10.jpg": ("S__52854816_0.jpg", []),
    "g11.jpg": ("S__52854822_0.jpg", []),         # + signage
}

# Masking regions filled after viewing each source (Step 3). Keyed by SOURCE file.
# Values: list of (x, y, w, h) fractions in [0,1].
REGIONS = {
    # "S__52854810_0.jpg": [(0.62, 0.40, 0.18, 0.16)],  # example: worker face
}

def mask(img, regions):
    for (fx, fy, fw, fh) in regions:
        W, H = img.size
        box = (int(fx*W), int(fy*H), int((fx+fw)*W), int((fy+fh)*H))
        region = img.crop(box)
        # strong blur so features are unrecoverable
        region = region.filter(ImageFilter.GaussianBlur(radius=max(box[2]-box[0], box[3]-box[1]) // 8 + 8))
        img.paste(region, box)
    return img

def process():
    os.makedirs(OUT, exist_ok=True)
    for out_name, (src_name, _) in JOBS.items():
        src_path = os.path.join(SRC, src_name)
        img = Image.open(src_path).convert("RGB")
        img = mask(img, REGIONS.get(src_name, []))
        if img.width > MAXW:
            h = int(img.height * MAXW / img.width)
            img = img.resize((MAXW, h), Image.LANCZOS)
        img.save(os.path.join(OUT, out_name), "JPEG", quality=82, optimize=True)
        print(f"wrote {out_name} <- {src_name} regions={len(REGIONS.get(src_name, []))}")

if __name__ == "__main__":
    process()
```

- [ ] **Step 3: Fill masking regions by viewing sources**

For each source marked "+ face/plate/signage" above, open it (image viewer or Read tool) and note the bounding box of the sensitive area as fractions of the image width/height, then add an entry to `REGIONS`. Sources needing regions: `S__52854810_0.jpg` (face), `S__52854812_0.jpg` (plate), `S__52854797_0.jpg` (plate), `S__52854800_0.jpg` (plate), `S__52854806_0.jpg` (face), `S__52854822_0.jpg` (KFC/台新 signage). Add a small margin around each box.

- [ ] **Step 4: Run the script**

Run: `python3 scripts/blur.py`
Expected: one "wrote …" line per JOB; `images/web/` now contains hero.jpg, svc-*.jpg, g01–g11.jpg.

- [ ] **Step 5: Verify masking visually**

Open each masked output in `images/web/` and confirm faces/plates/signage are unreadable and no un-masked sensitive area remains. If a box is off, adjust the fraction in `REGIONS` and re-run Step 4.

- [ ] **Step 6: Commit**

```bash
git add scripts/blur.py images/web
git commit -m "feat: add photo masking script and processed web images"
```

---

### Task 3: Header + Hero

**Files:**
- Modify: `index.html` (header before `<main>`; fill `#hero`)
- Modify: `styles.css` (append header + hero styles)

**Interfaces:**
- Consumes: `images/web/hero.jpg`; color tokens.
- Produces: sticky `<header class="site-header">` with brand text 「松坂搬家」and two contact links (`.btn-phone` → `tel:0916383872`, `.btn-line` → LINE url). Hero uses `#hero` with background `hero.jpg` + dark overlay, `<h1>`, slogan, and two CTA buttons reusing `.btn-phone`/`.btn-line` classes.

- [ ] **Step 1: Add header markup** (insert immediately after `<body>`)

```html
<header class="site-header">
  <div class="container header-inner">
    <a href="#hero" class="brand">松坂搬家</a>
    <nav class="header-cta">
      <a class="btn btn-phone" href="tel:0916383872" aria-label="撥打電話 0916383872">📞 撥電話</a>
      <a class="btn btn-line" href="https://lin.ee/VOLz2Qq" target="_blank" rel="noopener" aria-label="加入 LINE 好友詢價">💬 加 LINE</a>
    </nav>
  </div>
</header>
```

- [ ] **Step 2: Fill `#hero`**

```html
<section id="hero" class="hero">
  <div class="hero-overlay"></div>
  <div class="container hero-content">
    <h1>松坂搬運搬家 ＆ 廢棄物清運</h1>
    <p class="hero-slogan">專業搬遷團隊，從打包到清運一次搞定</p>
    <div class="hero-cta">
      <a class="btn btn-phone btn-lg" href="tel:0916383872">📞 撥打 0916383872</a>
      <a class="btn btn-line btn-lg" href="https://lin.ee/VOLz2Qq" target="_blank" rel="noopener">💬 加 LINE 免費估價</a>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Append header + button + hero styles to `styles.css`**

```css
.site-header { position: sticky; top: 0; z-index: 50; background: rgba(255,255,255,.95);
  backdrop-filter: blur(6px); box-shadow: 0 2px 12px rgba(15,42,74,.08); }
.header-inner { display: flex; align-items: center; justify-content: space-between; height: 64px; }
.brand { font-weight: 900; font-size: 22px; color: var(--navy); letter-spacing: 1px; }
.header-cta { display: flex; gap: 8px; }
.btn { display: inline-flex; align-items: center; gap: 6px; font-weight: 700;
  padding: 10px 16px; border-radius: 999px; white-space: nowrap; transition: transform .1s, filter .1s; }
.btn:active { transform: scale(.97); }
.btn-phone { background: var(--phone); color: #fff; }
.btn-line { background: var(--line); color: #fff; }
.btn-lg { padding: 15px 26px; font-size: 17px; }
.hero { position: relative; min-height: 78vh; display: grid; place-items: center;
  background: url("images/web/hero.jpg") center/cover no-repeat; color: #fff; text-align: center; }
.hero-overlay { position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(15,42,74,.55), rgba(15,42,74,.78)); }
.hero-content { position: relative; padding: 40px 0; }
.hero h1 { font-size: clamp(28px, 7vw, 52px); font-weight: 900; line-height: 1.25;
  text-shadow: 0 2px 16px rgba(0,0,0,.4); }
.hero-slogan { font-size: clamp(16px, 3.5vw, 22px); margin: 16px 0 28px; opacity: .95; }
.hero-cta { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }
@media (max-width: 480px) {
  .brand { font-size: 19px; }
  .btn { padding: 9px 12px; font-size: 14px; }
  .header-cta .btn span, .header-cta .btn { }
}
```

- [ ] **Step 4: Serve and verify**

Open `http://localhost:8000` — Expected: sticky header with 松坂搬家 + two buttons; full-width hero photo with dark overlay, white title, slogan, two large CTAs. `tel:` link shows call prompt on hover/click; LINE opens new tab. No console errors.

- [ ] **Step 5: Commit**

```bash
git add index.html styles.css
git commit -m "feat: add sticky header and hero with contact CTAs"
```

---

### Task 4: Services section

**Files:**
- Modify: `index.html` (fill `#services`)
- Modify: `styles.css`

**Interfaces:**
- Consumes: `images/web/svc-home.jpg`, `svc-office.jpg`, `svc-heavy.jpg`, `svc-waste.jpg`.
- Produces: `#services` with a responsive `.service-grid` of four `.service-card`.

- [ ] **Step 1: Fill `#services`**

```html
<section id="services" class="section">
  <div class="container">
    <h2 class="section-title">服務項目</h2>
    <p class="section-sub">搬家與清運一條龍，一通電話全部搞定</p>
    <div class="service-grid">
      <article class="service-card">
        <img src="images/web/svc-home.jpg" alt="住家搬家：電梯口包裝保護好的家具" loading="lazy">
        <div class="service-body"><h3>住家搬家</h3>
          <p>套房、公寓、透天住家搬遷，細心包裝家具家電，快速確實。</p></div>
      </article>
      <article class="service-card">
        <img src="images/web/svc-office.jpg" alt="公司辦公室搬遷：大樓走廊搬運設備" loading="lazy">
        <div class="service-body"><h3>公司／辦公室搬遷</h3>
          <p>辦公桌椅、設備、文件整批搬遷，配合時段減少營運影響。</p></div>
      </article>
      <article class="service-card">
        <img src="images/web/svc-heavy.jpg" alt="家具重物搬運：完整包覆保護的大型家具" loading="lazy">
        <div class="service-body"><h3>家具／重物搬運</h3>
          <p>鋼琴、保險箱、大型家電等重物專業搬運，安全就定位。</p></div>
      </article>
      <article class="service-card">
        <img src="images/web/svc-waste.jpg" alt="廢棄物清運：工地與大型廢棄物清運" loading="lazy">
        <div class="service-body"><h3>廢棄物清運</h3>
          <p>舊家具、大型垃圾、裝潢廢棄物清除，快速估價、環保處理。</p></div>
      </article>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Append styles**

```css
#services { background: var(--bg); }
.service-grid { display: grid; gap: 20px; grid-template-columns: 1fr; }
.service-card { background: #fff; border-radius: var(--radius); overflow: hidden;
  box-shadow: var(--shadow); }
.service-card img { width: 100%; height: 200px; object-fit: cover; }
.service-body { padding: 18px 20px 22px; }
.service-body h3 { color: var(--navy); font-size: 20px; margin-bottom: 8px; }
.service-body p { color: var(--muted); }
@media (min-width: 640px) { .service-grid { grid-template-columns: 1fr 1fr; } }
@media (min-width: 1000px) { .service-grid { grid-template-columns: repeat(4, 1fr); } }
```

- [ ] **Step 3: Serve and verify**

Open site — Expected: 4 cards, 1 col on phone / 2 on tablet / 4 on desktop, each with photo + title + text. Images load from `images/web/`. No console errors, no broken-image icons.

- [ ] **Step 4: Commit**

```bash
git add index.html styles.css
git commit -m "feat: add services section with four cards"
```

---

### Task 5: Why-us section

**Files:**
- Modify: `index.html` (fill `#why`)
- Modify: `styles.css`

**Interfaces:**
- Produces: `#why` with four `.feature` items (emoji icon + heading + one line). No images.

- [ ] **Step 1: Fill `#why`**

```html
<section id="why" class="section">
  <div class="container">
    <h2 class="section-title">為什麼選擇松坂搬家</h2>
    <p class="section-sub">讓您搬家省心又安心</p>
    <div class="feature-grid">
      <div class="feature"><span class="feature-ico">💰</span><h3>透明報價</h3><p>清楚估價不亂加價</p></div>
      <div class="feature"><span class="feature-ico">📦</span><h3>細心包裝</h3><p>專業防護物品不受損</p></div>
      <div class="feature"><span class="feature-ico">⏰</span><h3>準時到府</h3><p>約定時間準時服務</p></div>
      <div class="feature"><span class="feature-ico">♻️</span><h3>搬運＋清運一條龍</h3><p>舊物清運一次完成</p></div>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Append styles**

```css
.feature-grid { display: grid; gap: 20px; grid-template-columns: 1fr 1fr; }
.feature { text-align: center; padding: 22px 14px; background: var(--bg);
  border-radius: var(--radius); }
.feature-ico { font-size: 40px; display: block; margin-bottom: 10px; }
.feature h3 { color: var(--navy); font-size: 17px; margin-bottom: 4px; }
.feature p { color: var(--muted); font-size: 14px; }
@media (min-width: 900px) { .feature-grid { grid-template-columns: repeat(4, 1fr); } }
```

- [ ] **Step 3: Serve and verify**

Open site — Expected: four feature blocks, 2×2 on phone, single row on desktop. No console errors.

- [ ] **Step 4: Commit**

```bash
git add index.html styles.css
git commit -m "feat: add why-us feature section"
```

---

### Task 6: Gallery + lightbox

**Files:**
- Modify: `index.html` (fill `#gallery`)
- Modify: `styles.css`
- Modify: `main.js` (lightbox logic)

**Interfaces:**
- Consumes: `images/web/g01.jpg … g11.jpg`.
- Produces: `#gallery` grid of thumbnails; a `.lightbox` overlay (hidden by default). `main.js` adds click handlers that open the clicked image in the overlay, close on overlay click / Esc / close button.

- [ ] **Step 1: Fill `#gallery`** (11 thumbs g01–g11)

```html
<section id="gallery" class="section">
  <div class="container">
    <h2 class="section-title">實績照片</h2>
    <p class="section-sub">實際搬運與清運現場</p>
    <div class="gallery-grid">
      <button class="gallery-item" data-src="images/web/g01.jpg"><img src="images/web/g01.jpg" alt="搬運清運實績照片 1" loading="lazy"></button>
      <button class="gallery-item" data-src="images/web/g02.jpg"><img src="images/web/g02.jpg" alt="搬運清運實績照片 2" loading="lazy"></button>
      <button class="gallery-item" data-src="images/web/g03.jpg"><img src="images/web/g03.jpg" alt="搬運清運實績照片 3" loading="lazy"></button>
      <button class="gallery-item" data-src="images/web/g04.jpg"><img src="images/web/g04.jpg" alt="搬運清運實績照片 4" loading="lazy"></button>
      <button class="gallery-item" data-src="images/web/g05.jpg"><img src="images/web/g05.jpg" alt="搬運清運實績照片 5" loading="lazy"></button>
      <button class="gallery-item" data-src="images/web/g06.jpg"><img src="images/web/g06.jpg" alt="搬運清運實績照片 6" loading="lazy"></button>
      <button class="gallery-item" data-src="images/web/g07.jpg"><img src="images/web/g07.jpg" alt="搬運清運實績照片 7" loading="lazy"></button>
      <button class="gallery-item" data-src="images/web/g08.jpg"><img src="images/web/g08.jpg" alt="搬運清運實績照片 8" loading="lazy"></button>
      <button class="gallery-item" data-src="images/web/g09.jpg"><img src="images/web/g09.jpg" alt="搬運清運實績照片 9" loading="lazy"></button>
      <button class="gallery-item" data-src="images/web/g10.jpg"><img src="images/web/g10.jpg" alt="搬運清運實績照片 10" loading="lazy"></button>
      <button class="gallery-item" data-src="images/web/g11.jpg"><img src="images/web/g11.jpg" alt="搬運清運實績照片 11" loading="lazy"></button>
    </div>
  </div>
  <div class="lightbox" id="lightbox" hidden>
    <button class="lightbox-close" aria-label="關閉">✕</button>
    <img class="lightbox-img" src="" alt="放大檢視">
  </div>
</section>
```

- [ ] **Step 2: Append styles**

```css
.gallery-grid { display: grid; gap: 10px; grid-template-columns: repeat(2, 1fr); }
.gallery-item { padding: 0; border: 0; cursor: pointer; background: none; border-radius: 10px; overflow: hidden; }
.gallery-item img { width: 100%; height: 130px; object-fit: cover; transition: transform .2s; }
.gallery-item:hover img { transform: scale(1.05); }
@media (min-width: 640px) { .gallery-grid { grid-template-columns: repeat(3, 1fr); } .gallery-item img { height: 170px; } }
@media (min-width: 1000px) { .gallery-grid { grid-template-columns: repeat(4, 1fr); } .gallery-item img { height: 190px; } }
.lightbox { position: fixed; inset: 0; z-index: 100; background: rgba(0,0,0,.9);
  display: grid; place-items: center; padding: 20px; }
.lightbox[hidden] { display: none; }
.lightbox-img { max-width: 92vw; max-height: 86vh; object-fit: contain; border-radius: 8px; }
.lightbox-close { position: absolute; top: 16px; right: 20px; font-size: 30px; color: #fff;
  background: none; border: 0; cursor: pointer; }
```

- [ ] **Step 3: Add lightbox logic to `main.js`** (inside the DOMContentLoaded callback)

```js
const lightbox = document.getElementById('lightbox');
const lightboxImg = lightbox.querySelector('.lightbox-img');
const closeBtn = lightbox.querySelector('.lightbox-close');
function openLightbox(src) { lightboxImg.src = src; lightbox.hidden = false; document.body.style.overflow = 'hidden'; }
function closeLightbox() { lightbox.hidden = true; lightboxImg.src = ''; document.body.style.overflow = ''; }
document.querySelectorAll('.gallery-item').forEach(btn =>
  btn.addEventListener('click', () => openLightbox(btn.dataset.src)));
closeBtn.addEventListener('click', closeLightbox);
lightbox.addEventListener('click', e => { if (e.target === lightbox) closeLightbox(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && !lightbox.hidden) closeLightbox(); });
```

- [ ] **Step 4: Serve and verify**

Open site — Expected: thumbnail grid (2/3/4 cols by width). Clicking a thumb opens a full-screen dark overlay with the large image; clicking backdrop, ✕, or pressing Esc closes it; page scroll locks while open. No console errors.

- [ ] **Step 5: Commit**

```bash
git add index.html styles.css main.js
git commit -m "feat: add gallery with lightbox"
```

---

### Task 7: FAQ accordion

**Files:**
- Modify: `index.html` (fill `#faq`)
- Modify: `styles.css`
- Modify: `main.js`

**Interfaces:**
- Produces: `#faq` using native `<details>/<summary>` (no JS strictly required, but JS ensures single-open behavior). Four Q&A items with the spec's copy.

- [ ] **Step 1: Fill `#faq`**

```html
<section id="faq" class="section">
  <div class="container narrow">
    <h2 class="section-title">常見問答</h2>
    <div class="faq-list">
      <details class="faq-item"><summary>怎麼報價？</summary>
        <p>可電話或加 LINE 告知物品與樓層，我們提供估價。</p></details>
      <details class="faq-item"><summary>服務範圍到哪？</summary>
        <!-- 服務地區：待業主確認，暫以示意 -->
        <p>雙北・桃園地區皆可服務，詳細範圍歡迎來電洽詢。</p></details>
      <details class="faq-item"><summary>大型廢棄物能一起清嗎？</summary>
        <p>可以，搬家同時可代清運舊家具與大型垃圾。</p></details>
      <details class="faq-item"><summary>假日有服務嗎？</summary>
        <!-- 營業時間：待業主確認，暫以示意 -->
        <p>週一至週日 08:00–20:00 皆可服務，歡迎預約。</p></details>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Append styles**

```css
.container.narrow { width: min(100% - 32px, 760px); }
.faq-list { display: grid; gap: 12px; }
.faq-item { background: var(--bg); border-radius: 12px; padding: 4px 18px; }
.faq-item summary { cursor: pointer; font-weight: 700; color: var(--navy);
  padding: 14px 0; list-style: none; position: relative; }
.faq-item summary::-webkit-details-marker { display: none; }
.faq-item summary::after { content: "＋"; position: absolute; right: 0; color: var(--blue-bright); }
.faq-item[open] summary::after { content: "－"; }
.faq-item p { padding: 0 0 16px; color: var(--muted); }
```

- [ ] **Step 3: Add single-open behavior to `main.js`**

```js
const faqItems = document.querySelectorAll('.faq-item');
faqItems.forEach(item => item.addEventListener('toggle', () => {
  if (item.open) faqItems.forEach(o => { if (o !== item) o.open = false; });
}));
```

- [ ] **Step 4: Serve and verify**

Open site — Expected: four collapsible rows; clicking one expands it and collapses others; ＋/－ marker toggles. No console errors.

- [ ] **Step 5: Commit**

```bash
git add index.html styles.css main.js
git commit -m "feat: add FAQ accordion"
```

---

### Task 8: Contact / footer + mobile floating bar

**Files:**
- Modify: `index.html` (fill `#contact`; add floating bar before `<script>`)
- Modify: `styles.css`

**Interfaces:**
- Consumes: color tokens; phone/LINE constants.
- Produces: `#contact` footer block with brand, phone, LINE, service area, hours; a `.mobile-bar` fixed at viewport bottom (shown only ≤768px) with phone + LINE buttons.

- [ ] **Step 1: Fill `#contact`**

```html
<section id="contact" class="contact">
  <div class="container">
    <h2 class="section-title contact-title">立即聯絡我們</h2>
    <p class="contact-sub">免費估價・快速回覆</p>
    <div class="contact-cta">
      <a class="btn btn-phone btn-lg" href="tel:0916383872">📞 撥打 0916383872</a>
      <a class="btn btn-line btn-lg" href="https://lin.ee/VOLz2Qq" target="_blank" rel="noopener">💬 加 LINE 詢價</a>
    </div>
    <ul class="contact-info">
      <li>📍 服務地區：雙北・桃園<!-- 待業主確認 --></li>
      <li>🕗 營業時間：週一至週日 08:00–20:00<!-- 待業主確認 --></li>
    </ul>
    <p class="footer-brand">松坂搬家 ｜ 專業搬家・廢棄物清運</p>
  </div>
</section>
```

- [ ] **Step 2: Add mobile floating bar** (before `<script src="main.js">`)

```html
<div class="mobile-bar">
  <a class="mobile-bar-btn phone" href="tel:0916383872" aria-label="撥打電話">📞 撥電話</a>
  <a class="mobile-bar-btn line" href="https://lin.ee/VOLz2Qq" target="_blank" rel="noopener" aria-label="加 LINE">💬 加 LINE</a>
</div>
```

- [ ] **Step 3: Append styles**

```css
.contact { background: var(--navy); color: #fff; text-align: center; padding: 56px 0 84px; }
.contact-title { color: #fff; }
.contact-sub { color: #cdd8e8; margin-bottom: 26px; }
.contact-cta { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; margin-bottom: 26px; }
.contact-info { list-style: none; display: grid; gap: 8px; color: #dbe4f0; margin-bottom: 20px; }
.footer-brand { color: #9fb2cc; font-size: 14px; }
.mobile-bar { display: none; position: fixed; bottom: 0; left: 0; right: 0; z-index: 60;
  gap: 1px; background: rgba(15,42,74,.15); }
.mobile-bar-btn { flex: 1; text-align: center; padding: 15px 0; font-weight: 700; color: #fff; }
.mobile-bar-btn.phone { background: var(--phone); }
.mobile-bar-btn.line { background: var(--line); }
@media (max-width: 768px) { .mobile-bar { display: flex; } .contact { padding-bottom: 96px; } }
```

- [ ] **Step 4: Serve and verify**

Open site — Expected: dark navy footer with two large CTAs + service area/hours + brand line. Resize to ≤768px (or DevTools mobile): a fixed bottom bar with 撥電話 / 加 LINE appears and stays while scrolling; it hides on desktop widths. No console errors.

- [ ] **Step 5: Commit**

```bash
git add index.html styles.css
git commit -m "feat: add contact footer and mobile floating contact bar"
```

---

### Task 9: Polish — SEO/meta, favicon, responsive & a11y pass, deploy config

**Files:**
- Modify: `index.html` (Open Graph tags, favicon link, `<html>` already lang-set)
- Create: `favicon.svg`
- Create: `netlify.toml`

**Interfaces:**
- Produces: social-share meta, a simple favicon, and a deploy config so the site can be published as-is.

- [ ] **Step 1: Add Open Graph + favicon link** (in `<head>`)

```html
<meta property="og:title" content="松坂搬家 ｜ 專業搬家・廢棄物清運">
<meta property="og:description" content="住家搬家、公司搬遷、家具重物搬運、廢棄物清運。細心包裝、準時到府、透明報價。電話 0916383872。">
<meta property="og:type" content="website">
<meta property="og:image" content="images/web/hero.jpg">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
```

- [ ] **Step 2: Create `favicon.svg`** (simple navy badge with 松)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#0F2A4A"/>
  <text x="32" y="44" font-size="38" font-family="sans-serif" font-weight="700"
    text-anchor="middle" fill="#ffffff">松</text>
</svg>
```

- [ ] **Step 3: Create `netlify.toml`**

```toml
[build]
  publish = "."

[[headers]]
  for = "/images/web/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

- [ ] **Step 4: Full responsive + a11y verification**

Serve and check at widths 360 / 768 / 1280 px:
- No horizontal scroll at any width.
- Header CTAs, hero, services, features, gallery, FAQ, footer all readable and not overlapping.
- Mobile bar visible ≤768px only; does not cover footer content (footer has bottom padding).
- Tab through page: header links, gallery buttons, FAQ summaries, footer links are all focusable; Esc closes lightbox.
- Console has zero errors; no broken images (all `images/web/*` resolve).
- `tel:` and LINE links correct.

Fix any issue found before committing.

- [ ] **Step 5: Commit**

```bash
git add index.html favicon.svg netlify.toml
git commit -m "feat: add SEO meta, favicon, and deploy config"
```

---

## Self-Review

**Spec coverage check (spec §→task):**
- §2 pure static / no framework → Task 1 ✓
- §3 single brand 松坂搬家 + 0916383872 + LINE + colors → Global Constraints + Tasks 3/8 ✓
- §4.1 header → Task 3 ✓; §4.2 hero → Task 3 ✓; §4.3 services → Task 4 ✓; §4.4 why-us → Task 5 ✓; §4.5 gallery → Task 6 ✓; §4.6 FAQ → Task 7 ✓; §4.7 footer → Task 8 ✓; §4.8 mobile floating bar → Task 8 ✓
- §5 copy → Tasks 3–8 (verbatim) ✓
- §6 photo masking to images/web/ → Task 2 ✓
- §7 file structure → Tasks 1/2/9 ✓
- §8 interactions + a11y → Tasks 6/7/9 ✓
- §9 non-goals → nothing built for them ✓ (no form/analytics/multipage)
- §10 owner placeholders → marked with HTML comments in Tasks 7/8 ✓

**Placeholder scan:** No "TBD/TODO" in build steps. The only deferred data is `REGIONS` coordinates in Task 2, which are genuine execution-time observations with an explicit procedure (Task 2 Step 3) and enumerated source list — not vague placeholders.

**Type/name consistency:** Output filenames `hero.jpg / svc-home.jpg / svc-office.jpg / svc-heavy.jpg / svc-waste.jpg / g01–g11.jpg` defined in Task 2 JOBS match every `src="images/web/…"` in Tasks 3/4/6/9. Button classes `.btn/.btn-phone/.btn-line/.btn-lg` defined in Task 3 and reused in Tasks 8. Lightbox ids/classes (`#lightbox`, `.lightbox-img`, `.lightbox-close`, `.gallery-item[data-src]`) consistent between Task 6 HTML and JS. `.faq-item` consistent between Task 7 HTML and JS.

**Note:** Gallery lists g01–g11 (11 items) — Task 2 JOBS defines exactly g01–g11. Consistent.
