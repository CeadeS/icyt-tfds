"""poldiv dataset."""

import csv
import os
import re

import tensorflow as tf
import tensorflow_datasets as tfds
import tifffile as tiff

_DESCRIPTION = """The poldiv dataset contains IFC-measured pollen samples from 2018 to 2021 in 117 species and 57 
genera. The images are R3/R4-gated and depict single in-focus, non-cropped cells (R4) or cells/multiple cells of the 
same species of poor quality that are cropped or polluted (R3). The dataset yields the individual multispectral 
channels and their corresponding default masks that are generated by the Amnis ImageStream Mk II as separate 16-bit 
images with varying width and height."""

# TODO(poldiv): BibTeX citation
_CITATION = """
"""

_DATA_OPTIONS = ['all']


class PoldivConfig(tfds.core.BuilderConfig):
    """BuilderConfig for poldiv dataset."""

    def __init__(self, dataset=None, selection=None, **kwargs):
        """Constructs a PoldivConfig.

        Args:
          selection: `str`, one of `_DATA_OPTIONS`.
          **kwargs: keyword arguments forwarded to super.
        """

        if selection not in _DATA_OPTIONS:
            raise ValueError('Selection must be one of %s' % _DATA_OPTIONS)

        super(PoldivConfig, self).__init__(
            version=tfds.core.Version('3.0.0'),
            release_notes={
                '3.0.0': 'New dataset',
                '2.4.0': 'Removed builder config for balanced dataset',
                '2.3.0': 'Builder config for balanced dataset',
                '2.2.0': 'Genus as separate feature',
                '2.1.0': 'Builder configs for all-species and all-genus',
                '2.0.0': 'Additional Urtica samples',
                '1.0.0': 'Full dataset',
                '0.1.0': 'Initial release.'
            },
            **kwargs)
        self.selection = selection
        self.dataset = dataset


class Poldiv(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for poldiv dataset."""

    MANUAL_DOWNLOAD_INSTRUCTIONS = """
    Place the dataset tar.gz file in the `~/tensorflow_datasets/downloads/manual` dir.
    """

    # pytype: disable=wrong-keyword-args
    BUILDER_CONFIGS = [
        PoldivConfig(name='all', selection='all', dataset="poldiv-dataset-3.0.0.tar.gz",
                     description='All samples, channels 1/2/3/4/5/6/9 only'),
    ]

    # pytype: enable=wrong-keyword-args

    def _info(self) -> tfds.core.DatasetInfo:
        """Returns the dataset metadata."""

        channels = {str(i + 1): tfds.features.Tensor(dtype=tf.uint16, shape=(None, None), encoding='zlib') for i in
                    range(6)}
        channels['9'] = tfds.features.Tensor(dtype=tf.uint16, shape=(None, None), encoding='zlib')
        masks = {str(i + 1): tfds.features.Tensor(dtype=tf.uint16, shape=(None, None), encoding='zlib') for i in
                 range(6)}
        masks['9'] = tfds.features.Tensor(dtype=tf.uint16, shape=(None, None), encoding='zlib')

        features = {'channels': {**channels},
                    'masks': {**masks},
                    'filename': tf.string,
                    'species': tfds.features.ClassLabel(
                        names_file=f'poldiv/classes-{self.builder_config.selection}-species.txt'),
                    'genus': tfds.features.ClassLabel(
                        names_file=f'poldiv/classes-{self.builder_config.selection}-genus.txt')}

        return tfds.core.DatasetInfo(
            builder=self,
            description=_DESCRIPTION,
            features=tfds.features.FeaturesDict(features),
            supervised_keys=None,
            homepage='https://github.com/lahr/icyt-tfds',
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Returns SplitGenerators."""

        path = os.path.join(dl_manager.manual_dir, self.builder_config.dataset)

        if not tf.io.gfile.exists(path):
            raise AssertionError(
                f'You must download the dataset .tar.gz file and place it into {dl_manager.manual_dir}')

        if self.builder_config.selection == 'all':
            path_iter = dl_manager.iter_archive(path)
            return {
                'train': self._generate_examples(path_iter)
            }

    def _generate_examples(self, path_iter, split_name=None):
        """Yields examples."""

        path_regex = r'^(?:([^/\n.A-Z]+)/)?([a-zA-Z]+\.?[a-zA-Z]+).*$'

        mapping_reader = csv.DictReader(open('poldiv/mapping-species-genus.csv'), fieldnames=['species', 'genus'])
        mappings = list(mapping_reader)

        for filename, fobj in path_iter:
            assert filename is not None
            assert fobj is not None

            m = re.match(path_regex, filename)
            species = m.group(2).lower()

            if 'chaenopodium.album' == species:
                species = 'chenopodium.album'

            elif 'galium.mullogo' == species:
                species = 'galium.mollugo'

            elif 'ginkgo.bilboa' == species:
                species = 'ginkgo.biloba'

            mapping_result = next((item for item in mappings if item['species'] == species), None)
            assert mapping_result is not None, f'Genus not found for {species}'
            genus = mapping_result['genus']

            img = tiff.imread(fobj)
            num_channels = img.shape[-1] / 2  # for 2018 there are 7, 9 or 12 channels

            if num_channels == 7 or num_channels == 9:
                channels = {str(i + 1): img[:, :, i] for i in range(0, 6)}
                channels['9'] = img[:, :, 6]
                masks = {str(i - 6): img[:, :, i] for i in range(7, 13)}
                masks['9'] = img[:, :, 13]

            elif num_channels == 12:
                channels = {str(i + 1): img[:, :, i] for i in range(0, 6)}
                channels['9'] = img[:, :, 8]
                masks = {str(i - 11): img[:, :, i] for i in range(12, 18)}
                masks['9'] = img[:, :, 20]

            else:
                raise AssertionError(f'Unknown number of channels ({num_channels}) for file {filename}')

            features = {
                'channels': {**channels},
                'masks': {**masks},
                'filename': filename,
                'species': species,
                'genus': genus}

            yield filename, features
