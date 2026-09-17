import os
import sys
import pathlib
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

def main():
    print('\n' + '='*60)
    print('SECTION 1: IMPORTS & CONFIGURATION')
    print('='*60)
    
    # Set random seeds for reproducibility
    tf.random.set_seed(42)
    np.random.seed(42)
    
    # Configuration constants
    IMG_SIZE = 224
    BATCH_SIZE = 32
    EPOCHS = 10
    DATASET_DIR = 'dataset'
    
    print(f"Configuration: IMG_SIZE={IMG_SIZE}, BATCH_SIZE={BATCH_SIZE}, EPOCHS={EPOCHS}")
    print(f"Dataset Directory: {DATASET_DIR}")
    
    # Create directory for plots
    os.makedirs('plots', exist_ok=True)
    
    # Optional plot styling
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except:
        pass # Fallback to default if seaborn styles not available
    
    # Check if dataset exists before proceeding
    if not os.path.exists(DATASET_DIR):
        print(f"WARNING: Directory '{DATASET_DIR}' not found. Please place dataset in this folder.")
        print("Expected structure: dataset/TB/ and dataset/Normal/")
        return
        
    print('\n' + '='*60)
    print('SECTION 2: DATA LOADING & EXPLORATORY DATA ANALYSIS (EDA)')
    print('='*60)
    
    tb_dir = os.path.join(DATASET_DIR, 'TB')
    normal_dir = os.path.join(DATASET_DIR, 'Normal')
    
    if not os.path.exists(tb_dir) or not os.path.exists(normal_dir):
        print(f"WARNING: Subdirectories 'TB' or 'Normal' missing in {DATASET_DIR}.")
        return
        
    tb_files = [f for f in os.listdir(tb_dir) if f.lower().endswith('.png')]
    normal_files = [f for f in os.listdir(normal_dir) if f.lower().endswith('.png')]
    
    count_tb = len(tb_files)
    count_normal = len(normal_files)
    total_images = count_tb + count_normal
    
    print(f"Total Images: {total_images}")
    print(f"TB Images: {count_tb} ({(count_tb/total_images)*100:.2f}%)")
    print(f"Normal Images: {count_normal} ({(count_normal/total_images)*100:.2f}%)")
    
    # 2.1 Bar chart of class distribution
    plt.figure(figsize=(8, 6))
    plt.bar(['Normal (0)', 'TB (1)'], [count_normal, count_tb], color=['green', 'red'])
    plt.title('Class Distribution')
    plt.ylabel('Number of Images')
    plt.savefig('plots/class_distribution.png')
    plt.close()
    print("Saved plots/class_distribution.png")
    
    # 2.2 Sample images grid (5 TB + 5 Normal)
    try:
        fig, axes = plt.subplots(2, 5, figsize=(15, 6))
        for i in range(5):
            if i < len(tb_files):
                img_path = os.path.join(tb_dir, tb_files[i])
                img = tf.keras.utils.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
                axes[0, i].imshow(img)
                axes[0, i].set_title('TB')
                axes[0, i].axis('off')
            
            if i < len(normal_files):
                img_path = os.path.join(normal_dir, normal_files[i])
                img = tf.keras.utils.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
                axes[1, i].imshow(img)
                axes[1, i].set_title('Normal')
                axes[1, i].axis('off')
        
        plt.tight_layout()
        plt.savefig('plots/sample_images.png')
        plt.close()
        print("Saved plots/sample_images.png")
    except Exception as e:
        print(f"Could not load sample images: {e}")
        
    # 2.3 Pixel intensity histograms
    try:
        tb_sample = np.random.choice(tb_files, min(50, len(tb_files)), replace=False)
        normal_sample = np.random.choice(normal_files, min(50, len(normal_files)), replace=False)
        
        tb_pixels = []
        normal_pixels = []
        
        for f in tb_sample:
            img = tf.keras.utils.load_img(os.path.join(tb_dir, f), color_mode='grayscale')
            tb_pixels.extend(tf.keras.utils.img_to_array(img).flatten())
            
        for f in normal_sample:
            img = tf.keras.utils.load_img(os.path.join(normal_dir, f), color_mode='grayscale')
            normal_pixels.extend(tf.keras.utils.img_to_array(img).flatten())
            
        plt.figure(figsize=(10, 5))
        plt.hist(normal_pixels, bins=50, alpha=0.5, color='green', label='Normal', density=True)
        plt.hist(tb_pixels, bins=50, alpha=0.5, color='red', label='TB', density=True)
        plt.title('Pixel Intensity Distribution (Grayscale)')
        plt.xlabel('Pixel Value (0-255)')
        plt.ylabel('Density')
        plt.legend()
        plt.savefig('plots/pixel_distribution.png')
        plt.close()
        print("Saved plots/pixel_distribution.png")
    except Exception as e:
        print(f"Could not process pixel distribution: {e}")

    print('\n' + '='*60)
    print('SECTION 3: DATA PREPROCESSING & AUGMENTATION')
    print('='*60)
    
    # Load full dataset
    full_dataset = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        label_mode='binary',
        seed=42,
        shuffle=True
    )
    
    # Manually split
    dataset_batches = tf.data.experimental.cardinality(full_dataset).numpy()
    train_size = int(0.7 * dataset_batches)
    val_size = int(0.15 * dataset_batches)
    test_size = dataset_batches - train_size - val_size
    
    train_ds_raw = full_dataset.take(train_size)
    val_ds = full_dataset.skip(train_size).take(val_size)
    test_ds = full_dataset.skip(train_size + val_size)
    
    print(f"Splits (Batches): Train={train_size}, Validation={val_size}, Test={test_size}")
    
    # Data Augmentation Sequential Model
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip('horizontal'),
        tf.keras.layers.RandomRotation(0.2),
        tf.keras.layers.RandomZoom(0.2),
        tf.keras.layers.RandomContrast(0.2)
    ], name='data_augmentation')
    
    # Apply augmentation to training set via map
    train_ds = train_ds_raw.map(
        lambda x, y: (data_augmentation(x, training=True), y),
        num_parallel_calls=tf.data.AUTOTUNE
    )
    
    # Performance optimization
    train_ds = train_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
    test_ds = test_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
    
    # Compute Class Weights (approximated from overall counts assuming uniform distribution in shuffle)
    # Using the total counts to build class weights dictionary:
    weight_0 = total_images / (2.0 * count_normal) if count_normal > 0 else 1.0
    weight_1 = total_images / (2.0 * count_tb) if count_tb > 0 else 1.0
    class_weight_dict = {0: weight_0, 1: weight_1}
    print(f"Computed Class Weights: {class_weight_dict}")

    print('\n' + '='*60)
    print('SECTION 4: MODEL ARCHITECTURE')
    print('='*60)
    
    # Base VGG16 model
    base_model = tf.keras.applications.VGG16(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    base_model.trainable = False # Freeze VGG16
    
    # Build functional model
    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = tf.keras.layers.Rescaling(1./255)(inputs)
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    
    model = tf.keras.Model(inputs, outputs, name='TB_VGG16_Model')
    
    model.summary()

    print('\n' + '='*60)
    print('SECTION 5: COMPILE & TRAIN')
    print('='*60)
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='binary_crossentropy',
        metrics=[
            'accuracy',
            tf.keras.metrics.AUC(name='auc'),
            tf.keras.metrics.Precision(name='precision'),
            tf.keras.metrics.Recall(name='recall')
        ]
    )
    
    callbacks_list = [
        tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3)
    ]
    
    print("Starting training...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        class_weight=class_weight_dict,
        callbacks=callbacks_list
    )
    
    model.save('tb_xray_model.keras')
    print("Model saved to tb_xray_model.keras")

    print('\n' + '='*60)
    print('SECTION 6: TRAINING HISTORY PLOTS')
    print('='*60)
    
    epochs_range = range(1, len(history.history['accuracy']) + 1)
    
    # Accuracy Plot
    plt.figure()
    plt.plot(epochs_range, history.history['accuracy'], label='Training Accuracy')
    plt.plot(epochs_range, history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig('plots/training_accuracy.png')
    plt.close()
    
    # Loss Plot
    plt.figure()
    plt.plot(epochs_range, history.history['loss'], label='Training Loss')
    plt.plot(epochs_range, history.history['val_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig('plots/training_loss.png')
    plt.close()
    
    # AUC Plot
    plt.figure()
    plt.plot(epochs_range, history.history['auc'], label='Training AUC')
    plt.plot(epochs_range, history.history['val_auc'], label='Validation AUC')
    plt.title('Training and Validation AUC')
    plt.xlabel('Epochs')
    plt.ylabel('AUC')
    plt.legend()
    plt.savefig('plots/training_auc.png')
    plt.close()
    
    print("Training history plots saved to plots/")

    print('\n' + '='*60)
    print('SECTION 7: EVALUATION & METRICS')
    print('='*60)
    
    print("Evaluating on Test Set...")
    test_loss, test_acc, test_auc, test_precision, test_recall = model.evaluate(test_ds, verbose=0)
    
    # Get predictions
    y_true_list = []
    y_pred_probs_list = []
    
    misclassified_imgs = []
    misclassified_true = []
    misclassified_pred = []
    
    for x_batch, y_batch in test_ds:
        preds = model.predict(x_batch, verbose=0)
        batch_y_true = y_batch.numpy().flatten()
        batch_y_probs = preds.flatten()
        batch_y_pred = (batch_y_probs > 0.5).astype(int)
        
        y_true_list.extend(batch_y_true)
        y_pred_probs_list.extend(batch_y_probs)
        
        # Track up to 10 misclassified
        for i in range(len(batch_y_true)):
            if batch_y_true[i] != batch_y_pred[i]:
                if len(misclassified_imgs) < 10:
                    misclassified_imgs.append(x_batch[i].numpy())
                    misclassified_true.append(batch_y_true[i])
                    misclassified_pred.append(batch_y_pred[i])

    y_true = np.array(y_true_list)
    y_pred_probs = np.array(y_pred_probs_list)
    y_pred = (y_pred_probs > 0.5).astype(int)
    
    # Confusion Matrix manually
    TP = np.sum((y_pred == 1) & (y_true == 1))
    TN = np.sum((y_pred == 0) & (y_true == 0))
    FP = np.sum((y_pred == 1) & (y_true == 0))
    FN = np.sum((y_pred == 0) & (y_true == 1))
    
    cm = np.array([[TN, FP], [FN, TP]])
    
    # Plot Confusion Matrix
    fig, ax = plt.subplots(figsize=(6, 6))
    cax = ax.imshow(cm, interpolation='nearest', cmap='Blues')
    plt.title('Confusion Matrix')
    fig.colorbar(cax)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Normal (0)', 'TB (1)'])
    ax.set_yticklabels(['Normal (0)', 'TB (1)'])
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    
    # Annotate CM
    thresh = cm.max() / 2.
    for i in range(2):
        for j in range(2):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black", fontsize=14)
    plt.savefig('plots/confusion_matrix.png')
    plt.close()
    
    # Compute Classification Metrics manually (Handle division by zero)
    acc = (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # ROC Curve manually
    thresholds = np.linspace(0, 1, 100)
    tpr_list, fpr_list = [], []
    
    for t in thresholds:
        y_pred_t = (y_pred_probs >= t).astype(int)
        TP_t = np.sum((y_pred_t == 1) & (y_true == 1))
        TN_t = np.sum((y_pred_t == 0) & (y_true == 0))
        FP_t = np.sum((y_pred_t == 1) & (y_true == 0))
        FN_t = np.sum((y_pred_t == 0) & (y_true == 1))
        
        tpr_t = TP_t / (TP_t + FN_t) if (TP_t + FN_t) > 0 else 0
        fpr_t = FP_t / (FP_t + TN_t) if (FP_t + TN_t) > 0 else 0
        tpr_list.append(tpr_t)
        fpr_list.append(fpr_t)
        
    sort_idx = np.argsort(fpr_list)
    fpr_arr = np.array(fpr_list)[sort_idx]
    tpr_arr = np.array(tpr_list)[sort_idx]
    trapz_func = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
    roc_auc_score = trapz_func(tpr_arr, fpr_arr) if trapz_func else test_auc
    
    # Plot ROC Curve
    plt.figure()
    plt.plot(fpr_arr, tpr_arr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc_score:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    plt.savefig('plots/roc_curve.png')
    plt.close()
    
    # Plot misclassified images
    if misclassified_imgs:
        num_imgs = min(10, len(misclassified_imgs))
        cols = 5
        rows = int(np.ceil(num_imgs / cols))
        fig, axes = plt.subplots(rows, cols, figsize=(15, 3 * rows))
        axes = axes.flatten() if num_imgs > 1 else [axes]
        
        for i in range(num_imgs):
            # Convert back to uint8 for display purposes
            img_display = tf.cast(misclassified_imgs[i], tf.uint8).numpy()
            axes[i].imshow(img_display)
            t_label = 'TB' if misclassified_true[i] == 1 else 'Normal'
            p_label = 'TB' if misclassified_pred[i] == 1 else 'Normal'
            axes[i].set_title(f"True: {t_label}\nPred: {p_label}", color='red')
            axes[i].axis('off')
            
        for j in range(num_imgs, len(axes)):
            axes[j].axis('off')
            
        plt.tight_layout()
        plt.savefig('plots/misclassified.png')
        plt.close()
        print(f"Saved {num_imgs} misclassified images grid to plots/misclassified.png")
    
    print('\n' + '='*60)
    print('SECTION 8: FINAL SUMMARY')
    print('='*60)
    print(f"Total Test Samples: {len(y_true)}")
    print("-" * 30)
    print(f"Accuracy:    {acc:.4f}")
    print(f"Precision:   {precision:.4f}")
    print(f"Recall:      {recall:.4f}")
    print(f"Specificity: {specificity:.4f}")
    print(f"F1 Score:    {f1_score:.4f}")
    print(f"ROC AUC:     {roc_auc_score:.4f}")
    print("-" * 30)
    print("Confusion Matrix:")
    print(f"TN: {TN} | FP: {FP}")
    print(f"FN: {FN} | TP: {TP}")
    print("=" * 60)
    
    print("\nAll plots saved to plots/ directory.")
    print("Model saved to tb_xray_model.keras.")
    print("Pipeline execution complete!")

if __name__ == '__main__':
    # Force minimal GPU message logging for cleaner output
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    main()
