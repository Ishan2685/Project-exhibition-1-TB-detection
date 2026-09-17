import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def load_img(path, color_mode='rgb', target_size=(224, 224)):
    img = Image.open(path)
    if color_mode == 'grayscale':
        img = img.convert('L')
    else:
        img = img.convert('RGB')
    if target_size:
        img = img.resize(target_size)
    return img

def main():
    dataset_path = 'dataset/'
    tb_path = os.path.join(dataset_path, 'TB')
    normal_path = os.path.join(dataset_path, 'Normal')
    
    os.makedirs('plots', exist_ok=True)
    
    print("=== Exploratory Data Analysis ===")
    if not os.path.exists(dataset_path):
        print(f"Warning: Dataset path '{dataset_path}' not found. Please ensure the data exists.")
        return

    # Count images
    tb_images = [f for f in os.listdir(tb_path) if os.path.isfile(os.path.join(tb_path, f))] if os.path.exists(tb_path) else []
    normal_images = [f for f in os.listdir(normal_path) if os.path.isfile(os.path.join(normal_path, f))] if os.path.exists(normal_path) else []
    
    num_tb = len(tb_images)
    num_normal = len(normal_images)
    
    print(f"Total TB images: {num_tb}")
    print(f"Total Normal images: {num_normal}")
    print(f"Total images: {num_tb + num_normal}")
    
    # Class distribution plot
    classes = ['TB', 'Normal']
    counts = [num_tb, num_normal]
    
    plt.figure(figsize=(8, 6))
    plt.bar(classes, counts, color=['red', 'blue'])
    plt.title('Class Distribution')
    plt.ylabel('Number of Images')
    plt.savefig('plots/class_distribution.png')
    plt.close()
    
    # Sample images
    if num_tb >= 5 and num_normal >= 5:
        plt.figure(figsize=(15, 6))
        for i in range(5):
            # TB
            img_path = os.path.join(tb_path, tb_images[i])
            img = load_img(img_path, target_size=(224, 224))
            plt.subplot(2, 5, i + 1)
            plt.imshow(img)
            plt.title('TB')
            plt.axis('off')
            
            # Normal
            img_path = os.path.join(normal_path, normal_images[i])
            img = load_img(img_path, target_size=(224, 224))
            plt.subplot(2, 5, i + 6)
            plt.imshow(img)
            plt.title('Normal')
            plt.axis('off')
            
        plt.tight_layout()
        plt.savefig('plots/sample_images.png')
        plt.close()
        
    # Pixel intensity histograms
    print("Calculating pixel intensity distributions...")
    tb_pixels = []
    normal_pixels = []
    
    sample_size = min(50, num_tb, num_normal)
    if sample_size > 0:
        for i in range(sample_size):
            img_tb = load_img(os.path.join(tb_path, tb_images[i]), color_mode='grayscale', target_size=(224, 224))
            tb_pixels.extend(np.array(img_tb).flatten())
            
            img_normal = load_img(os.path.join(normal_path, normal_images[i]), color_mode='grayscale', target_size=(224, 224))
            normal_pixels.extend(np.array(img_normal).flatten())
            
        plt.figure(figsize=(12, 5))
        plt.hist(tb_pixels, bins=50, alpha=0.5, color='red', label='TB', density=True)
        plt.hist(normal_pixels, bins=50, alpha=0.5, color='blue', label='Normal', density=True)
        plt.title('Pixel Intensity Distribution')
        plt.xlabel('Pixel Intensity')
        plt.ylabel('Frequency')
        plt.legend()
        plt.savefig('plots/pixel_distribution.png')
        plt.close()
        
    print("EDA complete. Plots saved to 'plots/' directory.")

if __name__ == '__main__':
    main()
