import tensorflow as tf

def load_data(data_dir='dataset/', img_size=224, batch_size=32):
    print(f"Loading data from {data_dir}...")
    dataset = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        labels='inferred',
        label_mode='binary',
        class_names=['Normal', 'TB'],
        color_mode='rgb',
        batch_size=batch_size,
        image_size=(img_size, img_size),
        shuffle=True,
        seed=42
    )
    return dataset

def split_dataset(dataset, train_ratio=0.7, val_ratio=0.15):
    print("Splitting dataset...")
    dataset_size = len(dataset)
    
    train_size = int(train_ratio * dataset_size)
    val_size = int(val_ratio * dataset_size)
    
    train_ds = dataset.take(train_size)
    remaining_ds = dataset.skip(train_size)
    
    val_ds = remaining_ds.take(val_size)
    test_ds = remaining_ds.skip(val_size)
    
    return train_ds, val_ds, test_ds

def get_augmentation_layer():
    print("Creating augmentation layer...")
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.2),
        tf.keras.layers.RandomZoom(0.2),
        tf.keras.layers.RandomContrast(0.2)
    ])
    return data_augmentation

def compute_class_weights(train_ds):
    print("Computing class weights...")
    total_images = 0
    pos_count = 0  # Assuming 1 is TB based on class_names=['Normal', 'TB']
    neg_count = 0  # Assuming 0 is Normal
    
    for images, labels in train_ds:
        pos = tf.math.reduce_sum(labels).numpy()
        total = len(labels)
        pos_count += pos
        neg_count += (total - pos)
        total_images += total
        
    if total_images == 0:
        return {0: 1.0, 1: 1.0}
        
    weight_for_0 = (1 / neg_count) * (total_images / 2.0) if neg_count > 0 else 1.0
    weight_for_1 = (1 / pos_count) * (total_images / 2.0) if pos_count > 0 else 1.0
    
    class_weight = {0: weight_for_0, 1: weight_for_1}
    print(f"Class weights: {class_weight}")
    return class_weight

def prepare_datasets(train_ds, val_ds, test_ds, augmentation):
    print("Preparing datasets for training...")
    AUTOTUNE = tf.data.AUTOTUNE
    
    # Train dataset gets augmentation
    train_ds = train_ds.map(lambda x, y: (augmentation(x, training=True), y), num_parallel_calls=AUTOTUNE)
    
    # Optimization (Rescaling is handled inside the model architecture in 03_model.py)
    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    test_ds = test_ds.cache().prefetch(buffer_size=AUTOTUNE)
    
    return train_ds, val_ds, test_ds

if __name__ == '__main__':
    try:
        ds = load_data()
        train, val, test = split_dataset(ds)
        print(f"Train batches: {len(train)}")
        print(f"Val batches: {len(val)}")
        print(f"Test batches: {len(test)}")
        aug = get_augmentation_layer()
        cw = compute_class_weights(train)
        train_p, val_p, test_p = prepare_datasets(train, val, test, aug)
        print("Preprocessing demo successful.")
    except Exception as e:
        print(f"Error during demo (usually happens if dataset is missing): {e}")
