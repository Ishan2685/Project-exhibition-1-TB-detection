# Tuberculosis Detection from Chest X-rays using Deep Learning

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15%2B-orange.svg)](https://www.tensorflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Domain](https://img.shields.io/badge/Domain-Medical%20Imaging-red.svg)]()

An automated diagnostic pipeline utilizing transfer learning with deep convolutional neural networks (VGG16) to classify chest X-ray radiographs into **Normal** and **Tuberculosis (TB)** positive cases.

---

## 📌 Problem Statement

Tuberculosis (TB), caused by the bacterium *Mycobacterium tuberculosis*, remains one of the world's deadliest infectious diseases. According to the World Health Organization (WHO), TB claims approximately **1.3 million lives annually**, disproportionately impacting low- and middle-income countries. 

While chest radiography (X-ray) is one of the most accessible primary screening modalities for pulmonary tuberculosis, early-stage detection presents notable challenges:
- Subtle, ambiguous radiological patterns (e.g., small infiltrates, cavitation, apical scarring) can be easily missed.
- Severe shortage of expert radiologists in rural and under-resourced healthcare facilities.
- High inter-observer variability and heavy clinical workloads leading to diagnostic delays or diagnostic fatigue.

Deep learning-powered computer-aided detection (CAD) systems provide rapid, consistent, and scalable triaging assistance, facilitating early intervention, reduced transmission rates, and timely patient care.

---

## 📊 Dataset Description

This project utilizes the benchmark **Tuberculosis (TB) Chest X-ray Database** hosted on Kaggle:

- **Source / Curators:** Tawsifur Rahman et al., in collaboration with Hamad Medical Corporation (Qatar), University of Dhaka (Bangladesh), and international research partners.
- **Image Specifications:** 512 × 512 resolution, single-channel (grayscale) / 3-channel PNG format.
- **Distribution:**
  - **Tuberculosis Positive:** 700 images
  - **Normal / Healthy:** 3,500 images
  - **Total:** 4,200 chest X-ray radiographs
- **Class Imbalance Handling:** Addressed via weighted cross-entropy loss, class weighting during training, and targeted data augmentation.

### Citation
If utilizing this dataset or project in academic research, please cite:
```bibtex
@article{rahman2020reliable,
  title={Reliable Tuberculosis Detection using Chest X-ray with Deep Learning, Segmentation and Visualization},
  author={Rahman, Tawsifur and Khandakar, Amith and Kadir, Muhammad A. and Islam, Khandaker R. and Islam, Kazi F. and Mazhar, Risul and Hamid, Tania and Reaz, Mamun B. I. and Boghdady, M. and Kashem, M. A. and Mahbub, Z. B. and Hasan, M. A. and Shamsi, R. and Al-Maadeed, Somaya},
  journal={IEEE Access},
  volume={8},
  pages={191586--191601},
  year={2020},
  publisher={IEEE}
}
```

---

## 🛠 Tech Stack

- **Programming Language:** Python 3.10+
- **Deep Learning Framework:** TensorFlow 2.15+ / Keras
- **Numerical Computing:** NumPy >= 1.24.0
- **Data Visualization & Plotting:** Matplotlib >= 3.7.0
- **Image Processing:** OpenCV / PIL / Keras Preprocessing

---

## 🧠 Model Architecture

The core classifier is built upon **VGG16 Transfer Learning** pre-trained on ImageNet:
1. **Feature Extractor:** VGG16 convolutional backbone (frozen base during initial feature transfer, retaining generalized low-level edge and texture detectors).
2. **Global Feature Aggregation:** Global Average Pooling 2D (GAP) layer reducing spatial dimensionality while avoiding overfitting.
3. **Dense Classification Head:**
   - Dense layer (256 units, ReLU activation) with Batch Normalization
   - Dropout regularization ($p = 0.5$) for robust generalization
   - Output Dense layer (1 unit, Sigmoid activation) for binary classification (`Normal` vs. `Tuberculosis`)
4. **Optimization:** Adam optimizer with binary cross-entropy loss and dynamic learning rate scheduling.

---

## 📁 Project Structure

```text
tb-xray-detection/
├── dataset/
│   ├── Normal/             # 3,500 normal chest X-ray images
│   └── TB/                 # 700 tuberculosis chest X-ray images
├── plots/                  # Training history curves, confusion matrices, ROC plots
├── 06_ethics.md            # Detailed ethics, bias, privacy, and societal impact report
├── main.py                 # End-to-end training and evaluation pipeline
├── README.md               # Project documentation and reproduction guide
└── requirements.txt        # Python dependency manifest
```

---

## 🚀 How to Run

### 1. Prerequisites & Environment Setup
Clone the repository and prepare a Python 3.10+ virtual environment:
```bash
git clone https://github.com/username/tb-xray-detection.git
cd tb-xray-detection
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate
```

### 2. Install Dependencies
Install all required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Download & Extract Dataset
1. Download the [TB Chest X-ray Database from Kaggle](https://www.kaggle.com/datasets/tawsifurrahman/tuberculosis-tb-chest-xray-dataset).
2. Extract the dataset archive into the `dataset/` directory. Ensure the directory structure matches:
   ```text
   dataset/
   ├── Normal/
   └── TB/
   ```

### 4. Run the Pipeline & Scripts

**Option A: Master Pipeline (End-to-End)**
```bash
python main.py
```
This script runs the complete pipeline: dataset loading, EDA, training over 10 epochs, saving `tb_xray_model.keras`, and generating all 9 evaluation plots.

**Option B: Single-Image Clinical Inference Demo (`predict.py`)**
Run instant inference on any chest X-ray image (ideal for live project presentations):
```bash
# Predict on a random test sample:
python predict.py

# Or predict on a specific X-ray image:
python predict.py --image dataset/TB/Tuberculosis-1.png
python predict.py --image dataset/Normal/Normal-1.png
```
This prints the diagnostic classification, probability confidence score, and generates a visual diagnostic figure in `plots/single_prediction.png`.

**Option C: Modular Execution**
```bash
python 01_eda.py          # Exploratory Data Analysis & distribution plots
python 02_preprocessing.py  # Data loading & augmentation verification
python 03_model.py          # VGG16 model architecture summary
python 04_train.py          # Model training with EarlyStopping
python 05_evaluate.py       # Comprehensive test evaluation & metrics calculation
```

---

## 🏆 Final Model Evaluation Performance (Held-Out Test Set: 648 Images)

| Evaluation Metric | Score | Clinical / Technical Significance |
|---|---|---|
| **ROC AUC** | **`95.12%`** | **Exceptional discriminatory capability** between Normal and TB |
| **Sensitivity (Recall)** | **`87.37%`** | **83 of 95 positive TB cases caught** (only 12 missed) |
| **Specificity** | **`85.17%`** | **471 of 553 healthy patients correctly identified** |
| **Test Accuracy** | **`85.49%`** | High overall reliability despite severe 5:1 class imbalance |
| **F1-Score** | **`0.6385`** | Harmonic balance between precision and recall |

### Confusion Matrix
```text
                   Predicted Normal     Predicted TB
Actual Normal            471 (TN)           82 (FP)
Actual TB                 12 (FN)           83 (TP)
```

---

## ⚖️ Ethics, Privacy & Responsible AI

Medical artificial intelligence requires rigorous ethical deliberation, transparency, and safety mechanisms. For an in-depth analysis regarding:
- Demographic bias & domain adaptation
- Patient privacy & HIPAA/GDPR compliance
- Clinical risks of false negatives vs. false positives
- Human-in-the-loop clinical assistance paradigms
- Environmental footprint and efficient inference

Please refer to the comprehensive [06_ethics.md](06_ethics.md) report.

---

## 👥 Team Members

| Name | registration number |
| :--- | :--- | :--- |
| *Ishan Choudhary* | 25BCE10753 |
| *Khush Gupta* | 25BCE10038 |
| *Vidit Choudhary* |25BCE10749 |
| *Saransh Mathur*| 25BCE10354 |
| *Somya Bhardwaj*| 25BCE10409 |
---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
