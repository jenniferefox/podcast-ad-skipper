import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras import Model, Sequential, layers, regularizers, optimizers, applications, models
from podcast_ad_skipper.params import *
from podcast_ad_skipper.google_cloud import *
import numpy as np
from sklearn.model_selection import train_test_split
from data_preparation import get_bq_processed_data

INPUT_SHAPE = (128, 216, 1)

def prep_data_for_model(spectrograms, labels, seconds=None, duration=None):

    X = np.expand_dims(np.array(spectrograms), axis=-1)
    y = np.array(labels)
    
    #Feature to calculate progress

    # X_timing = np.array(all_spectrograms[2]/all_spectrograms[3])

    X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,  # This ensures similar class distribution in train/test splits
    )
    return X_train, X_test, y_train, y_test

def build_baseline_model(input_shape=(128,216,1)):
    model = tf.keras.models.Sequential([
    # Input layer - note that Input() doesn't take an activation
    tf.keras.layers.Input(shape=input_shape),

    # Conv2D layer
    tf.keras.layers.Conv2D(32, 3, strides=2, padding='same', activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Conv2D(64, 3, padding='same', activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Conv2D(128, 3, padding='same', activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
    tf.keras.layers.BatchNormalization(),

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



def fit_model(model, X_train, X_test, y_train, y_test):

    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    history = model.fit(
    X_train,
    y_train,
    batch_size=16,
    epochs=50,
    validation_data=(X_test,y_test),
    callbacks=[early_stopping,])
    return model, history

def save_model_to_gcs(model, bucket_name, model_name="latest_trained_model.h5"):
    """
    Save a TensorFlow model directly to Google Cloud Storage.

    Args:
        model: TensorFlow model to save
        bucket_name: Name of the GCS bucket
        model_name: Name of the model file

    Returns:
        tuple: (bool, str) - (success status, message)
    """
    # Initialize GCS client
    gc_client = auth_gc_storage()

    # Check if bucket exists
    if not gc_client.bucket(bucket_name):
        return False, f"Bucket {bucket_name} not found"

    # Get bucket
    bucket = gc_client.bucket(bucket_name)

    # Create GCS URI for saving
    gcs_uri = f"gs://{bucket_name}/{model_name}"

    # Attempt to save model directly to GCS
    save_status = models.save_model(
        model,
        gcs_uri,
        overwrite=True,
        include_optimizer=True,
        save_format='h5'
    )

    # Check save status
    if save_status is None:  # TensorFlow returns None on successful save
        print(f"Model saved successfully to {gcs_uri}")
        return True

    else:
        print("Failed to save model to GCS")
        return False

def build_trained_model(X_train, X_test, y_train, y_test):
    model = build_baseline_model(input_shape=INPUT_SHAPE)
    latest_trained_model, history = fit_model(model, X_train, X_test, y_train, y_test)

    save_model_to_gcs(latest_trained_model, BUCKET_NAME_MODEL)

    return latest_trained_model, history


# def download_model_from_gcs(gcs_uri):
#     client = auth_gc_storage()
#     blobs = list(client.get_bucket(BUCKET_NAME_MODEL).list_blobs())

#     try:
#         latest_trained_model = models.load_model(gcs_uri)
#         print("✅ Latest model downloaded from cloud storage")
#         return latest_trained_model

#     except:
#         print(f"\n❌ No model found in GCS bucket {BUCKET_NAME_MODEL}")
#         return None


def download_model_from_gcs(bucket_name, model_name="latest_trained_model.h5"):
    """
    Download a TensorFlow model from Google Cloud Storage.

    Args:
        bucket_name: Name of the GCS bucket
        model_name: Name of the model file

    Returns:
        model: TensorFlow model or None if download fails
    """
    try:
        # Initialize GCS client
        storage_client = auth_gc_storage()

        # Check if bucket exists
        if not storage_client.lookup_bucket(bucket_name):
            return None, f"Bucket {bucket_name} not found"

        # Get bucket
        bucket = storage_client.bucket(bucket_name)

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary file path
            temp_model_path = os.path.join(temp_dir, model_name)

            # Download file from GCS
            blob = bucket.blob(model_name)
            blob.download_to_filename(temp_model_path)

            # Load the model using TensorFlow
            model = tf.keras.models.load_model(temp_model_path)

            return model, f"Model successfully downloaded from gs://{bucket_name}/{model_name}"

    except Exception as e:
        return None, f"Error downloading model from GCS: {str(e)}"



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

def predict(model, X_predict):
    return model.predict(X_predict)

if __name__ == "__main__":
    bq_client = auth_gc_bigquery()
    print('Auth bigquery')

    table_id = f"{GCP_PROJECT_ID}.Numpy_Arrays_Dataset.processed_train_data_II"
    print('table ID')
    output= get_output_query_bigquery(bq_client, table_id, custom="Leo")
    print('bq output')
    processed_output = get_bq_processed_data(output)
    print('process bq output')

    spectrogram_np = np.array(processed_output[0])
    labels_np = np.array(processed_output[1])
    print(spectrogram_np.shape)
    print(labels_np.shape)

    X_train, X_test, y_train, y_test = prep_data_for_model(spectrogram_np, labels_np)
    print(X_train.shape)

    print('X and y split')
    build_trained_model(X_train, X_test, y_train, y_test)
    print('trained model built')
