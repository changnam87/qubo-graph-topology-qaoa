from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

img1_path = ROOT / "results" / "rq1_extended" / "fig_rq1a_edges_vs_transpiled_depth.png"
img2_path = ROOT / "results" / "rq1_extended" / "fig_rq1b_topology_distance_vs_swap_count.png"
out_path = ROOT / "figures" / "fig_rq1_graph_topology_complexity.png"

out_path.parent.mkdir(parents=True, exist_ok=True)

img1 = Image.open(img1_path).convert("RGB")
img2 = Image.open(img2_path).convert("RGB")

target_h = max(img1.height, img2.height)

def resize_to_height(img, target_h):
    new_w = int(img.width * target_h / img.height)
    return img.resize((new_w, target_h), Image.LANCZOS)

img1 = resize_to_height(img1, target_h)
img2 = resize_to_height(img2, target_h)

gap = 30
pad = 20

canvas_w = img1.width + img2.width + gap + 2 * pad
canvas_h = target_h + 2 * pad

canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
canvas.paste(img1, (pad, pad))
canvas.paste(img2, (pad + img1.width + gap, pad))

canvas.save(out_path, dpi=(300, 300))

print(f"Saved: {out_path}")
