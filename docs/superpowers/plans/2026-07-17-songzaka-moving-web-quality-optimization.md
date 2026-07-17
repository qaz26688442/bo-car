# Songzaka Moving Web Quality Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把松坂搬家純靜態網站最佳化到行動版 Lighthouse Performance 中位數至少 90、LCP 不超過 2.5 秒，並補齊 WCAG 2.2、SEO、404、安全標頭與可重複驗證流程。

**Architecture:** Cloudflare Pages 繼續直接發布 `public/`，不加入前端框架或正式建置流程。開發時以 Python 3.14、Pillow 12.3.0 產生已遮蔽的版本化 WebP/JPEG 圖片；瀏覽器只載入 `public/index.html`、版本化 CSS/JS 與按裝置選中的圖片。Python `unittest` 負責圖片契約與靜態網站契約，瀏覽器與 Lighthouse 負責實際互動和效能驗收。

**Tech Stack:** HTML5、CSS、原生 JavaScript、Cloudflare Pages `_headers`、Python 3.14 `unittest`、Pillow 12.3.0、Lighthouse 13.4.0。

## Global Constraints

- 正式網址固定為 `https://songzaka-moving.pages.dev/`。
- 保留電話 `0916383872`、LINE `https://lin.ee/VOLz2Qq`、服務範圍「新竹以北」及「24 小時客服、全年無休」。
- Cloudflare Pages 直接發布 `public/`；不得加入 Node、Vite、前端框架、CMS、後端或正式建置流程。
- 原始 `images/` 永遠只讀；網站只引用提交到 `public/images/web/` 的衍生圖片。
- 圖片使用 WebP 與 JPEG fallback；Hero 640/1280/1600、服務卡 480/800、Gallery 縮圖 320/640、燈箱最大寬度 1280、OG 圖 1200 × 630。
- 本次靜態檔案版本固定為 `v2`；設定 immutable 的檔案不得原地覆寫。
- CTA 保留 `#F5793B` 與 `#06C755` 背景，文字固定為 `#0F2A4A`。
- 不加入未確認的地址、價格、評分、評論、正式 logo、分析追蹤或詢價表單。
- 不修改或提交既有的 `.vscode/settings.json` 使用者變更。

---

## File Map

- Create `requirements-dev.txt`: 唯一開發依賴 Pillow 的版本鎖定。
- Create `tests/__init__.py`: 讓標準函式庫 `unittest` 可穩定匯入測試模組。
- Create `tests/test_image_pipeline.py`: 圖片 manifest、遮蔽座標、輸出尺寸、格式、完整性與預算測試。
- Modify `scripts/blur.py`: EXIF 轉正、遮蔽、裁切、響應式輸出與原子寫入。
- Create `public/images/web/*-v2-*`: 89 個版本化 WebP/JPEG 衍生產物。
- Create `tests/test_site_quality.py`: HTML、CSS、JS、SEO、crawl files 與 `_headers` 的靜態契約。
- Modify `public/index.html`: 響應式圖片、語意結構、Dialog、metadata 與 JSON-LD。
- Create `public/styles.v2.css`: 系統字型、響應式圖片、焦點、Dialog、reduced motion 與 404 樣式。
- Create `public/main.v2.js`: Gallery Dialog、焦點回復、圖片錯誤與 FAQ 行為。
- Create `public/favicon-v2.svg`: 版本化 favicon。
- Create `public/robots.txt`, `public/sitemap.xml`, `public/404.html`, `public/llms.txt`: crawl 與錯誤頁資源。
- Modify `public/_headers`: CSP、安全標頭與版本化資源長快取。
- Delete after validation `public/styles.css`, `public/main.js`, `public/images/web/hero.jpg`, `public/images/web/svc-*.jpg`, `public/images/web/g*.jpg`: 移除已被 v2 取代的產物。

---

### Task 1: Build the deterministic responsive-image pipeline

**Files:**
- Create: `requirements-dev.txt`
- Create: `tests/__init__.py`
- Create: `tests/test_image_pipeline.py`
- Modify: `scripts/blur.py`

**Interfaces:**
- Produces: `Variant`, `AssetJob`, `validate_manifest()`, `generate_job()`, `generate_all()`, `expected_paths()` and production constants `JOBS`, `REGIONS`, `SOURCE_DIR`, `OUTPUT_DIR`.
- Consumes: original JPEG files in `images/`; no browser assets are replaced in this task.

- [ ] **Step 1: Pin the development dependency**

Create `requirements-dev.txt` with exactly:

```text
Pillow==12.3.0
```

Create an empty `tests/__init__.py` so `python -m unittest tests.test_image_pipeline` has an explicit package.

- [ ] **Step 2: Create the failing image-pipeline tests**

Create `tests/test_image_pipeline.py` with these concrete cases:

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

from scripts.blur import (
    AssetJob,
    JOBS,
    OUTPUT_DIR,
    REGIONS,
    SOURCE_DIR,
    Variant,
    expected_paths,
    generate_job,
    validate_manifest,
)


class ImagePipelineTests(unittest.TestCase):
    def test_manifest_has_89_unique_outputs(self):
        validate_manifest(JOBS, REGIONS, SOURCE_DIR)
        paths = expected_paths(JOBS, OUTPUT_DIR)
        self.assertEqual(len(paths), 89)

    def test_rejects_out_of_range_mask(self):
        job = AssetJob(
            source="sample.jpg",
            variants=(Variant("sample-v2-10.webp", 10, 10, "WEBP", 75),),
        )
        with TemporaryDirectory() as directory:
            source_dir = Path(directory)
            Image.new("RGB", (20, 20), "white").save(source_dir / "sample.jpg")
            with self.assertRaisesRegex(ValueError, "sample.jpg"):
                validate_manifest(
                    (job,),
                    {"sample.jpg": ((0.9, 0.9, 0.2, 0.2),)},
                    source_dir,
                )

    def test_generates_fixed_and_preserved_aspect_outputs(self):
        job = AssetJob(
            source="sample.jpg",
            variants=(
                Variant("sample-v2-40.webp", 40, 30, "WEBP", 75),
                Variant("sample-v2-50.jpg", 50, None, "JPEG", 80),
            ),
        )
        with TemporaryDirectory() as source, TemporaryDirectory() as output:
            source_dir = Path(source)
            output_dir = Path(output)
            Image.new("RGB", (100, 50), "navy").save(source_dir / "sample.jpg")
            written = generate_job(job, source_dir, output_dir, {})
            self.assertEqual({path.name for path in written}, {
                "sample-v2-40.webp",
                "sample-v2-50.jpg",
            })
            with Image.open(output_dir / "sample-v2-40.webp") as fixed:
                self.assertEqual(fixed.size, (40, 30))
                self.assertEqual(fixed.format, "WEBP")
            with Image.open(output_dir / "sample-v2-50.jpg") as preserved:
                self.assertEqual(preserved.size, (50, 25))
                self.assertEqual(preserved.format, "JPEG")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Create the isolated environment and verify the tests fail**

Run:

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements-dev.txt
venv/bin/python -m unittest tests.test_image_pipeline -v
```

Expected: dependency installation succeeds; tests fail because the new dataclasses and functions do not yet exist.

- [ ] **Step 4: Replace the image script with the typed pipeline**

In `scripts/blur.py`, define the public types and manifest helpers exactly as follows, then retain the existing mask coordinates in `REGIONS`:

```python
#!/usr/bin/env python3
"""Create masked, responsive web images without modifying originals."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "images"
OUTPUT_DIR = ROOT / "public" / "images" / "web"
Region = tuple[float, float, float, float]


@dataclass(frozen=True)
class Variant:
    filename: str
    width: int
    height: int | None
    format: str
    quality: int


@dataclass(frozen=True)
class AssetJob:
    source: str
    variants: tuple[Variant, ...]


def responsive_variants(
    stem: str,
    widths: Sequence[int],
    ratio: tuple[int, int] | None,
) -> tuple[Variant, ...]:
    variants: list[Variant] = []
    for width in widths:
        height = round(width * ratio[1] / ratio[0]) if ratio else None
        variants.extend((
            Variant(f"{stem}-{width}.webp", width, height, "WEBP", 75),
            Variant(f"{stem}-{width}.jpg", width, height, "JPEG", 80),
        ))
    return tuple(variants)


def gallery_job(stem: str, source: str) -> AssetJob:
    return AssetJob(
        source,
        responsive_variants(stem, (320, 640), (4, 3))
        + responsive_variants(stem, (1280,), None),
    )
```

Use this exact production source mapping:

```python
SERVICE_SOURCES = {
    "svc-home-v2": "S__52854796_0.jpg",
    "svc-office-v2": "S__52854810_0.jpg",
    "svc-heavy-v2": "S__52854811_0.jpg",
    "svc-waste-v2": "S__52854812_0.jpg",
}

GALLERY_SOURCES = {
    "g01-v2": "S__52854819_0.jpg",
    "g02-v2": "S__52854797_0.jpg",
    "g03-v2": "S__52854798_0.jpg",
    "g04-v2": "S__52854800_0.jpg",
    "g05-v2": "S__52854803_0.jpg",
    "g06-v2": "S__52854804_0.jpg",
    "g07-v2": "S__52854806_0.jpg",
    "g08-v2": "S__52854811_0.jpg",
    "g09-v2": "S__52854812_0.jpg",
    "g10-v2": "S__52854809_0.jpg",
    "g11-v2": "S__52854822_0.jpg",
}

JOBS = (
    AssetJob(
        "S__52854819_0.jpg",
        responsive_variants("hero-v2", (640, 1280, 1600), (16, 9)),
    ),
    AssetJob(
        "S__52854819_0.jpg",
        (Variant("og-songzaka-v2-1200x630.jpg", 1200, 630, "JPEG", 80),),
    ),
    *(AssetJob(source, responsive_variants(stem, (480, 800), (4, 3)))
      for stem, source in SERVICE_SOURCES.items()),
    *(gallery_job(stem, source) for stem, source in GALLERY_SOURCES.items()),
)

REGIONS: dict[str, tuple[Region, ...]] = {
    "S__52854810_0.jpg": ((0.55, 0.22, 0.17, 0.16),),
    "S__52854812_0.jpg": ((0.57, 0.86, 0.17, 0.06),),
    "S__52854797_0.jpg": ((0.34, 0.51, 0.13, 0.09),),
    "S__52854800_0.jpg": ((0.29, 0.64, 0.10, 0.08),),
    "S__52854806_0.jpg": ((0.50, 0.40, 0.22, 0.14),),
    "S__52854822_0.jpg": (
        (0.00, 0.10, 0.24, 0.25),
        (0.35, 0.30, 0.11, 0.12),
        (0.48, 0.29, 0.11, 0.13),
    ),
}
```

Add these complete processing functions below the manifest:

```python
def validate_manifest(
    jobs: Sequence[AssetJob],
    regions: Mapping[str, Sequence[Region]],
    source_dir: Path,
) -> None:
    filenames: set[str] = set()
    for job in jobs:
        source_path = source_dir / job.source
        if not source_path.is_file():
            raise FileNotFoundError(f"missing source: {job.source}")
        for region in regions.get(job.source, ()):
            x, y, width, height = region
            if min(region) < 0 or x + width > 1 or y + height > 1:
                raise ValueError(f"invalid mask region for {job.source}: {region}")
        for variant in job.variants:
            if variant.filename in filenames:
                raise ValueError(f"duplicate output: {variant.filename}")
            filenames.add(variant.filename)
            if variant.width <= 0 or (variant.height is not None and variant.height <= 0):
                raise ValueError(f"invalid dimensions: {variant.filename}")
            if variant.format not in {"WEBP", "JPEG"}:
                raise ValueError(f"invalid format: {variant.filename}")


def apply_masks(image: Image.Image, regions: Sequence[Region]) -> Image.Image:
    result = image.copy()
    for x, y, width, height in regions:
        left = round(x * result.width)
        top = round(y * result.height)
        right = round((x + width) * result.width)
        bottom = round((y + height) * result.height)
        box = (left, top, right, bottom)
        masked = result.crop(box)
        radius = max(right - left, bottom - top) // 8 + 8
        result.paste(masked.filter(ImageFilter.GaussianBlur(radius)), box)
    return result


def resize_variant(image: Image.Image, variant: Variant) -> Image.Image:
    if variant.height is not None:
        return ImageOps.fit(
            image,
            (variant.width, variant.height),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
    width = min(variant.width, image.width)
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def save_atomic(image: Image.Image, path: Path, variant: Variant) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        options = {"quality": variant.quality, "optimize": True}
        if variant.format == "WEBP":
            options["method"] = 6
        image.save(temporary, variant.format, **options)
        with Image.open(temporary) as check:
            check.verify()
        if temporary.stat().st_size == 0:
            raise ValueError(f"empty output: {variant.filename}")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def generate_job(
    job: AssetJob,
    source_dir: Path,
    output_dir: Path,
    regions: Mapping[str, Sequence[Region]],
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(source_dir / job.source) as source:
        base = ImageOps.exif_transpose(source).convert("RGB")
    base = apply_masks(base, regions.get(job.source, ()))
    written: list[Path] = []
    for variant in job.variants:
        output = output_dir / variant.filename
        save_atomic(resize_variant(base, variant), output, variant)
        written.append(output)
    return written


def expected_paths(
    jobs: Sequence[AssetJob],
    output_dir: Path,
) -> set[Path]:
    return {
        output_dir / variant.filename
        for job in jobs
        for variant in job.variants
    }


def generate_all() -> list[Path]:
    validate_manifest(JOBS, REGIONS, SOURCE_DIR)
    written: list[Path] = []
    for job in JOBS:
        written.extend(generate_job(job, SOURCE_DIR, OUTPUT_DIR, REGIONS))
    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    validate_manifest(JOBS, REGIONS, SOURCE_DIR)
    if args.check:
        print(f"manifest valid: {len(expected_paths(JOBS, OUTPUT_DIR))} outputs")
        return
    for path in generate_all():
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run unit tests and manifest validation**

Run:

```bash
venv/bin/python -m unittest tests.test_image_pipeline -v
venv/bin/python scripts/blur.py --check
```

Expected: 3 tests pass; manifest reports `89 outputs`.

- [ ] **Step 6: Commit the pipeline**

```bash
git add requirements-dev.txt tests/__init__.py tests/test_image_pipeline.py scripts/blur.py
git commit -m "feat(images): add responsive asset pipeline"
```

---

### Task 2: Generate and verify the production image assets

**Files:**
- Modify: `tests/test_image_pipeline.py`
- Create: `public/images/web/*-v2-*`

**Interfaces:**
- Consumes: `JOBS`, `expected_paths()` and `generate_all()` from Task 1.
- Produces: exactly 89 versioned files referenced by the page tasks.

- [ ] **Step 1: Add failing production-output tests**

Append these methods to `ImagePipelineTests`:

```python
    def test_production_outputs_match_manifest(self):
        paths = expected_paths(JOBS, OUTPUT_DIR)
        self.assertEqual(len(paths), 89)
        for path in sorted(paths):
            self.assertTrue(path.is_file(), path.name)
            self.assertGreater(path.stat().st_size, 0, path.name)
            with Image.open(path) as image:
                image.verify()

    def test_hero_budget_and_dimensions(self):
        hero = OUTPUT_DIR / "hero-v2-1280.webp"
        self.assertLessEqual(hero.stat().st_size, 250 * 1024)
        with Image.open(hero) as image:
            self.assertEqual(image.size, (1280, 720))
            self.assertEqual(image.format, "WEBP")
```

- [ ] **Step 2: Run tests to verify the assets are missing**

Run: `venv/bin/python -m unittest tests.test_image_pipeline -v`

Expected: the original 3 tests pass; the 2 new tests fail on missing `v2` outputs.

- [ ] **Step 3: Generate the responsive assets twice and confirm deterministic bytes**

Run these commands in order:

```bash
venv/bin/python scripts/blur.py
shasum -a 256 public/images/web/*-v2-* > /tmp/songzaka-images-first.sha256
venv/bin/python scripts/blur.py
shasum -a 256 public/images/web/*-v2-* > /tmp/songzaka-images-second.sha256
diff -u /tmp/songzaka-images-first.sha256 /tmp/songzaka-images-second.sha256
```

Expected: 89 outputs are written on each run; `diff` has no output.

- [ ] **Step 4: Run automated image verification**

Run: `venv/bin/python -m unittest tests.test_image_pipeline -v`

Expected: all 5 tests pass and `hero-v2-1280.webp` is at most 250 KiB.

- [ ] **Step 5: Inspect privacy masks and crops visually**

Open and inspect these exact outputs at original detail:

- `svc-office-v2-800.webp`: worker face remains unreadable.
- `svc-waste-v2-800.webp` and `g09-v2-1280.webp`: license plate remains unreadable.
- `g02-v2-1280.webp` and `g04-v2-1280.webp`: license plates remain unreadable.
- `g07-v2-1280.webp`: worker face remains unreadable.
- `g11-v2-1280.webp`: KFC and Taishin signage remains unreadable.
- Hero, four service images, eleven 640px thumbnails and OG image: focal subject is not cut off.

Expected: no face, plate or third-party sign identified in `REGIONS` is readable; all fixed-ratio crops retain the service subject.

- [ ] **Step 6: Commit generated assets**

```bash
git add tests/test_image_pipeline.py public/images/web
git commit -m "perf(images): generate responsive web assets"
```

---

### Task 3: Serve responsive images and remove render-blocking fonts

**Files:**
- Create: `tests/test_site_quality.py`
- Create: `public/styles.v2.css`
- Modify: `public/index.html`

**Interfaces:**
- Consumes: all `v2` image names from Task 2.
- Produces: a working no-third-party-font page with discoverable Hero and responsive below-fold images; retains `public/main.js` and the current lightbox until Task 4.

- [ ] **Step 1: Write failing static performance tests**

Create `tests/test_site_quality.py`:

```python
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
HTML = (PUBLIC / "index.html").read_text(encoding="utf-8")
CSS = (PUBLIC / "styles.v2.css").read_text(encoding="utf-8") if (PUBLIC / "styles.v2.css").exists() else ""


class SiteQualityTests(unittest.TestCase):
    def test_uses_versioned_local_styles_and_system_fonts(self):
        self.assertIn('href="styles.v2.css"', HTML)
        self.assertNotIn("fonts.googleapis.com", HTML)
        self.assertNotIn("fonts.gstatic.com", HTML)
        self.assertIn('"PingFang TC"', CSS)
        self.assertIn('"Microsoft JhengHei"', CSS)

    def test_hero_is_discoverable_and_prioritized(self):
        self.assertIn('class="hero-media"', HTML)
        self.assertIn('hero-v2-640.webp 640w', HTML)
        self.assertIn('hero-v2-1280.webp 1280w', HTML)
        self.assertIn('hero-v2-1600.webp 1600w', HTML)
        self.assertRegex(HTML, r'<img[^>]+fetchpriority="high"[^>]+loading="eager"')
        self.assertNotIn('background: url("images/web/hero.jpg")', CSS)

    def test_content_images_have_dimensions_and_lazy_loading(self):
        image_tags = re.findall(r"<img\b[^>]*>", HTML)
        self.assertGreaterEqual(len(image_tags), 16)
        for tag in image_tags:
            self.assertIn(" width=", tag)
            self.assertIn(" height=", tag)
        lazy_images = [tag for tag in image_tags if 'alt=""' not in tag]
        for tag in lazy_images:
            self.assertIn('loading="lazy"', tag)
            self.assertIn('decoding="async"', tag)
        self.assertNotRegex(HTML, r'alt="搬運清運實績照片 \d+"')
        ids = re.findall(r'\sid="([^"]+)"', HTML)
        self.assertEqual(len(ids), len(set(ids)))

    def test_cta_colors_use_navy_text(self):
        self.assertIn("--phone: #F5793B", CSS)
        self.assertIn("--line: #06C755", CSS)
        self.assertRegex(CSS, r"\.btn-phone\s*\{[^}]*color:\s*var\(--navy\)")
        self.assertRegex(CSS, r"\.btn-line\s*\{[^}]*color:\s*var\(--navy\)")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify failure**

Run: `venv/bin/python -m unittest tests.test_site_quality -v`

Expected: tests fail because `styles.v2.css`, local-only fonts and responsive pictures are absent.

- [ ] **Step 3: Create the v2 stylesheet from the current layout rules**

Create `public/styles.v2.css` by retaining the layout rules in `public/styles.css` and making these exact replacements:

```css
:root {
  --navy: #0F2A4A;
  --blue: #1E5AA8;
  --blue-bright: #2E7BD6;
  --phone: #F5793B;
  --line: #06C755;
  --bg: #F5F7FA;
  --ink: #1A2230;
  --muted: #667085;
  --white: #FFFFFF;
  --maxw: 1120px;
  --radius: 14px;
  --shadow: 0 6px 24px rgba(15, 42, 74, .10);
}

body {
  font-family: system-ui, -apple-system, "PingFang TC", "Microsoft JhengHei", sans-serif;
  color: var(--ink);
  line-height: 1.7;
  background: var(--white);
}

.btn-phone { background: var(--phone); color: var(--navy); }
.btn-line { background: var(--line); color: var(--navy); }
.mobile-bar-btn.phone { background: var(--phone); color: var(--navy); }
.mobile-bar-btn.line { background: var(--line); color: var(--navy); }

.hero {
  position: relative;
  min-height: 78vh;
  display: grid;
  place-items: center;
  overflow: hidden;
  color: var(--white);
  text-align: center;
}
.hero-media,
.hero-media img { position: absolute; inset: 0; width: 100%; height: 100%; }
.hero-media img { object-fit: cover; }
.hero-overlay { z-index: 1; }
.hero-content { z-index: 2; }
```

Keep service cards at 4:3 with `aspect-ratio: 4 / 3; object-fit: cover;` and Gallery thumbnails at the same ratio instead of fixed pixel heights. Do not add `@import`, external URLs or inline data fonts.

- [ ] **Step 4: Replace every page image with exact responsive markup**

In `public/index.html`:

1. Remove both font preconnects and the Google Fonts stylesheet.
2. Change the stylesheet reference to `styles.v2.css`.
3. Put this `<picture>` immediately inside `.hero`, before `.hero-overlay`:

```html
<picture class="hero-media" aria-hidden="true">
  <source type="image/webp"
    srcset="images/web/hero-v2-640.webp 640w, images/web/hero-v2-1280.webp 1280w, images/web/hero-v2-1600.webp 1600w"
    sizes="100vw">
  <img src="images/web/hero-v2-1280.jpg"
    srcset="images/web/hero-v2-640.jpg 640w, images/web/hero-v2-1280.jpg 1280w, images/web/hero-v2-1600.jpg 1600w"
    sizes="100vw" alt="" width="1600" height="900"
    fetchpriority="high" loading="eager" decoding="async">
</picture>
```

Use this complete service mapping, with `<source type="image/webp">`, a JPEG `<img>`, `width="800" height="600"`, `loading="lazy" decoding="async"`, and sizes `(min-width: 1000px) 25vw, (min-width: 640px) 50vw, 100vw`:

| Stem | Alt |
|---|---|
| `svc-home-v2` | `包裝完成並準備從電梯口搬運的住家家具` |
| `svc-office-v2` | `搬家人員在大樓走廊搬運辦公設備` |
| `svc-heavy-v2` | `以防護毯完整包覆的大型家具` |
| `svc-waste-v2` | `怪手與貨車進行工地廢棄物清運` |

Each service picture follows this exact attribute contract, substituting only the stem and alt from the table:

```html
<picture>
  <source type="image/webp"
    srcset="images/web/svc-home-v2-480.webp 480w, images/web/svc-home-v2-800.webp 800w"
    sizes="(min-width: 1000px) 25vw, (min-width: 640px) 50vw, 100vw">
  <img src="images/web/svc-home-v2-800.jpg"
    srcset="images/web/svc-home-v2-480.jpg 480w, images/web/svc-home-v2-800.jpg 800w"
    sizes="(min-width: 1000px) 25vw, (min-width: 640px) 50vw, 100vw"
    alt="包裝完成並準備從電梯口搬運的住家家具"
    width="800" height="600" loading="lazy" decoding="async">
</picture>
```

Use this exact Gallery alt mapping:

| Stem | Alt |
|---|---|
| `g01-v2` | `松坂搬家人員整理路邊待搬運家具` |
| `g02-v2` | `搬家貨車在地下停車場裝載包裝物品` |
| `g03-v2` | `搬家人員在樓梯間搬運多箱紙箱` |
| `g04-v2` | `搬家貨車裝載袋裝衣物與紙箱` |
| `g05-v2` | `吊車在大樓外進行高樓層吊掛搬運` |
| `g06-v2` | `松坂搬家人員拆卸大型冰箱抽屜` |
| `g07-v2` | `搬家人員扛著防護毯包覆的大型家具` |
| `g08-v2` | `防護毯完整包覆的桌櫃家具` |
| `g09-v2` | `怪手與貨車進行工地廢棄物清運` |
| `g10-v2` | `松坂搬家人員搬運包膜保護的家具` |
| `g11-v2` | `路邊集中等待清運的舊家具` |

Each Gallery button retains its existing class and uses a responsive 320/640 `<picture>` with `width="640" height="480"`, `loading="lazy"`, `decoding="async"`, and sizes `(min-width: 1000px) 25vw, (min-width: 640px) 33vw, 50vw`. Keep the current lightbox wrapper and script reference until Task 4.

During this transition, set the current `.lightbox-img` to `width="1280" height="960" loading="lazy" decoding="async"` so every `<img>` satisfies the static dimensions/loading contract before Task 4 replaces the wrapper.

- [ ] **Step 5: Run static and image tests**

Run:

```bash
venv/bin/python -m unittest tests.test_site_quality -v
venv/bin/python -m unittest tests.test_image_pipeline -v
```

Expected: all Task 3 tests and all 5 image tests pass.

- [ ] **Step 6: Start a local server and smoke-test rendering**

Run: `python3 -m http.server 4173 -d public`

Open `http://127.0.0.1:4173/` at 375px and 1440px. Expected: Hero, service cards and Gallery render with no missing resources; the old Gallery lightbox still works; no Google Fonts request appears in Network.

- [ ] **Step 7: Commit page performance changes**

```bash
git add tests/test_site_quality.py public/index.html public/styles.v2.css
git commit -m "perf(page): serve responsive images and system fonts"
```

---

### Task 4: Add accessible navigation and native Gallery Dialog

**Files:**
- Modify: `tests/test_site_quality.py`
- Modify: `public/index.html`
- Modify: `public/styles.v2.css`
- Create: `public/main.v2.js`

**Interfaces:**
- Consumes: Gallery button stems, captions and 1280px image files from Tasks 2–3.
- Produces: `openLightbox(button)`, `close` event cleanup, native Dialog semantics and FAQ single-open behavior.

- [ ] **Step 1: Add failing accessibility and script-contract tests**

Extend `tests/test_site_quality.py` with:

```python
JS = (PUBLIC / "main.v2.js").read_text(encoding="utf-8") if (PUBLIC / "main.v2.js").exists() else ""


def channel(value: int) -> float:
    component = value / 255
    return component / 12.92 if component <= 0.04045 else ((component + 0.055) / 1.055) ** 2.4


def contrast(foreground: str, background: str) -> float:
    colors = []
    for color in (foreground, background):
        rgb = tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))
        colors.append(0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2]))
    light, dark = sorted(colors, reverse=True)
    return (light + 0.05) / (dark + 0.05)
```

Place this block after the `HTML` and `CSS` constants and before `class SiteQualityTests` so the test methods can use `JS` and `contrast()`.

Add these test methods to `SiteQualityTests`:

```python
    def test_skip_link_main_and_dialog_semantics(self):
        self.assertIn('class="skip-link" href="#main-content"', HTML)
        self.assertIn('<main id="main-content" tabindex="-1">', HTML)
        self.assertIn('<dialog class="lightbox" id="lightbox"', HTML)
        self.assertIn('aria-labelledby="lightbox-title"', HTML)
        self.assertIn('aria-describedby="lightbox-caption"', HTML)

    def test_versioned_script_is_deferred_and_safe(self):
        self.assertIn('<script src="main.v2.js" defer></script>', HTML)
        self.assertIn("showModal()", JS)
        self.assertIn("opener.focus()", JS)
        self.assertNotIn("console.log", JS)
        self.assertNotIn("innerHTML", JS)
        self.assertNotIn("document.body.style", JS)

    def test_focus_motion_and_safe_area_rules_exist(self):
        self.assertIn(":focus-visible", CSS)
        self.assertIn("prefers-reduced-motion: reduce", CSS)
        self.assertIn("safe-area-inset-bottom", CSS)
        self.assertIn("min-height: 44px", CSS)

    def test_cta_contrast_passes_wcag_aa(self):
        self.assertGreaterEqual(contrast("#0F2A4A", "#F5793B"), 4.5)
        self.assertGreaterEqual(contrast("#0F2A4A", "#06C755"), 4.5)
```

- [ ] **Step 2: Run the tests and verify accessibility failures**

Run: `venv/bin/python -m unittest tests.test_site_quality -v`

Expected: Task 3 tests pass; new skip-link, Dialog, script and CSS tests fail.

- [ ] **Step 3: Add the semantic navigation and Dialog markup**

Update `public/index.html` as follows:

- Change `<html lang="zh-Hant">` to `<html lang="zh-Hant-TW">`.
- Insert `<a class="skip-link" href="#main-content">跳到主要內容</a>` immediately after `<body>`.
- Change `<main>` to `<main id="main-content" tabindex="-1">`.
- Set the Header `<nav>` to `aria-label="主要聯絡方式"` and change `.mobile-bar` to a `<nav aria-label="行動版聯絡方式">`.
- Wrap every decorative emoji in `<span aria-hidden="true">` and keep visible text outside the span.
- Ensure every CTA has a 44px target and a specific accessible name; LINE names end with「在新分頁開啟」。
- Change the final script tag to `<script src="main.v2.js" defer></script>`.

Set `type="button"` on all Gallery buttons and use this exact full-image contract:

| Stem | Data caption | Data width | Data height |
|---|---|---:|---:|
| `g01-v2` | `松坂搬家人員整理路邊待搬運家具` | 1280 | 960 |
| `g02-v2` | `搬家貨車在地下停車場裝載包裝物品` | 1280 | 960 |
| `g03-v2` | `搬家人員在樓梯間搬運多箱紙箱` | 1108 | 1477 |
| `g04-v2` | `搬家貨車裝載袋裝衣物與紙箱` | 1280 | 960 |
| `g05-v2` | `吊車在大樓外進行高樓層吊掛搬運` | 1108 | 1477 |
| `g06-v2` | `松坂搬家人員拆卸大型冰箱抽屜` | 1108 | 1477 |
| `g07-v2` | `搬家人員扛著防護毯包覆的大型家具` | 1108 | 1477 |
| `g08-v2` | `防護毯完整包覆的桌櫃家具` | 1108 | 1477 |
| `g09-v2` | `怪手與貨車進行工地廢棄物清運` | 1108 | 1477 |
| `g10-v2` | `松坂搬家人員搬運包膜保護的家具` | 1108 | 1477 |
| `g11-v2` | `路邊集中等待清運的舊家具` | 1280 | 960 |

For each row, set `data-webp` and `data-jpeg` from its stem, set `data-caption`, `data-width`, `data-height`, and prefix the caption with「放大檢視：」for `aria-label`. The first row therefore becomes:

```html
data-webp="images/web/g01-v2-1280.webp"
data-jpeg="images/web/g01-v2-1280.jpg"
data-caption="松坂搬家人員整理路邊待搬運家具"
aria-label="放大檢視：松坂搬家人員整理路邊待搬運家具"
```

Replace the old lightbox `<div>` with:

```html
<dialog class="lightbox" id="lightbox"
  aria-labelledby="lightbox-title" aria-describedby="lightbox-caption">
  <div class="lightbox-panel">
    <h2 id="lightbox-title" class="sr-only">實績照片放大檢視</h2>
    <button class="lightbox-close" type="button" aria-label="關閉實績照片">
      <span aria-hidden="true">✕</span>
    </button>
    <picture class="lightbox-picture">
      <source class="lightbox-source-webp" type="image/webp">
      <img class="lightbox-img" alt="" width="1280" height="960"
        loading="lazy" decoding="async">
    </picture>
    <p id="lightbox-caption" class="lightbox-caption"></p>
    <p class="lightbox-error" role="alert" hidden>圖片載入失敗，請稍後再試。</p>
  </div>
</dialog>
```

- [ ] **Step 4: Add focus, Dialog and reduced-motion CSS**

Add these rules to `public/styles.v2.css`, adapting the current lightbox selectors so no old `[hidden]` overlay rule remains:

```css
.skip-link {
  position: fixed;
  z-index: 200;
  top: 8px;
  left: 8px;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--white);
  color: var(--navy);
  transform: translateY(-150%);
}
.skip-link:focus { transform: translateY(0); }
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
a:focus-visible,
button:focus-visible,
summary:focus-visible {
  outline: 3px solid var(--white);
  outline-offset: 3px;
  box-shadow: 0 0 0 6px var(--navy);
}
.btn,
.brand,
.gallery-item,
.lightbox-close,
.mobile-bar-btn,
.faq-item summary { min-height: 44px; }
.brand { display: inline-flex; align-items: center; }
.gallery-item:hover img,
.gallery-item:focus-visible img { transform: scale(1.05); }
section, [id] { scroll-margin-top: 80px; }
.dialog-open { overflow: hidden; }
.lightbox {
  width: min(92vw, 1100px);
  max-width: none;
  max-height: 92vh;
  padding: 0;
  border: 0;
  border-radius: 12px;
  overflow: visible;
  background: transparent;
  color: var(--white);
}
.lightbox::backdrop { background: rgba(0, 0, 0, .9); }
.lightbox-panel { position: relative; display: grid; gap: 10px; justify-items: center; }
.lightbox-picture[hidden] { display: none; }
.lightbox-img { max-width: 92vw; max-height: 80vh; width: auto; height: auto; object-fit: contain; border-radius: 8px; }
.lightbox-caption { max-width: 70ch; text-align: center; }
.lightbox-error { padding: 32px; border-radius: 8px; background: var(--navy); }
.lightbox-close {
  position: absolute;
  z-index: 1;
  top: 8px;
  right: 8px;
  min-width: 44px;
  border: 0;
  border-radius: 999px;
  background: var(--white);
  color: var(--navy);
  cursor: pointer;
}
.mobile-bar { padding-bottom: env(safe-area-inset-bottom); }
body { padding-bottom: calc(58px + env(safe-area-inset-bottom)); }
@media (min-width: 769px) { body { padding-bottom: 0; } }
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after {
    scroll-behavior: auto !important;
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
  }
  .gallery-item:hover img,
  .gallery-item:focus-visible img { transform: none; }
}
```

- [ ] **Step 5: Implement the Dialog and FAQ behavior**

Create `public/main.v2.js` with:

```javascript
"use strict";

const dialog = document.getElementById("lightbox");
const picture = dialog.querySelector(".lightbox-picture");
const webpSource = dialog.querySelector(".lightbox-source-webp");
const image = dialog.querySelector(".lightbox-img");
const caption = dialog.querySelector(".lightbox-caption");
const errorMessage = dialog.querySelector(".lightbox-error");
const closeButton = dialog.querySelector(".lightbox-close");
let opener = null;

function openLightbox(button) {
  if (typeof dialog.showModal !== "function") {
    window.location.href = button.dataset.jpeg;
    return;
  }
  opener = button;
  caption.textContent = button.dataset.caption;
  image.alt = button.dataset.caption;
  image.width = Number(button.dataset.width);
  image.height = Number(button.dataset.height);
  errorMessage.hidden = true;
  picture.hidden = false;
  webpSource.srcset = button.dataset.webp;
  image.src = button.dataset.jpeg;
  document.documentElement.classList.add("dialog-open");
  dialog.showModal();
  closeButton.focus();
}

document.querySelector(".gallery-grid").addEventListener("click", (event) => {
  const button = event.target.closest(".gallery-item");
  if (button) openLightbox(button);
});

closeButton.addEventListener("click", () => dialog.close());

dialog.addEventListener("click", (event) => {
  const bounds = dialog.getBoundingClientRect();
  const outside = event.clientX < bounds.left || event.clientX > bounds.right
    || event.clientY < bounds.top || event.clientY > bounds.bottom;
  if (outside) dialog.close();
});

image.addEventListener("error", () => {
  picture.hidden = true;
  errorMessage.hidden = false;
});

dialog.addEventListener("close", () => {
  document.documentElement.classList.remove("dialog-open");
  image.removeAttribute("src");
  webpSource.removeAttribute("srcset");
  picture.hidden = false;
  errorMessage.hidden = true;
  if (opener) opener.focus();
  opener = null;
});

const faqItems = document.querySelectorAll(".faq-item");
faqItems.forEach((item) => item.addEventListener("toggle", () => {
  if (item.open) {
    faqItems.forEach((other) => {
      if (other !== item) other.open = false;
    });
  }
}));
```

- [ ] **Step 6: Run tests and manual keyboard checks**

Run: `venv/bin/python -m unittest tests.test_site_quality -v`

Expected: all tests pass.

With the local server still running, verify in order using only the keyboard: Skip Link focuses main content; both Header CTAs focus visibly; each Gallery button opens the Dialog; focus starts on Close; Escape closes; focus returns to the originating thumbnail; FAQ summaries toggle; the fixed mobile CTA never covers focused content.

Temporarily change one `data-jpeg` in DevTools to a missing path. Expected: the Dialog announces「圖片載入失敗，請稍後再試。」and Close remains usable.

- [ ] **Step 7: Commit the accessibility changes**

```bash
git add tests/test_site_quality.py public/index.html public/styles.v2.css public/main.v2.js
git commit -m "fix(a11y): add accessible dialog and keyboard support"
```

---

### Task 5: Add canonical SEO, structured data, crawl files and custom 404

**Files:**
- Modify: `tests/test_site_quality.py`
- Modify: `public/index.html`
- Modify: `public/styles.v2.css`
- Create: `public/favicon-v2.svg`
- Create: `public/robots.txt`
- Create: `public/sitemap.xml`
- Create: `public/404.html`
- Create: `public/llms.txt`

**Interfaces:**
- Consumes: canonical URL, confirmed business facts and `og-songzaka-v2-1200x630.jpg`.
- Produces: indexable homepage metadata, two valid JSON-LD objects, real top-level 404 and crawl discovery files.

- [ ] **Step 1: Add failing SEO and crawl-file tests**

Add imports `json` and `xml.etree.ElementTree as ET` to `tests/test_site_quality.py`, then add:

```python
    def test_canonical_and_social_metadata_are_absolute(self):
        self.assertIn('<link rel="canonical" href="https://songzaka-moving.pages.dev/">', HTML)
        self.assertIn('<meta property="og:url" content="https://songzaka-moving.pages.dev/">', HTML)
        self.assertIn('content="https://songzaka-moving.pages.dev/images/web/og-songzaka-v2-1200x630.jpg"', HTML)
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', HTML)

    def test_json_ld_contains_only_confirmed_business_facts(self):
        blocks = re.findall(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            HTML,
            re.DOTALL,
        )
        data = [json.loads(block) for block in blocks]
        self.assertEqual({item["@type"] for item in data}, {"MovingCompany", "FAQPage"})
        moving = next(item for item in data if item["@type"] == "MovingCompany")
        self.assertEqual(moving["telephone"], "+886916383872")
        self.assertEqual(moving["areaServed"], "新竹以北")
        for forbidden in ("address", "priceRange", "aggregateRating", "review", "logo"):
            self.assertNotIn(forbidden, moving)

    def test_robots_sitemap_404_and_llms_exist(self):
        robots = (PUBLIC / "robots.txt").read_text(encoding="utf-8")
        self.assertEqual(robots, "User-agent: *\nAllow: /\n\nSitemap: https://songzaka-moving.pages.dev/sitemap.xml\n")
        root = ET.parse(PUBLIC / "sitemap.xml").getroot()
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        self.assertEqual(root.findtext("s:url/s:loc", namespaces=namespace), "https://songzaka-moving.pages.dev/")
        not_found = (PUBLIC / "404.html").read_text(encoding="utf-8")
        self.assertIn('content="noindex, follow"', not_found)
        self.assertIn('href="/"', not_found)
        self.assertIn('href="tel:0916383872"', not_found)
        llms = (PUBLIC / "llms.txt").read_text(encoding="utf-8")
        self.assertIn("https://songzaka-moving.pages.dev/", llms)
        self.assertIn("新竹以北", llms)
```

- [ ] **Step 2: Run tests and verify SEO files are missing**

Run: `venv/bin/python -m unittest tests.test_site_quality -v`

Expected: accessibility/performance tests pass; new SEO tests fail.

- [ ] **Step 3: Replace the homepage metadata with exact canonical values**

At the top of `public/index.html`, keep charset first and viewport second, then set:

```html
<title>新竹以北搬家公司｜搬家與廢棄物清運｜松坂搬家</title>
<meta name="description" content="松坂搬家提供新竹以北住家搬家、公司搬遷、家具重物搬運與廢棄物清運服務。24 小時客服、全年無休，歡迎致電 0916383872 或加 LINE 免費估價。">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="https://songzaka-moving.pages.dev/">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_TW">
<meta property="og:title" content="新竹以北搬家公司｜搬家與廢棄物清運｜松坂搬家">
<meta property="og:description" content="松坂搬家提供新竹以北住家搬家、公司搬遷、家具重物搬運與廢棄物清運服務。24 小時客服、全年無休，歡迎致電 0916383872 或加 LINE 免費估價。">
<meta property="og:url" content="https://songzaka-moving.pages.dev/">
<meta property="og:image" content="https://songzaka-moving.pages.dev/images/web/og-songzaka-v2-1200x630.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="松坂搬家人員與待搬運家具">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="新竹以北搬家公司｜搬家與廢棄物清運｜松坂搬家">
<meta name="twitter:description" content="松坂搬家提供新竹以北搬家與廢棄物清運服務，24 小時客服、全年無休。">
<meta name="twitter:image" content="https://songzaka-moving.pages.dev/images/web/og-songzaka-v2-1200x630.jpg">
<link rel="icon" href="favicon-v2.svg" type="image/svg+xml">
```

- [ ] **Step 4: Add exact MovingCompany and FAQPage JSON-LD**

Add these two `<script type="application/ld+json">` elements in `<head>`; the FAQ answers must remain identical to visible HTML:

```json
{
  "@context": "https://schema.org",
  "@type": "MovingCompany",
  "@id": "https://songzaka-moving.pages.dev/#business",
  "name": "松坂搬家",
  "url": "https://songzaka-moving.pages.dev/",
  "telephone": "+886916383872",
  "image": "https://songzaka-moving.pages.dev/images/web/og-songzaka-v2-1200x630.jpg",
  "areaServed": "新竹以北",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+886916383872",
    "contactType": "customer service",
    "availableLanguage": "zh-Hant",
    "hoursAvailable": {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": [
        "https://schema.org/Monday",
        "https://schema.org/Tuesday",
        "https://schema.org/Wednesday",
        "https://schema.org/Thursday",
        "https://schema.org/Friday",
        "https://schema.org/Saturday",
        "https://schema.org/Sunday"
      ],
      "opens": "00:00",
      "closes": "23:59"
    }
  }
}
```

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "怎麼報價？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "可電話或加 LINE 告知物品與樓層，我們提供估價。"
      }
    },
    {
      "@type": "Question",
      "name": "服務範圍到哪？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "新竹以北皆可服務，詳細範圍歡迎來電洽詢。"
      }
    },
    {
      "@type": "Question",
      "name": "大型廢棄物能一起清嗎？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "可以，搬家同時可代清運舊家具與大型垃圾。"
      }
    },
    {
      "@type": "Question",
      "name": "假日有服務嗎？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "24 小時客服，全年無休，歡迎隨時來電或加 LINE 預約。"
      }
    }
  ]
}
```

Wrap each object in its own JSON-LD script tag; do not merge them into a graph because the tests expect two top-level objects.

- [ ] **Step 5: Create crawl files, favicon and 404**

Create `public/robots.txt`:

```text
User-agent: *
Allow: /

Sitemap: https://songzaka-moving.pages.dev/sitemap.xml
```

Create `public/sitemap.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://songzaka-moving.pages.dev/</loc>
    <lastmod>2026-07-17</lastmod>
  </url>
</urlset>
```

Create `public/llms.txt`:

```markdown
# 松坂搬家

> 松坂搬家提供新竹以北的住家搬家、公司搬遷、家具重物搬運與廢棄物清運服務。

## 主要頁面

- [松坂搬家首頁](https://songzaka-moving.pages.dev/)

## 服務與聯絡

- 服務範圍：新竹以北
- 客服時間：24 小時客服、全年無休
- 電話：0916383872
- LINE：https://lin.ee/VOLz2Qq
```

Create `public/favicon-v2.svg` with the current favicon artwork:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#0F2A4A"/>
  <text x="32" y="44" font-size="38" font-family="sans-serif" font-weight="700"
    text-anchor="middle" fill="#ffffff">松</text>
</svg>
```

Create `public/404.html` as this complete HTML5 document:

```html
<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>找不到頁面｜松坂搬家</title>
  <meta name="robots" content="noindex, follow">
  <link rel="icon" href="/favicon-v2.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/styles.v2.css">
</head>
<body>
  <a class="skip-link" href="#main-content">跳到主要內容</a>
  <main id="main-content" class="error-page" tabindex="-1">
    <p class="error-code">404</p>
    <h1>找不到這個頁面</h1>
    <p>網址可能已變更，您可以返回首頁，或直接聯絡松坂搬家。</p>
    <div class="error-actions">
      <a class="btn" href="/">返回首頁</a>
      <a class="btn btn-phone" href="tel:0916383872"><span aria-hidden="true">📞</span> 撥打 0916383872</a>
      <a class="btn btn-line" href="https://lin.ee/VOLz2Qq" target="_blank" rel="noopener" aria-label="加 LINE，在新分頁開啟"><span aria-hidden="true">💬</span> 加 LINE</a>
    </div>
  </main>
</body>
</html>
```

Add `.error-page`, `.error-code` and `.error-actions` rules to center the error page, limit text width and wrap the three 44px actions without horizontal overflow.

- [ ] **Step 6: Run SEO/static tests and local route checks**

Run:

```bash
venv/bin/python -m unittest tests.test_site_quality -v
curl -I http://127.0.0.1:4173/robots.txt
curl -I http://127.0.0.1:4173/sitemap.xml
curl -I http://127.0.0.1:4173/404.html
```

Expected: all tests pass and all three files return `200` locally. The actual missing-route `404` status is a Cloudflare Pages deployment check in Task 7 because Python's static server has different fallback behavior.

- [ ] **Step 7: Commit SEO and crawl resources**

```bash
git add tests/test_site_quality.py public/index.html public/styles.v2.css public/favicon-v2.svg public/robots.txt public/sitemap.xml public/404.html public/llms.txt
git commit -m "feat(seo): add canonical metadata and crawl resources"
```

---

### Task 6: Enforce security headers and immutable asset caching

**Files:**
- Modify: `tests/test_site_quality.py`
- Modify: `public/_headers`

**Interfaces:**
- Consumes: versioned CSS, JS, favicon and image paths.
- Produces: Cloudflare Pages header rules with one broad security block and non-overlapping Cache-Control blocks.

- [ ] **Step 1: Add failing header-policy tests**

Add this method to `SiteQualityTests`:

```python
    def test_security_and_cache_header_contract(self):
        headers = (PUBLIC / "_headers").read_text(encoding="utf-8")
        global_block = headers.split("/styles.v2.css", 1)[0]
        for required in (
            "Content-Security-Policy:",
            "default-src 'self'",
            "frame-ancestors 'none'",
            "require-trusted-types-for 'script'",
            "Strict-Transport-Security: max-age=31536000; includeSubDomains",
            "X-Content-Type-Options: nosniff",
            "X-Frame-Options: DENY",
            "Cross-Origin-Opener-Policy: same-origin",
            "Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()",
        ):
            self.assertIn(required, global_block)
        self.assertNotIn("unsafe-inline", headers)
        self.assertNotIn("unsafe-eval", headers)
        self.assertNotIn("Cross-Origin-Embedder-Policy", headers)
        self.assertNotIn("Cache-Control", global_block)
        self.assertEqual(headers.count("Cache-Control: public, max-age=31536000, immutable"), 4)
```

- [ ] **Step 2: Run tests and verify header failures**

Run: `venv/bin/python -m unittest tests.test_site_quality -v`

Expected: only `test_security_and_cache_header_contract` fails.

- [ ] **Step 3: Replace `_headers` with exact route blocks**

Set `public/_headers` to:

```text
# Cloudflare Pages security headers
/*
  Content-Security-Policy: default-src 'self'; base-uri 'self'; object-src 'none'; frame-src 'none'; frame-ancestors 'none'; form-action 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; media-src 'none'; manifest-src 'self'; upgrade-insecure-requests; require-trusted-types-for 'script'; trusted-types 'none'
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Cross-Origin-Opener-Policy: same-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()

# Versioned assets may be cached for one year.
/styles.v2.css
  Cache-Control: public, max-age=31536000, immutable

/main.v2.js
  Cache-Control: public, max-age=31536000, immutable

/favicon-v2.svg
  Cache-Control: public, max-age=31536000, immutable

/images/web/*
  Cache-Control: public, max-age=31536000, immutable
```

Do not add Cache-Control to `/*`; Cloudflare Pages supplies `public, max-age=0, must-revalidate` for non-versioned responses, and overlapping custom rules with the same header name would be combined.

- [ ] **Step 4: Run all automated tests**

Run:

```bash
venv/bin/python -m unittest discover -s tests -v
git diff --check
```

Expected: every discovered test passes; `git diff --check` has no output.

- [ ] **Step 5: Commit the security policy**

```bash
git add tests/test_site_quality.py public/_headers
git commit -m "feat(security): add strict headers and cache policy"
```

---

### Task 7: Remove superseded files and run full acceptance checks

**Files:**
- Delete: `public/styles.css`
- Delete: `public/main.js`
- Delete: `public/favicon.svg`
- Delete: `public/images/web/hero.jpg`
- Delete: `public/images/web/svc-home.jpg`, `svc-office.jpg`, `svc-heavy.jpg`, `svc-waste.jpg`
- Delete: `public/images/web/g01.jpg` through `g11.jpg`
- Verify: all created and modified files from Tasks 1–6

**Interfaces:**
- Consumes: complete v2 site and test suites.
- Produces: clean deploy directory, Lighthouse reports in `/tmp`, and an explicit list of any deployment-only checks that cannot yet run.

- [ ] **Step 1: Prove old files are unreferenced**

Run:

```bash
rg -n "styles\.css|main\.js|favicon\.svg|images/web/(hero|svc-(home|office|heavy|waste)|g[0-9]{2})\.jpg" public/index.html public/404.html public/styles.v2.css public/main.v2.js public/robots.txt public/sitemap.xml public/llms.txt
```

Expected: no matches.

- [ ] **Step 2: Remove only the explicit superseded files**

Delete the 19 exact files listed in this task. Do not delete `images/`, any `*-v2-*` file, `.vscode/settings.json`, or any unrelated file:

```bash
rm public/styles.css public/main.js public/favicon.svg public/images/web/hero.jpg public/images/web/svc-home.jpg public/images/web/svc-office.jpg public/images/web/svc-heavy.jpg public/images/web/svc-waste.jpg public/images/web/g01.jpg public/images/web/g02.jpg public/images/web/g03.jpg public/images/web/g04.jpg public/images/web/g05.jpg public/images/web/g06.jpg public/images/web/g07.jpg public/images/web/g08.jpg public/images/web/g09.jpg public/images/web/g10.jpg public/images/web/g11.jpg
```

- [ ] **Step 3: Run the complete local verification suite**

Run:

```bash
venv/bin/python scripts/blur.py --check
venv/bin/python -m unittest discover -s tests -v
node --check public/main.v2.js
git diff --check
git status --short
```

Expected: manifest reports 89 outputs; every discovered test passes; Node syntax check and diff check have no output; status contains only this task's deletions plus the pre-existing `.vscode/settings.json` change.

- [ ] **Step 4: Perform responsive, zoom, motion and keyboard browser checks**

With `python3 -m http.server 4173 -d public` running, inspect widths 320, 375, 768 and 1440. At each width confirm no content overflow, no missing image and both CTA destinations. At 200% zoom confirm no content-only horizontal scrolling. Emulate `prefers-reduced-motion: reduce` and confirm smooth scrolling, Gallery scale and transitions stop.

Using only the keyboard and VoiceOver, verify Skip Link, headings, regions, descriptive Gallery names, Dialog title/description, Escape, focus return, FAQ and fixed mobile actions. Confirm the focus ring remains visible against white, navy, orange and green surfaces.

Disable JavaScript and reload once. Expected: service content, Gallery thumbnails, FAQ native expansion, telephone and LINE links remain available; only Gallery enlargement and single-open FAQ behavior are absent.

- [ ] **Step 5: Run three local Lighthouse 13.4.0 mobile audits**

Run the following command three times, changing only the output number from 1 through 3:

```bash
npx --yes lighthouse@13.4.0 http://127.0.0.1:4173/ --quiet --output=json --output-path=/tmp/songzaka-mobile-1.json --only-categories=performance,accessibility,best-practices,seo --chrome-flags="--headless"
```

Summarize the three reports:

```bash
jq -s '{
  performance_median: ([.[].categories.performance.score * 100] | sort | .[1]),
  accessibility_min: ([.[].categories.accessibility.score * 100] | min),
  best_practices_min: ([.[].categories["best-practices"].score * 100] | min),
  seo_min: ([.[].categories.seo.score * 100] | min),
  lcp_median_ms: ([.[].audits["largest-contentful-paint"].numericValue] | sort | .[1]),
  cls_median: ([.[].audits["cumulative-layout-shift"].numericValue] | sort | .[1]),
  tbt_median_ms: ([.[].audits["total-blocking-time"].numericValue] | sort | .[1]),
  bytes_median: ([.[].audits["total-byte-weight"].numericValue] | sort | .[1])
}' /tmp/songzaka-mobile-1.json /tmp/songzaka-mobile-2.json /tmp/songzaka-mobile-3.json
```

Required result: Performance median ≥ 90; Accessibility, Best Practices and SEO minimum = 100; LCP median ≤ 2500 ms; CLS median ≤ 0.1; TBT median ≤ 200 ms; transferred-byte median ≤ 1,572,864.

- [ ] **Step 6: Run one desktop Lighthouse and inspect the LCP request chain**

Run:

```bash
npx --yes lighthouse@13.4.0 http://127.0.0.1:4173/ --quiet --preset=desktop --output=json --output-path=/tmp/songzaka-desktop.json --only-categories=performance,accessibility,best-practices,seo --chrome-flags="--headless"
jq '{performance: (.categories.performance.score * 100), accessibility: (.categories.accessibility.score * 100), best_practices: (.categories["best-practices"].score * 100), seo: (.categories.seo.score * 100), lcp_ms: .audits["largest-contentful-paint"].numericValue}' /tmp/songzaka-desktop.json
```

Expected: all category scores are at least 90, Accessibility/Best Practices/SEO are 100, and the Hero request is discovered from initial HTML rather than CSS.

- [ ] **Step 7: Commit the cleanup**

Stage only the explicit deletions and verify staged scope before committing:

```bash
git add public/styles.css public/main.js public/favicon.svg public/images/web/hero.jpg public/images/web/svc-home.jpg public/images/web/svc-office.jpg public/images/web/svc-heavy.jpg public/images/web/svc-waste.jpg public/images/web/g01.jpg public/images/web/g02.jpg public/images/web/g03.jpg public/images/web/g04.jpg public/images/web/g05.jpg public/images/web/g06.jpg public/images/web/g07.jpg public/images/web/g08.jpg public/images/web/g09.jpg public/images/web/g10.jpg public/images/web/g11.jpg
git diff --cached --name-status
git commit -m "chore: remove superseded site assets"
```

- [ ] **Step 8: Run deployment-only acceptance checks when a Pages deployment exists**

Do not push or deploy without separate user authorization. Once the commit is available on a Cloudflare Pages preview or production deployment, run:

```bash
curl -I https://songzaka-moving.pages.dev/
curl -I https://songzaka-moving.pages.dev/styles.v2.css
curl -I https://songzaka-moving.pages.dev/images/web/hero-v2-1280.webp
curl -I https://songzaka-moving.pages.dev/robots.txt
curl -I https://songzaka-moving.pages.dev/sitemap.xml
curl -I https://songzaka-moving.pages.dev/quality-check-missing-20260717
```

Expected:

- Homepage, robots and sitemap return `200`; missing path returns `404` and renders the custom page.
- Homepage includes CSP, HSTS, nosniff, DENY frame control, COOP, Referrer Policy and Permissions Policy.
- Versioned CSS and Hero include `Cache-Control: public, max-age=31536000, immutable`.
- Homepage/non-versioned files use Cloudflare's revalidating cache behavior.

Validate both JSON-LD blocks with Schema.org Validator or Google Rich Results Test. Then rerun the three mobile production Lighthouse audits and compare against the same thresholds from Step 5. If no preview/deployment authority is available, report Step 8 as pending instead of claiming online completion.

Submit the production URL to the W3C Nu HTML Checker and require zero HTML errors. Review the browser console at the production URL and require zero CSP, JavaScript, mixed-content or failed-resource errors.

---

## Completion Evidence

Before declaring the work complete, retain or report:

- Output of `venv/bin/python -m unittest discover -s tests -v`.
- Output of `git diff --check` and final `git status --short`.
- The three mobile Lighthouse summaries and one desktop summary.
- Manual keyboard, VoiceOver, 320px, 200% zoom and reduced-motion results.
- Cloudflare HTTP status/header results, or a clear statement that deployment authorization is still required.
- Final commit list; `.vscode/settings.json` must remain unstaged and unmodified by this work.

## Primary References

- Pillow package and Python support: `https://pypi.org/project/pillow/`
- Cloudflare Pages custom headers: `https://developers.cloudflare.com/pages/configuration/headers/`
- Cloudflare Pages custom 404 and default cache behavior: `https://developers.cloudflare.com/pages/configuration/serving-pages/`
