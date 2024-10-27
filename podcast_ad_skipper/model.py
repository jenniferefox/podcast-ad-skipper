import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras import Model, Sequential, layers, regularizers, optimizers, applications, models
from podcast_ad_skipper.params import *
from podcast_ad_skipper.google_cloud import *

def build_baseline_model(input_shape=(224,224,3), freeze_base=True):
    base_model = applications.VGG16(
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



def fit_model(model, X_train, y_train, X_test, y_test):
    history = model.fit(
    X_train,
    y_train,
    batch_size=16,
    epochs=2,
    validation_data=(X_test,y_test))
    return model, history


def build_trained_model(X_train, y_train, X_test, y_test):
    model = build_baseline_model(input_shape=(224,224,3), freeze_base=True)
    trained_model, history = fit_model(model, X_train, y_train, X_test, y_test)
    gcs_uri = f"gs://{BUCKET_NAME_MODEL}/{trained_model}"
    # Save the model directly to GCS

    models.save_model(trained_model, gcs_uri)
    return trained_model, history


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
