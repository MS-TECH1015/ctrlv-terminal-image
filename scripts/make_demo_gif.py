"""README demo GIF for ctrlv-terminal-image (an illustration, not a screen recording).

usage: python scripts/make_demo_gif.py media/demo.gif [contact_sheet.png]  (needs Pillow and Windows fonts)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 800, 460
FRAMES = 100  # 10 fps
FONTS = "C:/Windows/Fonts/"
mono = ImageFont.truetype(FONTS + "consola.ttf", 15)
mono_s = ImageFont.truetype(FONTS + "consola.ttf", 13)
mono_b = ImageFont.truetype(FONTS + "consolab.ttf", 15)
sym = ImageFont.truetype(FONTS + "seguisym.ttf", 15)
ui = ImageFont.truetype(FONTS + "segoeui.ttf", 13)
ui_b = ImageFont.truetype(FONTS + "segoeuib.ttf", 18)
cap = ImageFont.truetype(FONTS + "segoeuib.ttf", 15)

BG, EDITOR, TITLE, BORDER = (24, 24, 24), (31, 31, 31), (43, 43, 43), (62, 62, 62)
TEXT, DIM, ACCENT, BLUE, RED = (212, 212, 212), (128, 128, 128), (217, 119, 87), (110, 170, 255), (241, 96, 96)
KW, STR = (197, 134, 192), (206, 145, 120)

ERROR_BOX = (400, 70, 770, 150)
SNIP = (390, 60, 780, 160)
INPUT_BOX = (16, 330, 784, 366)
TYPED = "why does this crash?"

CODE = [
    [("import", KW), (" { render } ", TEXT), ("from", KW), (" './ui'", STR)],
    [],
    [("export function", KW), (" App({ items }) {", TEXT)],
    [("  return", KW), (" items.map(renderRow)", TEXT)],
    [("}", TEXT)],
]


def text_runs(d, x, y, runs, font):
    for s, color in runs:
        d.text((x, y), s, font=font, fill=color)
        x += font.getlength(s)
    return x


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def caption_for(f):
    if f < 10:
        return "Claude Code running in the Cursor terminal"
    if f < 36:
        return "1.  Take a screenshot   (Win + Shift + S)"
    if f < 68:
        return "2.  Ctrl+V in the terminal  \u2192  [Image #1]"
    return "3.  Send it. Claude Code reads the image"


def draw_base(d, f):
    d.rectangle((0, 0, W, H), fill=BG)
    # title bar and tab
    d.rectangle((0, 0, W, 30), fill=TITLE)
    d.rectangle((8, 4, 118, 30), fill=EDITOR)
    d.text((22, 8), "app.tsx", font=ui, fill=TEXT)
    d.text((W - 92, 6), "—    ☐    ✕", font=sym, fill=DIM)
    # editor
    d.rectangle((0, 30, W, 200), fill=EDITOR)
    for i, runs in enumerate(CODE):
        y = 50 + i * 22
        d.text((16, y), str(i + 1).rjust(2), font=mono_s, fill=DIM)
        text_runs(d, 48, y, runs, mono_s)
    d.rounded_rectangle(ERROR_BOX, radius=6, fill=(64, 32, 32), outline=RED, width=2)
    d.text((414, 80), "Uncaught TypeError:", font=mono_s, fill=RED)
    d.text((414, 102), "Cannot read properties of undefined", font=mono_s, fill=TEXT)
    d.text((414, 124), "(reading 'map')  at App (app.tsx:4)", font=mono_s, fill=TEXT)
    # terminal panel
    d.line((0, 200, W, 200), fill=BORDER)
    d.text((16, 206), "TERMINAL", font=ui, fill=TEXT)
    d.line((16, 224, 74, 224), fill=TEXT)
    d.text((16, 238), "PS C:\\my-project> claude", font=mono, fill=DIM)
    d.text((16, 262), "Claude Code", font=mono_b, fill=ACCENT)

    if f >= 72:
        x = text_runs(d, 16, 290, [("> ", DIM), ("[Image #1]", BLUE), (" " + TYPED, TEXT)], mono)
        spin = "\u2722\u2733\u2736\u273b\u273d"[(f // 2) % 5]
        d.text((16, 306 - 2), spin, font=sym, fill=ACCENT)
        d.text((36, 306), "Thinking\u2026", font=mono, fill=ACCENT)

    d.rounded_rectangle(INPUT_BOX, radius=6, outline=DIM, width=1)
    runs = [("> ", DIM)]
    if 44 <= f < 72:
        runs += [("[Image #1]", BLUE), (" ", TEXT)]
        runs.append((TYPED[: max(0, f - 48)], TEXT))
    x = text_runs(d, 28, 339, runs, mono)
    typing = 44 <= f < 72
    if typing or (f // 5) % 2 == 0:
        d.rectangle((x + 1, 339, x + 9, 356), fill=TEXT)
    d.text((16, 374), "? for shortcuts", font=mono_s, fill=DIM)

    # caption bar
    d.rectangle((0, 420, W, H), fill=(14, 14, 14))
    c = caption_for(f)
    d.text(((W - cap.getlength(c)) / 2, 430), c, font=cap, fill=(240, 240, 240))


def badge(im, label, center, f, start, length=10):
    if not (start <= f < start + length):
        return
    t = ease((f - start) / 3)
    d = ImageDraw.Draw(im)
    w = ui_b.getlength(label) + 32
    h = 38
    cx, cy = center
    cy = cy + (1 - t) * 10
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=8,
                        fill=(250, 250, 250), outline=(180, 180, 180), width=1)
    d.text((cx - w / 2 + 16, cy - 13), label, font=ui_b, fill=(30, 30, 30))


def snip_overlay(im, f):
    if not (12 <= f < 34):
        return im
    x0, y0, x1, y1 = SNIP
    t = ease((f - 16) / 12) if f >= 16 else 0.0
    cur = (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
    shade = Image.new("RGBA", im.size, (0, 0, 0, 120))
    if f >= 16:
        ImageDraw.Draw(shade).rectangle((x0, y0, cur[0], cur[1]), fill=(0, 0, 0, 0))
    out = Image.alpha_composite(im.convert("RGBA"), shade)
    d = ImageDraw.Draw(out)
    if f >= 16:
        d.rectangle((x0, y0, cur[0], cur[1]), outline=(255, 255, 255), width=1)
    if f < 30:
        cx, cy = cur if f >= 16 else (x0, y0)
        d.line((cx - 9, cy, cx + 9, cy), fill=(255, 255, 255), width=1)
        d.line((cx, cy - 9, cx, cy + 9), fill=(255, 255, 255), width=1)
    if f in (30, 31):
        flash = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(flash).rectangle(SNIP, fill=(255, 255, 255, 170 if f == 30 else 70))
        out = Image.alpha_composite(out, flash)
    return out.convert("RGB")


def toast(im, f):
    if not (32 <= f < 50):
        return
    d = ImageDraw.Draw(im)
    box = (540, 164, 784, 194)
    d.rounded_rectangle(box, radius=6, fill=(52, 52, 52), outline=BORDER)
    d.text((552, 170), "Screenshot copied to clipboard", font=ui, fill=TEXT)


def frame(f):
    im = Image.new("RGB", (W, H))
    draw_base(ImageDraw.Draw(im), f)
    im = snip_overlay(im, f)
    toast(im, f)
    badge(im, "Win + Shift + S", (190, 150), f, 10, 24)
    badge(im, "Ctrl + V", (W / 2, 300), f, 37, 10)
    badge(im, "Enter", (W / 2, 300), f, 66, 7)
    return im


def main():
    out = sys.argv[1]
    frames = [frame(f) for f in range(FRAMES)]
    # one shared palette keeps colors stable between frames
    sample = Image.new("RGB", (W, H * 4))
    for i, f in enumerate((5, 22, 40, 80)):
        sample.paste(frames[f], (0, H * i))
    palette = sample.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    pal_frames = [fr.quantize(palette=palette, dither=Image.Dither.NONE) for fr in frames]
    durations = [100] * FRAMES
    durations[-1] = 1500
    pal_frames[0].save(out, save_all=True, append_images=pal_frames[1:], duration=durations,
                       loop=0, optimize=True, disposal=1)
    if len(sys.argv) > 2:
        picks = (5, 22, 31, 40, 55, 85)
        sheet = Image.new("RGB", (W * 2, H * 3))
        for i, f in enumerate(picks):
            sheet.paste(frames[f], ((i % 2) * W, (i // 2) * H))
        sheet.save(sys.argv[2])


main()
