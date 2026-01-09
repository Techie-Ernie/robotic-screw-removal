import os, json, math, random, cv2, numpy as np
from pathlib import Path

OUT_DIR = r"C:\NRP_script\screw2d"   
N_IMAGES = 500
W, H = 2028, 1520
SCREW_MIN, SCREW_MAX = 4, 10
R_MIN, R_MAX = 10, 12 

os.makedirs(os.path.join(OUT_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "masks"), exist_ok=True)

rng = random.Random(1337)
ann = {"images": [], "annotations": [], "categories": [{"id":1, "name":"screw"}]}
ann_id = 1

def vignette(img, strength=0.6):
    yy, xx = np.indices(img.shape[:2])
    cx, cy = img.shape[1]/2, img.shape[0]/2
    r = np.sqrt(((xx-cx)/cx)**2 + ((yy-cy)/cy)**2)
    v = 1.0 - strength*np.clip(r, 0, 1)
    return (img.astype(np.float32) * v[...,None]).clip(0,255).astype(np.uint8)

def lighting_gradient(h, w):
    # random linear gradient 
    x = np.linspace(0, 1, w, dtype=np.float32)
    y = np.linspace(0, 1, h, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    a, b, c = rng.uniform(-0.7,0.7), rng.uniform(-0.7,0.7), rng.uniform(-0.2,0.2)
    grad = a*xx + b*yy + c
    grad = (grad - grad.min())/(grad.max()-grad.min()+1e-6)
    return grad

def add_jpeg_noise(img, q=70):
    enc = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), q])[1]
    return cv2.imdecode(enc, cv2.IMREAD_COLOR)

def draw_screw(img, mask, cx, cy, r, orient_deg):
    # base disc with radial shading to mimic metal
    yy, xx = np.indices((H, W))
    dist = np.sqrt((xx-cx)**2 + (yy-cy)**2)
    disc = dist <= r
    # metal shading: dot with “light dir”
    theta = math.radians(rng.uniform(-180,180))
    lx, ly = math.cos(theta), math.sin(theta)
    nx = (xx - cx) / (r+1e-6); ny = (yy - cy) / (r+1e-6)
    nrm = np.sqrt(nx*nx + ny*ny) + 1e-6
    nx, ny = nx/nrm, ny/nrm
    ndotl = np.clip(nx*lx + ny*ly, 0, 1)
    # base silver color + subtle tint
    base = np.stack([
        170 + 40*ndotl,
        170 + 40*ndotl,
        175 + 45*ndotl
    ], axis=-1)
    base = base.astype(np.uint8)
    img[disc] = base[disc]

    # dark rim
    rim = (dist <= r) & (dist >= r*0.85)
    img[rim] = (img[rim] * 0.6).astype(np.uint8)

    # specular glint
    glx = cx + int(lx * r*0.4); gly = cy + int(ly * r*0.4)
    cv2.circle(img, (glx, gly), max(1, r//5), (255,255,255), -1)

    # two orthogonal rectangles rotated by orient_deg
    rect_w, rect_t = int(r*1.4), max(1, r//5)
    overlay = np.zeros_like(img)
    for ang in [orient_deg, orient_deg+90]:
        M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)
        box = np.zeros((H, W), np.uint8)
        cv2.rectangle(box, (cx-rect_w//2, cy-rect_t//2),
                            (cx+rect_w//2, cy+rect_t//2), 255, -1)
        box = cv2.warpAffine(box, M, (W, H), flags=cv2.INTER_NEAREST)
        overlay[box>0] = (40,40,45)
    # darken where overlay present and inside disc
    sel = (overlay[:,:,0] > 0) & disc
    img[sel] = (img[sel] * 0.35).astype(np.uint8)
    
    # update mask
    mask[disc] = 255

def random_plate():
    # background “laptop underside”: noisy plastic or brushed metal
    # randomize between random latpop underside images and synthetically generated ones
    choice = random.randint(0,1)
    if choice == 0:
        plate = np.zeros((H, W, 3), np.uint8)
        base = rng.choice([(25,25,28), (200,200,205), (90,95,100)])
        plate[:] = base
        # texture noise
        noise = (np.random.randn(H, W, 3)*rng.uniform(3,12)).astype(np.int16)
        plate = np.clip(plate.astype(np.int16)+noise,0,255).astype(np.uint8)
        # subtle linear gradient
        g = lighting_gradient(H, W)
        plate = (plate.astype(np.float32) * (0.8+0.4*g[...,None])).clip(0,255).astype(np.uint8)
    else:
        print("using laptop underside")
        LAPTOP_UNDERSIDE_DIR = Path("laptop_underside/laptop_underside/")
        files = [f for f in LAPTOP_UNDERSIDE_DIR.iterdir() if f.is_file()]
        file = random.choice(files)
        img = cv2.imread(str(file))
        plate = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA) # need to resize since not all images are of dimensions W, H
    return plate



for i in range(N_IMAGES):
    img = random_plate()
    mask = np.zeros((H, W), np.uint8)
    this = {"id": i, "file_name": f"{i:06d}.png", "width": W, "height": H}
    ann["images"].append(this)

    n = rng.randint(SCREW_MIN, SCREW_MAX)
    for k in range(n):
        r = rng.randint(R_MIN, R_MAX)
        # keep away from borders
        cx = rng.randint(r+6, W-r-6)
        cy = rng.randint(r+6, H-r-6)
        orient = rng.uniform(0, 180)
        draw_screw(img, mask, cx, cy, r, orient)

        bbox = [int(cx-r), int(cy-r), int(2*r), int(2*r)]
        ann["annotations"].append({
            "id": ann_id,
            "image_id": i,
            "category_id": 1,
            "bbox": bbox,
            "iscrowd": 0,
            "keypoints": [int(cx), int(cy), 2],
            "num_keypoints": 1
        })
        ann_id += 1

    # blur, noise, WB, JPEG artifacts to mimic camera
    if rng.random() < 0.6:
        ksz = rng.choice([3,5])
        img = cv2.GaussianBlur(img, (ksz,ksz), rng.uniform(0.2,1.2))
    img = vignette(img, strength=rng.uniform(0.3,0.7))
    gain = rng.uniform(0.9,1.1); bias = rng.randint(-6,6)
    img = np.clip(img.astype(np.int16)*gain + bias, 0, 255).astype(np.uint8)
    img = add_jpeg_noise(img, q=rng.randint(40, 95))

    # save
    cv2.imwrite(os.path.join(OUT_DIR, "images", f"{i:06d}.png"), img)
    cv2.imwrite(os.path.join(OUT_DIR, "masks", f"{i:06d}.png"), mask)

with open(os.path.join(OUT_DIR, "annotations.json"), "w") as f:
    json.dump(ann, f, indent=2)

print("done:", OUT_DIR, "images:", len(ann["images"]), "anns:", len(ann["annotations"]))
