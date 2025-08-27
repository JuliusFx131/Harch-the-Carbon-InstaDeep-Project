# Biomass Inference with Docker

This repository provides a Dockerized solution to run biomass inference on satellite image chips using a trained U-Net model.

---

## Project Structure

```
./Julius Fx/
├── Dockerfile
├── requirements.txt
├── app.py
├── .dockerignore
└── unet_weights.pth   # Your trained model file
```

---

## 1️⃣ Build the Docker Image

```bash
docker build --no-cache -t biomass-inference .
```

> `--no-cache` ensures a fresh build. Omit it for faster rebuilds after the first build.

---

## 2️⃣ Run Inference

### Windows (PowerShell)

```powershell
docker run --rm -it `
  -v "D:\ZINDI\hack-the-carbon\test\chips:/input_chips" `
  -v "C:\Users\PC\Downloads\Julius Fx\unet_weights.pth:/app/model_weights.pth:ro" `
  -v "D:\predictions:/output" `
  juliusfx/biomass-inference:latest `
  python app.py `
    --chips_dir /input_chips `
    --model_weights /app/model_weights.pth `
    --output_dir /output
```

### Linux / macOS (bash)

```bash
docker run --rm -it \
  -v "/home/user/hack-the-carbon/test/chips:/input_chips" \
  -v "/home/user/unet_weights.pth:/app/model_weights.pth:ro" \
  -v "/home/user/predictions:/output" \
  biomass-inference:fixed \
  python app.py \
    --chips_dir /input_chips \
    --model_weights /app/model_weights.pth \
    --output_dir /output
```

---

## 3️⃣ Notes

* **Input folder**: `/input_chips` inside the container → mount your host chips folder here.
* **Model file**: `/app/model_weights.pth` inside the container → mount your trained `.pth` file as read-only (`:ro`).
* **Output folder**: `/output` inside the container → predictions will be saved here and appear on your host machine.
* Make sure Docker has **access to the drive** where your files are stored (Windows: Docker Desktop → Resources → File Sharing).

---

## 4️⃣ Input

The model expects input `.tif` files with shape **3 timesteps × 6 spectral bands × 256 × 256** (Height × Width). Bands are ordered as:  

- **Timestep 1:** Blue_t1, Green_t1, Red_t1, NIR_t1, SWIR1_t1, SWIR2_t1  
- **Timestep 2:** Blue_t2, Green_t2, Red_t2, NIR_t2, SWIR1_t2, SWIR2_t2  
- **Timestep 3:** Blue_t3, Green_t3, Red_t3, NIR_t3, SWIR1_t3, SWIR2_t3  

Filenames should follow this pattern:  

```
chip_01.tif
chip_02.tif
...
```

---

## 4️⃣ Output

Predictions are saved as `.tif` files in the output folder. File names follow this pattern:

```
chip_01.tif  ->  prediction_01.tif
chip_02.tif  ->  prediction_02.tif
...
```

---

## 5️⃣ Sharing Your Docker Image

**Option 1: Docker Hub**

```bash
docker tag biomass-inference:fixed juliusfx/biomass-inference:latest
docker push juliusfx/biomass-inference:latest
```

Other users can pull and run:

```bash
docker pull juliusfx/biomass-inference:latest
```

**Option 2: Docker Image File**

```bash
docker save -o biomass-inference.tar biomass-inference:fixed
```

Other users can load it:

```bash
docker load -i biomass-inference.tar
```

---

## 6️⃣ License

Apache

