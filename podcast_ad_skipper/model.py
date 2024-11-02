import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras import Model, Sequential, layers, regularizers, optimizers, applications, models
from podcast_ad_skipper.params import *
from podcast_ad_skipper.google_cloud import *

INPUT_SHAPE = (128, 216, 1)

def build_baseline_model(input_shape=(128,216,1)):
    model = tf.keras.models.Sequential([
    # Input layer - note that Input() doesn't take an activation
    tf.keras.layers.Input(shape=input_shape),

    # Conv2D layer
    tf.keras.layers.Conv2D(32, 3, strides=2, padding='same', activation='relu'),

    # Flatten layer
    tf.keras.layers.Flatten(),

    # Dense layers
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

    # Compile model
    model.compile(
        loss='binary_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )

    return model



def fit_model(model, X_train, y_train, X_test, y_test):

    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    history = model.fit(
    X_train,
    y_train,
    batch_size=16,
    epochs=50,
    validation_data=(X_test,y_test),
    callbacks=[early_stopping,])
    return model, history


def build_trained_model(X_train, y_train, X_test, y_test):
    model = build_baseline_model(input_shape=INPUT_SHAPE)
    latest_trained_model, history = fit_model(model, X_train, y_train, X_test, y_test)
    gcs_uri = f"gs://{BUCKET_NAME_MODEL}/{latest_trained_model}"
    # Save the model directly to GCS

    models.save_model(latest_trained_model, gcs_uri)
    return latest_trained_model, history


def download_model_from_gcs(gcs_uri):
    client = auth_gc_storage()
    blobs = list(client.get_bucket(BUCKET_NAME_MODEL).list_blobs())

    try:
        latest_trained_model = models.load_model(gcs_uri)
        print("✅ Latest model downloaded from cloud storage")
        return latest_trained_model

    except:
        print(f"\n❌ No model found in GCS bucket {BUCKET_NAME}")
        return None

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

def evaluate_model(model, X_test, y_test):
    final_loss, final_acc = model.evaluate(X_test, y_test, verbose=0)
    print("Final loss: {0:.6f}, final accuracy: {1:.6f}".format(final_loss, final_acc))
    return final_loss, final_acc
