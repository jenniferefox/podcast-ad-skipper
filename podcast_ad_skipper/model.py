import matplotlib.pyplot as plt
from keras.applications import VGG16
from keras import layers, models, Model
from keras.optimizers import Adam
import tensorflow as tf

def build_baseline_model(input_shape=(224,224,3), freeze_base=True):
    base_model = tf.keras.applications.VGG16(
        include_top=False,
        input_shape=input_shape,
        weights=None)
    base_model.trainable = freeze_base
    x = base_model.output

    #flatten
    x = layers.Flatten()(x)

    #dense layer for ad detection
    x = layers.Dense(512, activation='relu')(x)
    x = layers.Dropout(0.5)(x)

    #output layer for ad detection
    output = layers.Dense(1, activation='sigmoid')(x)
    loss = 'binary_crossentropy'

    #create
    model = models.Model(
        inputs=base_model.input,
        outputs=output
    )

    #compile
    model.compile(
        loss=loss,
        optimizer='adam',
        metrics=['accuracy']
    )
    return model

def plot_history(history):
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    accuracy = history.history['accuracy']
    val_accuracy = history.history['val_accuracy']
    epochs = range(1, len(loss) + 1)

    plt.figure(figsize=(12,5))

    #loss plot
    plt.subplot(1, 2, 1)
    plt.plot(epochs, loss, 'bo-', label='Training Loss')
    plt.plot(epochs, val_loss, 'ro-', label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    # accuracy plot
    plt.subplot(1, 2, 2)
    plt.plot(epochs, accuracy, 'bo-', label='Training Accuracy')
    plt.plot(epochs, val_accuracy, 'ro-', label='Valisation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.show()
