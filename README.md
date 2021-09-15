[TensorFlow Datasets](https://www.tensorflow.org/datasets) for the iCyt platform.

## Installation

1. Request access to the dataset through the [UFZ data research portal](https://www.ufz.de/record/dmp/archive/11592/).
1. Copy the `.tar.gz` dataset to `~/tensorflow_datasets/downloads/manual/`.
2. Clone this repository and execute `tfds build` from the `poldiv` directory. The installation can take several hours.

## Usage

```python
import tensorflow as tf
import tensorflow_datasets as tfds

(ds_train, ds_validation, ds_test), ds_info = tfds.load('poldiv/all:2.0.0', split=['train[:80%]','train[80%:90%]','train[90%:]'], shuffle_files=True, with_info=True)
assert isinstance(ds_train, tf.data.Dataset)
assert isinstance(ds_validation, tf.data.Dataset)
assert isinstance(ds_test, tf.data.Dataset)
print(ds_info)
```
Output:
```
tfds.core.DatasetInfo(
    name='poldiv',
    full_name='poldiv/all/2.0.0',
    description="""
    The poldiv dataset contains IFC-measured pollen samples from 2018, 2019, 2020 and REF in 102 
    classes. The images are R3/R4-gated and depict single in-focus, non-cropped cells (R4) or cells/multiple cells of the 
    same species of poor quality that are cropped or polluted (R3). The dataset yields the individual multispectral 
    channels and their corresponding default masks that are generated by the Amnis ImageStream Mk II as separate 16-bit 
    images with varying width and height.
    """,
    config_description="""
    All samples without "Others", channels 1/2/3/4/5/6/9 only
    """,
    homepage='https://dataset-homepage/',
    data_path='/Users/lahr/tensorflow_datasets/poldiv/all/2.0.0',
    download_size=Unknown size,
    dataset_size=31.02 GiB,
    features=FeaturesDict({
        'channels': FeaturesDict({
            '1': Tensor(shape=(None, None), dtype=tf.uint16),
            '2': Tensor(shape=(None, None), dtype=tf.uint16),
            '3': Tensor(shape=(None, None), dtype=tf.uint16),
            '4': Tensor(shape=(None, None), dtype=tf.uint16),
            '5': Tensor(shape=(None, None), dtype=tf.uint16),
            '6': Tensor(shape=(None, None), dtype=tf.uint16),
            '9': Tensor(shape=(None, None), dtype=tf.uint16),
        }),
        'filename': tf.string,
        'label': ClassLabel(shape=(), dtype=tf.int64, num_classes=102),
        'masks': FeaturesDict({
            '1': Tensor(shape=(None, None), dtype=tf.uint16),
            '2': Tensor(shape=(None, None), dtype=tf.uint16),
            '3': Tensor(shape=(None, None), dtype=tf.uint16),
            '4': Tensor(shape=(None, None), dtype=tf.uint16),
            '5': Tensor(shape=(None, None), dtype=tf.uint16),
            '6': Tensor(shape=(None, None), dtype=tf.uint16),
            '9': Tensor(shape=(None, None), dtype=tf.uint16),
        }),
    }),
    supervised_keys=None,
    disable_shuffling=False,
    splits={
        'train': <SplitInfo num_examples=596450, num_shards=256>,
    },
    citation="""""",
)
```