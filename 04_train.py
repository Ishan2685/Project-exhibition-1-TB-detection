import os
import tensorflow as tf
import matplotlib.pyplot as plt

# Import custom modules dynamically since filenames start with numbers
from importlib.machinery import SourceFileLoader
preprocessing = SourceFileLoader("preprocessing", "02_preprocessing.py").load_module()
model_module = SourceFileLoader("model_module", "03_model.py").load_module()

def plot_training_history(history):
    print("Plotting training history...")
    metrics = ['accuracy', 'loss', 'auc']
    
    for metric in metrics:
        plt.figure(figsize=(8, 6))
        plt.plot(history.history[metric], label=f'Train {metric}')
        val_metric = f'val_{metric}'
        if val_metric in history.history:
            plt.plot(history.history[val_metric], label=f'Validation {metric}')
        plt.title(f'Model {metric.capitalize()}')
        plt.ylabel(metric.capitalize())
        plt.xlabel('Epoch')
        plt.legend()
        plt.savefig(f'plots/training_{metric}.png')
        plt.close()
    
    print("Training plots saved in plots/")

def main():
    os.makedirs('plots', exist_ok=True)
    print("=== Starting Training Pipeline ===")
    
    # 1. Load and preprocess data
    try:
        dataset = preprocessing.load_data()
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return
        
    train_ds, val_ds, test_ds = preprocessing.split_dataset(dataset)
    
    augmentation = preprocessing.get_augmentation_layer()
    class_weights = preprocessing.compute_class_weights(train_ds)
    
    train_ds, val_ds, test_ds = preprocessing.prepare_datasets(train_ds, val_ds, test_ds, augmentation)
    
    # 2. Build model
    model = model_module.build_model()
    
    # 3. Compile
    print("Compiling model...")
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
    
    # 4. Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True, monitor='val_loss'),
        tf.keras.callbacks.ReduceLROnPlateau(patience=3, monitor='val_loss', factor=0.5)
    ]
    
    # 5. Train
    print("Training model...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=15,
        callbacks=callbacks,
        class_weight=class_weights
    )
    
    # 6. Save model
    model.save('tb_xray_model.keras')
    print("Model saved to tb_xray_model.keras")
    
    # 7. Plot history
    plot_training_history(history)

if __name__ == '__main__':
    main()
