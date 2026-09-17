import os
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

from importlib.machinery import SourceFileLoader
preprocessing = SourceFileLoader("preprocessing", "02_preprocessing.py").load_module()

def plot_confusion_matrix(tp, tn, fp, fn):
    cm = np.array([[tn, fp], [fn, tp]])
    fig, ax = plt.subplots(figsize=(6, 6))
    cax = ax.matshow(cm, cmap=plt.cm.Blues)
    plt.colorbar(cax)
    
    for (i, j), z in np.ndenumerate(cm):
        ax.text(j, i, f'{z}', ha='center', va='center', fontsize=14)
        
    plt.xticks([0, 1], ['Normal (0)', 'TB (1)'])
    plt.yticks([0, 1], ['Normal (0)', 'TB (1)'])
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.savefig('plots/confusion_matrix.png')
    plt.close()

def plot_roc_curve(y_true, y_pred_prob):
    thresholds = np.linspace(0, 1, 100)
    tpr_list = []
    fpr_list = []
    
    for thresh in thresholds:
        preds = (y_pred_prob >= thresh).astype(int)
        tp = np.sum((y_true == 1) & (preds == 1))
        tn = np.sum((y_true == 0) & (preds == 0))
        fp = np.sum((y_true == 0) & (preds == 1))
        fn = np.sum((y_true == 1) & (preds == 0))
        
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        tpr_list.append(tpr)
        fpr_list.append(fpr)
        
    tpr_list = np.array(tpr_list)[np.argsort(fpr_list)]
    fpr_list = np.sort(fpr_list)
    
    trapz_fn = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
    auc = trapz_fn(tpr_list, fpr_list) if trapz_fn is not None else 0.5
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr_list, tpr_list, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC)')
    plt.legend(loc="lower right")
    plt.savefig('plots/roc_curve.png')
    plt.close()

def plot_misclassified(images, labels, preds):
    if not images:
        print("No misclassified images to plot.")
        return
        
    n = min(len(images), 10)
    cols = 5
    rows = (n + cols - 1) // cols
    
    plt.figure(figsize=(15, 3 * rows))
    for i in range(n):
        plt.subplot(rows, cols, i + 1)
        img = images[i]
        if np.max(img) <= 1.0:
            img = img * 255.0
        plt.imshow(img.astype('uint8'))
        
        true_str = 'TB' if labels[i] == 1 else 'Normal'
        pred_str = 'TB' if preds[i] > 0.5 else 'Normal'
        
        plt.title(f"T:{true_str} | P:{pred_str}\nProb: {preds[i]:.2f}")
        plt.axis('off')
        
    plt.tight_layout()
    plt.savefig('plots/misclassified.png')
    plt.close()

def main():
    os.makedirs('plots', exist_ok=True)
    print("=== Starting Evaluation ===")
    
    model_path = 'tb_xray_model.keras'
    if not os.path.exists(model_path):
        print(f"Model file '{model_path}' not found. Please train the model first.")
        return
        
    print("Loading model...")
    model = tf.keras.models.load_model(model_path)
    
    try:
        print("Loading dataset...")
        dataset = preprocessing.load_data()
        _, _, test_ds_raw = preprocessing.split_dataset(dataset)
        
        test_ds = test_ds_raw.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return

    print("Generating predictions...")
    y_true = []
    y_pred_prob = []
    
    misclassified_images = []
    misclassified_labels = []
    misclassified_preds = []
    
    for images, labels in test_ds:
        preds = model.predict(images, verbose=0)
        y_true.extend(labels.numpy().flatten())
        y_pred_prob.extend(preds.flatten())
        
        for i in range(len(labels)):
            true_label = int(labels[i].numpy()[0]) if len(labels[i].shape) > 0 else int(labels[i].numpy())
            pred_prob = preds[i][0]
            pred_label = 1 if pred_prob > 0.5 else 0
            
            if true_label != pred_label and len(misclassified_images) < 10:
                misclassified_images.append(images[i].numpy())
                misclassified_labels.append(true_label)
                misclassified_preds.append(pred_prob)
                
    y_true = np.array(y_true)
    y_pred_prob = np.array(y_pred_prob)
    y_pred_class = (y_pred_prob > 0.5).astype(int)
    
    # Compute Confusion Matrix with numpy
    tp = np.sum((y_true == 1) & (y_pred_class == 1))
    tn = np.sum((y_true == 0) & (y_pred_class == 0))
    fp = np.sum((y_true == 0) & (y_pred_class == 1))
    fn = np.sum((y_true == 1) & (y_pred_class == 0))
    
    plot_confusion_matrix(tp, tn, fp, fn)
    
    # Compute Metrics
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    plot_roc_curve(y_true, y_pred_prob)
    plot_misclassified(misclassified_images, misclassified_labels, misclassified_preds)
    
    print("\n=== Final Summary ===")
    print(f"Accuracy:    {accuracy:.4f}")
    print(f"Precision:   {precision:.4f}")
    print(f"Recall:      {recall:.4f}")
    print(f"Specificity: {specificity:.4f}")
    print(f"F1-Score:    {f1_score:.4f}")
    print("\nEvaluation plots saved to 'plots/' directory.")

if __name__ == '__main__':
    main()
