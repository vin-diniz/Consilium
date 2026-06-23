"""
Gera /assets/og-image.jpg 1200x630 (VULN-006).
JPG quality ~82, alvo <300 KB. Card de marca: fundo escuro Consilium,
wordmark "Consilium - Advocacia Empresarial" + tagline, detalhes em gold.
JPG (NAO AVIF) - scrapers WhatsApp/LinkedIn/Facebook nao renderizam AVIF.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1200, 630
BG     = (11, 10, 8)        # #0B0A08 - dark background
GOLD   = (192, 144, 48)     # #C09030 - accent gold
CREAM  = (244, 239, 228)    # #F4EFE4 - main text
MUTED  = (180, 175, 160)    # muted tagline

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# Subtle gradient overlay (top-left to bottom-right)
for y in range(H):
    alpha = int(20 * (1 - y / H))
    if alpha > 0:
        for x in range(0, W, 8):
            r, g, b = BG
            draw.point((x, y), (min(r+alpha, 255), min(g+alpha, 255), min(b+alpha, 255)))

# Try to load nice fonts; fall back to defaults if absent
font_dirs = [
    "C:/Windows/Fonts",
    "/usr/share/fonts",
    "/usr/local/share/fonts",
]
def find_font(*candidates):
    for d in font_dirs:
        for c in candidates:
            p = Path(d) / c
            if p.is_file():
                return str(p)
    return None

serif_path = find_font("georgia.ttf", "georgiab.ttf", "Georgia.ttf", "DejaVuSerif-Bold.ttf")
sans_path  = find_font("segoeui.ttf", "Inter-Regular.ttf", "Arial.ttf", "DejaVuSans.ttf")

try:
    f_brand   = ImageFont.truetype(serif_path, 86) if serif_path else ImageFont.load_default()
    f_suffix  = ImageFont.truetype(sans_path, 32)  if sans_path  else ImageFont.load_default()
    f_tagline = ImageFont.truetype(sans_path, 26)  if sans_path  else ImageFont.load_default()
    f_footer  = ImageFont.truetype(sans_path, 22)  if sans_path  else ImageFont.load_default()
except Exception:
    f_brand = f_suffix = f_tagline = f_footer = ImageFont.load_default()

# Gold accent bar (top)
bar_h = 6
draw.rectangle([(0, 0), (W, bar_h)], fill=GOLD)

# Center wordmark
brand_text = "Consilium"
bbox = draw.textbbox((0, 0), brand_text, font=f_brand)
bw = bbox[2] - bbox[0]
bh = bbox[3] - bbox[1]
brand_x = (W - bw) // 2
brand_y = 200
draw.text((brand_x, brand_y), brand_text, font=f_brand, fill=CREAM)

# Vertical divider line
divider_y_top = brand_y + bh + 30
divider_y_bot = divider_y_top + 4
draw.line([(brand_x + bw // 4, divider_y_top), (brand_x + bw * 3 // 4, divider_y_top)], fill=GOLD, width=2)

# Suffix line
suffix_text = "ADVOCACIA EMPRESARIAL"
sbbox = draw.textbbox((0, 0), suffix_text, font=f_suffix)
sw = sbbox[2] - sbbox[0]
sx = (W - sw) // 2
sy = divider_y_top + 28
draw.text((sx, sy), suffix_text, font=f_suffix, fill=GOLD)

# Tagline (lower third)
tagline_text = "Hub juridico para pequenas e medias empresas"
tbbox = draw.textbbox((0, 0), tagline_text, font=f_tagline)
tw = tbbox[2] - tbbox[0]
tx = (W - tw) // 2
ty = sy + 60
draw.text((tx, ty), tagline_text, font=f_tagline, fill=MUTED)

# Footer-right URL
url_text = "consiliumadvogados.com.br"
ubbox = draw.textbbox((0, 0), url_text, font=f_footer)
uw = ubbox[2] - ubbox[0]
draw.text((W - uw - 60, H - 60), url_text, font=f_footer, fill=GOLD)

# Footer-left badge
badge_text = "OAB/PR 122.982"
draw.text((60, H - 60), badge_text, font=f_footer, fill=MUTED)

# Save JPG quality 82, optimize
out = Path("assets/og-image.jpg")
out.parent.mkdir(parents=True, exist_ok=True)
img.save(out, "JPEG", quality=82, optimize=True, progressive=True)
print(f"OK {out} - {out.stat().st_size} bytes ({out.stat().st_size / 1024:.1f} KB)")
