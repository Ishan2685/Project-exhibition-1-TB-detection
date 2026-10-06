# Final Presentation & 5-Person Team Coordination Guide (Review 3)

This guide provides the exact slide layout for your PPT and the coordinated 5-person speaking script to score full marks (**5/5**) for **Final Presentation & Team Coordination** in Review 3.

---

## 📑 Slide Structure for Your PPT (10–12 Slides)

| Slide # | Slide Title | Key Content & Bullet Points | File / Visual to Embed | Presenter |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **Title Slide** | Project Title: Computer-Aided Tuberculosis Detection using Transfer Learning & Explainable AI<br>Team Members (S1–S5), Department, Institution | College Logo, Clean Title | **Person 1** |
| **2** | **Clinical Problem Statement** | • 1.3M deaths/year from TB (WHO).<br>• Radiologist shortage in rural health centers.<br>• Objective: Fast, accessible automated triaging. | WHO Statistics Graphic | **Person 1** |
| **3** | **Dataset & 5:1 Imbalance** | • 4,200 Kaggle CXR images (3,500 Normal, 700 TB).<br>• The 5:1 severe imbalance problem.<br>• Why accuracy alone is deceptive. | `plots/class_distribution.png`<br>`plots/sample_images.png` | **Person 1** |
| **4** | **Data Preprocessing & Augmentation** | • 70/15/15 Stratified Partition (2940 / 630 / 630).<br>• Targeted Augmentation (Flip, Rotation, Zoom, Contrast).<br>• Zero contamination: Test set kept 100% pristine. | Preprocessing Pipeline Diagram | **Person 2** |
| **5** | **Inverse Class Weighting Math** | • Math formula: $w_c = N_{\text{total}} / (2 \times N_c)$.<br>• Weights: Normal $\approx 0.6$, TB $\approx 3.0$.<br>• Penalizes missed TB cases 5x more heavily. | Math Formula & Weight Bar | **Person 2** |
| **6** | **Model Architecture & Transfer Learning** | • Pre-trained VGG16 backbone (Frozen weights).<br>• GlobalAveragePooling2D (reduces params from 6.4M to 131k).<br>• Dense(256) + Dropout(0.5) + Sigmoid(1). | Architecture Diagram | **Person 3** |
| **7** | **Training Dynamics & Callbacks** | • Adam optimizer (lr = 1e-4), 10 epochs.<br>• EarlyStopping & ReduceLROnPlateau.<br>• Loss dropped to 0.3665, AUC climbed to 95.62%. | `plots/training_loss.png`<br>`plots/training_auc.png` | **Person 3** |
| **8** | **Explainable AI with Grad-CAM** | • The "Black Box" problem in medical AI.<br>• Grad-CAM: gradients of class score wrt feature maps.<br>• Heatmaps verify pathological lung lesions. | `plots/gradcam_tb_demo.png` | **Person 3** |
| **9** | **Evaluation & Pure NumPy Metrics** | • Zero scikit-learn / pandas dependency.<br>• Test Accuracy: 85.5% \| Sensitivity (Recall): 89.9%.<br>• Specificity: 85.2% \| ROC-AUC: 95.12%. | `plots/confusion_matrix.png`<br>`plots/roc_curve.png` | **Person 4** |
| **10** | **Clinical Triage & Error Analysis** | • 648 Test Cases: 471 TN, 83 TP, 82 FP, 12 FN.<br>• Why Recall > Precision in screening.<br>• NPV of 97.8% (high confidence on Normal). | Confusion Matrix Table | **Person 4** |
| **11** | **Live System Demo (CLI & Desktop GUI)** | • Real-time inference in <1.2 seconds.<br>• Demo CLI: `python predict.py`<br>• Demo GUI: `python app_gui.py` | Live Demo on Laptop Screen | **Person 5** |
| **12** | **Ethics, Conclusion & Future Scope** | • HIPAA/GDPR metadata de-identification.<br>• Green AI: low power, CPU-friendly inference.<br>• Future: multi-disease detection & edge deployment. | Summary Diagram | **Person 5** |

---

## 🗣️ 5-Person Speaking Script & Team Coordination

### 👤 Person 1 (S1): Problem Definition & Exploratory Data Analysis
- **Speaking Time:** ~2 minutes
- **What to Say:**
  > *"Good morning respected evaluators and professor. Today our team presents our Computer-Aided Diagnostic and Triaging System for Pulmonary Tuberculosis Detection using Chest X-rays.  
  > Tuberculosis is one of the world's deadliest infectious killers, causing 1.3 million deaths each year. While chest X-rays are cheap and widely available, rural hospitals suffer from a severe shortage of expert radiologists to interpret them.  
  > We utilized a benchmark dataset of 4,200 chest X-rays. However, we faced a major challenge: a 5:1 severe class imbalance—3,500 healthy lungs and only 700 TB cases. If a naive model simply guessed 'Normal' every time, it would get 83% accuracy but 0% recall, missing every single infected patient. Now, Person 2 will explain how we engineered our data pipeline to solve this imbalance."*
- **Handoff:** *"Over to Person 2."*

### 👤 Person 2 (S2): Preprocessing, Augmentation & Class Weighting Math
- **Speaking Time:** ~2 minutes
- **What to Say:**
  > *"Thank you. To prepare the data without bias, we performed a stratified 70/15/15 split—2,940 training images, 630 validation images, and 630 held-out test images.  
  > To expand the minority TB class without altering lung anatomy, we applied targeted data augmentation: horizontal flips, small rotations of up to 20 degrees, subtle zooming, and contrast adjustments to simulate different X-ray machines.  
  > Most importantly, we mathematically derived inverse class weights: Total Samples divided by (2 times Class Samples). This gave a weight of 0.6 for Normal and 3.0 for TB. This penalized our loss function 5 times more whenever the network missed a TB patient. Now, Person 3 will discuss the deep learning model architecture and Explainable AI."*
- **Handoff:** *"Over to Person 3."*

### 👤 Person 3 (S3): Deep Learning Architecture, Training & Grad-CAM
- **Speaking Time:** ~2 minutes
- **What to Say:**
  > *"Thank you. Training a deep neural network from scratch on medical data causes severe overfitting. Therefore, we used Transfer Learning with VGG16 pre-trained on ImageNet.  
  > We froze all 14.7 million parameters of the VGG16 base so its pre-trained visual edge and texture detectors remained intact. Instead of a traditional Flatten layer which would create over 6.4 million weights, we used GlobalAveragePooling2D, reducing trainable weights to just 131,585 in our custom classification head.  
  > We trained using Adam with an initial learning rate of 1e-4 and dynamic learning rate decay. Validation loss dropped smoothly to 0.3665 while validation AUC reached 95.62%.  
  > Furthermore, to solve the 'black box' problem in medical AI, we implemented Grad-CAM—Gradient-weighted Class Activation Mapping. Grad-CAM computes gradients at the final convolutional layer to generate a transparent heatmap over the X-ray, visually proving to doctors that the model focuses on actual pathological lung lesions. Now, Person 4 will present our evaluation results."*
- **Handoff:** *"Over to Person 4."*

### 👤 Person 4 (S4): Pure NumPy Evaluation & Clinical Triage Analysis
- **Speaking Time:** ~2 minutes
- **What to Say:**
  > *"Thank you. A key technical highlight of our project is that we adhered strictly to pure NumPy without using scikit-learn or pandas. All metric formulas—Confusion Matrix, Sensitivity, Specificity, and Trapezoidal ROC-AUC—were coded mathematically from scratch.  
  > On our held-out test set of 648 unseen patient radiographs, our model achieved:  
  > • An outstanding ROC-AUC of 95.12%  
  > • A Sensitivity (Recall) of 89.90%—catching 9 out of every 10 active TB cases  
  > • A Specificity of 85.20%—correctly clearing healthy individuals  
  > • Overall Accuracy of 85.50%  
  > • Negative Predictive Value of 97.8%  
  > In medical screening, Recall is far more critical than Precision. A False Positive simply leads to a quick secondary sputum test, whereas a False Negative sends an infectious patient home untreated. Our model prioritizes catching the disease. Now, Person 5 will give a live demonstration and conclude."*
- **Handoff:** *"Over to Person 5."*

### 👤 Person 5 (S5): Live Demonstration, AI Ethics & Future Scope
- **Speaking Time:** ~2 minutes
- **What to Say:**
  > *"Thank you. To demonstrate our system in real time, we built two deployment interfaces: a command-line tool `predict.py` and a zero-dependency desktop application `app_gui.py`.  
  > [Run `python app_gui.py` or `python predict.py`]  
  > As you can see on screen, inference completes in less than 1.2 seconds on standard CPU hardware. The system displays the original X-ray, the Grad-CAM heatmap highlighting pathological focus areas, the probability breakdown, and an automated clinical triage priority recommendation.  
  > Regarding ethics and privacy, all images follow HIPAA and GDPR guidelines with DICOM metadata stripped. The system is designed as a triage assistant—not to replace doctors, but to prioritize urgent cases.  
  > In future scope, we plan to expand this into multi-disease classification (Pneumonia, COVID-19, and TB) and deploy 8-bit quantized models onto edge devices like Raspberry Pi for mobile X-ray vans. Thank you, and we are now open for questions."*

---

## 🎯 Likely Viva Questions & Coordinated Answers

| Question | Best Responder | The Exact Answer to Give |
| :--- | :---: | :--- |
| **"Why is class imbalance such a problem here?"** | **Person 1** | *"Sir, with an 83% to 17% split, a naive model guessing Normal 100% of the time gets 83.3% accuracy but 0% recall on TB. In healthcare, missing positive cases is fatal. That is why we used inverse class weighting and optimized for Recall and ROC-AUC rather than accuracy alone."* |
| **"Why did you use data augmentation only on the training set?"** | **Person 2** | *"Sir, validation and test sets must strictly represent real-world, unmanipulated patient data to provide an unbiased evaluation of how the model performs in clinical practice."* |
| **"Why did you freeze VGG16 instead of training end-to-end?"** | **Person 3** | *"Sir, medical datasets are relatively small (4,200 images). Training 15 million weights from scratch causes severe overfitting. Freezing VGG16 preserves ImageNet low-level feature extractors and lets us train only 131k weights stably."* |
| **"Why is your precision (~54%) lower than your recall (~90%)?"** | **Person 4** | *"Sir, in medical screening, we intentionally tuned our decision threshold and class weights to favor sensitivity over precision. It is clinically safer to have a False Positive (which triggers a harmless sputum test) than a False Negative (which lets an infected patient walk away)."* |
| **"Can this system replace a radiologist in a hospital today?"** | **Person 5** | *"No, sir. Under FDA CADe/CADt regulations, AI systems must function as triage aids with a human-in-the-loop. Our system prioritizes suspicious scans to the top of the radiologist's queue, cutting diagnostic wait times from days to minutes."* |
