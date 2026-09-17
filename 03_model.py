import tensorflow as tf

def build_model(img_size=224):
    print("Building model architecture...")
    
    # Load VGG16 base model
    base_model = tf.keras.applications.VGG16(
        weights='imagenet',
        include_top=False,
        input_shape=(img_size, img_size, 3)
    )
    
    # Freeze the base model
    base_model.trainable = False
    
    # Define inputs
    inputs = tf.keras.Input(shape=(img_size, img_size, 3))
    
    # Note: If rescaling is done in the dataset mapping, we don't necessarily need it here, 
    # but the instruction said "inputs -> Rescaling(1./255) -> VGG16"
    # To be safe and follow instructions strictly, we add it here as well. 
    # If the user feeds pre-rescaled images, this might divide by 255 again.
    # To match standard conventions when given this prompt, we add it to the model.
    # (Removed from prep script and kept here or vice-versa, prompt says to do both, 
    # I'll just follow the prompt exactly: inputs -> Rescaling -> VGG16)
    x = tf.keras.layers.Rescaling(1./255)(inputs)
    
    # Pass to base model
    x = base_model(x, training=False)
    
    # Custom head
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    
    # Create model
    model = tf.keras.Model(inputs, outputs)
    
    return model

if __name__ == '__main__':
    model = build_model()
    model.summary()
