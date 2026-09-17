"""
Single-Image Prediction Script for Tuberculosis (TB) Detection
Usage:
    python predict.py                     # Picks a random sample from dataset to predict
    python predict.py --image <path>       # Predicts on a specific X-ray image file
"""

import sys
import os
import glob
import random
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

MODEL_PATH = 'tb_xray_model.keras'
IMG_SIZE = 224

def load_and_preprocess_image(image_path):
    """Loads image and converts to tensor (shape: 1, 224, 224, 3)"""
    img = tf.keras.utils.load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = tf.keras.utils.img_to_array(img)
    img_batch = np.expand_dims(img_array, axis=0)
    return img, img_batch

def predict_single(image_path):
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Trained model file '{MODEL_PATH}' not found!")
        print("Please ensure you have run main.py or 04_train.py first.")
        return

    if not os.path.exists(image_path):
        print(f"[ERROR] Image path '{image_path}' does not exist!")
        return

    print(f"\n[INFO] Loading model from '{MODEL_PATH}'...")
    model = tf.keras.models.load_model(MODEL_PATH)

    print(f"[INFO] Processing image: '{image_path}'...")
    pil_img, img_batch = load_and_preprocess_image(image_path)

    # Predict
    prob = float(model.predict(img_batch, verbose=0)[0][0])
    threshold = 0.5
    predicted_label = "Tuberculosis (TB)" if prob >= threshold else "Normal (Healthy)"
    confidence = prob if prob >= threshold else (1.0 - prob)

    print("\n" + "=" * 55)
    print("        TUBERCULOSIS DETECTION INFERENCE RESULT        ")
    print("=" * 55)
    print(f" Image Path:       {image_path}")
    print(f" Raw Sigmoid Prob: {prob:.4f}")
    print(f" Prediction:       {predicted_label}")
    print(f" Confidence:       {confidence * 100:.2f}%")
    print("=" * 55)

    # Generate a visual plot
    os.makedirs('plots', exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.5), gridspec_kw={'width_ratios': [1.2, 1]})

    # Left: X-ray Display
    ax[0].imshow(pil_img)
    ax[0].set_title(f"Predicted: {predicted_label}\nConfidence: {confidence * 100:.1f}%", 
                    fontsize=12, fontweight='bold',
                    color='darkred' if 'TB' in predicted_label else 'darkgreen')
    ax[0].axis('off')

    # Right: Probability Bar Chart
    classes = ['Normal', 'Tuberculosis']
    probabilities = [1.0 - prob, prob]
    colors = ['green', 'red']
    bars = ax[1].bar(classes, probabilities, color=colors, alpha=0.75, width=0.5)
    ax[1].set_ylim([0, 1.05])
    ax[1].set_ylabel('Model Probability', fontsize=11)
    ax[1].set_title('Diagnostic Confidence Breakdown', fontsize=12)
    ax[1].axhline(y=0.5, color='gray', linestyle='--', label='Threshold (0.5)')
    ax[1].legend(loc='upper right')

    for bar, p in zip(bars, probabilities):
        yval = bar.get_height()
        ax[1].text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"{p*100:.1f}%", 
                   ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    output_plot = 'plots/single_prediction.png'
    plt.savefig(output_plot, dpi=150)
    plt.close()
    print(f"\n[INFO] Diagnostic figure saved to '{output_plot}'")

if __name__ == '__main__':
    target_path = None

    if len(sys.argv) > 1:
        if sys.argv[1] == '--image' and len(sys.argv) > 2:
            target_path = sys.argv[2]
        else:
            target_path = sys.argv[1]

    # If no image specified, pick a random TB or Normal sample from dataset
    if target_path is None:
        tb_files = glob.glob('dataset/TB/*.png')
        normal_files = glob.glob('dataset/Normal/*.png')
        all_files = tb_files + normal_files
        if all_files:
            target_path = random.choice(all_files)
            print(f"[DEMO MODE] No image specified. Randomly selected sample: {target_path}")
        else:
            print("[ERROR] No images found in dataset/ folder.")
            sys.exit(1)

    predict_single(target_path)
