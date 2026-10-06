"""
Automated Tuberculosis (TB) Diagnostic Inference & Explainable AI (Grad-CAM)
Usage:
    python predict.py                                 # Diagnoses a randomly selected sample
    python predict.py --image dataset/TB/Tuberculosis-10.png  # Diagnoses a specific chest X-ray
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

def load_model_and_gradcam_extractor(model_path=MODEL_PATH):
    """Loads trained Keras model and extracts VGG16 conv graph for Grad-CAM."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_path}' not found! Run main.py or 04_train.py first.")
    
    model = tf.keras.models.load_model(model_path)
    vgg = model.get_layer('vgg16')
    last_conv_layer = vgg.get_layer('block5_conv3')
    
    # Feature extractor for block5_conv3
    conv_extractor = tf.keras.Model(vgg.input, last_conv_layer.output)
    
    # Remaining layers in VGG after block5_conv3
    post_vgg_layers = []
    found = False
    for layer in vgg.layers:
        if found:
            post_vgg_layers.append(layer)
        elif layer.name == 'block5_conv3':
            found = True
            
    # Classification head layers: GAP2D, Dense(256), Dropout, Dense(1)
    head_layers = model.layers[3:]
    
    return model, conv_extractor, post_vgg_layers, head_layers

def compute_gradcam(img_array, model, conv_extractor, post_vgg_layers, head_layers):
    """
    Computes Gradient-weighted Class Activation Mapping (Grad-CAM) heatmap.
    img_array: numpy array with shape (1, 224, 224, 3) in [0, 255]
    """
    # Apply input rescaling layer (1./255)
    rescaled_input = model.layers[1](img_array)
    
    with tf.GradientTape() as tape:
        conv_outputs = conv_extractor(rescaled_input)
        tape.watch(conv_outputs)
        
        # Pass feature maps through remaining VGG layers
        x = conv_outputs
        for layer in post_vgg_layers:
            x = layer(x)
            
        # Pass through custom classification head
        for layer in head_layers:
            x = layer(x)
            
        preds = x # Shape (1, 1)
        tb_score = preds[:, 0]
        
    # Gradients of TB class score with respect to feature maps
    grads = tape.gradient(tb_score, conv_outputs)
    
    # Global average pooling of gradients (importance weight per channel)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    
    # Weight feature map activations
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    
    # Rectified Linear Unit (ReLU) to only retain features having positive influence
    heatmap = tf.maximum(heatmap, 0.0)
    max_val = tf.math.reduce_max(heatmap)
    if max_val != 0:
        heatmap = heatmap / max_val
        
    return heatmap.numpy(), float(preds[0][0])

def predict_single(image_path, output_plot='plots/single_prediction.png'):
    if not os.path.exists(image_path):
        print(f"[ERROR] Image path '{image_path}' does not exist!")
        return

    print(f"\n[INFO] Loading deep learning model from '{MODEL_PATH}'...")
    model, conv_extractor, post_vgg_layers, head_layers = load_model_and_gradcam_extractor(MODEL_PATH)

    print(f"[INFO] Processing chest radiograph: '{image_path}'...")
    pil_img = tf.keras.utils.load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = tf.keras.utils.img_to_array(pil_img)
    img_batch = np.expand_dims(img_array, axis=0)

    # Compute prediction & Grad-CAM heatmap
    heatmap, prob = compute_gradcam(img_batch, model, conv_extractor, post_vgg_layers, head_layers)
    
    threshold = 0.50
    is_tb = prob >= threshold
    predicted_label = "Tuberculosis (TB) Detected" if is_tb else "Normal (Healthy Lungs)"
    confidence = prob if is_tb else (1.0 - prob)
    status_color = 'darkred' if is_tb else 'darkgreen'

    # Clinical triaging advice
    if is_tb:
        triage_text = "PRIORITY 1: Immediate Sputum Smear / GeneXpert confirmation recommended"
        triage_bg = '#f8d7da'
    else:
        triage_text = "PRIORITY 3: Standard routine monitoring; no active consolidation detected"
        triage_bg = '#d4edda'

    print("\n" + "=" * 65)
    print("        TUBERCULOSIS COMPUTER-AIDED DIAGNOSTIC REPORT        ")
    print("=" * 65)
    print(f" Radiograph File:   {image_path}")
    print(f" Raw Sigmoid Output: {prob:.4f}")
    print(f" Clinical Decision:  {predicted_label}")
    print(f" Diagnostic Certainty: {confidence * 100:.2f}%")
    print(f" Triage Protocol:    {triage_text}")
    print("=" * 65)

    # Generate 3-panel visualization
    os.makedirs(os.path.dirname(output_plot), exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Panel 1: Original Radiograph
    axes[0].imshow(pil_img)
    axes[0].set_title("Input Chest Radiograph", fontsize=12, fontweight='bold')
    axes[0].axis('off')

    # Panel 2: Grad-CAM Pathology Localization
    heatmap_resized = tf.image.resize(np.expand_dims(heatmap, axis=-1), (IMG_SIZE, IMG_SIZE)).numpy().squeeze()
    axes[1].imshow(pil_img)
    im = axes[1].imshow(heatmap_resized, cmap='jet', alpha=0.45)
    axes[1].set_title("Explainable AI: Grad-CAM\n(Pathological Focus Areas)", fontsize=12, fontweight='bold')
    axes[1].axis('off')
    plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04, label='Relevance Weight')

    # Panel 3: Diagnostic Probability Bar Chart
    classes = ['Normal', 'Tuberculosis']
    probabilities = [1.0 - prob, prob]
    colors = ['#2ca02c', '#d62728']
    bars = axes[2].bar(classes, probabilities, color=colors, alpha=0.85, width=0.45)
    axes[2].set_ylim([0, 1.05])
    axes[2].set_ylabel('Model Probability', fontsize=11)
    axes[2].set_title(f"Diagnosis: {predicted_label}\nConfidence: {confidence * 100:.1f}%", 
                      fontsize=12, fontweight='bold', color=status_color)
    axes[2].axhline(y=threshold, color='gray', linestyle='--', label=f'Triage Threshold ({threshold:.2f})')
    axes[2].legend(loc='upper right')

    for bar, p in zip(bars, probabilities):
        yval = bar.get_height()
        axes[2].text(bar.get_x() + bar.get_width() / 2.0, yval + 0.02, f"{p * 100:.1f}%", 
                     ha='center', va='bottom', fontweight='bold', fontsize=11)

    fig.text(0.5, 0.02, f"Clinical Triage Advisory: {triage_text}", 
             ha='center', fontsize=11, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=triage_bg, edgecolor=status_color))

    plt.tight_layout(rect=[0, 0.06, 1, 1])
    plt.savefig(output_plot, dpi=160)
    plt.close()
    print(f"\n[INFO] Comprehensive diagnostic figure saved to: '{output_plot}'")

if __name__ == '__main__':
    target_path = None

    if len(sys.argv) > 1:
        if sys.argv[1] == '--image' and len(sys.argv) > 2:
            target_path = sys.argv[2]
        else:
            target_path = sys.argv[1]

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
