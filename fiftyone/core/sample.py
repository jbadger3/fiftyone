"""
Core Module for `fiftyone` Sample class

"""
# pragma pylint: disable=redefined-builtin
# pragma pylint: disable=unused-wildcard-import
# pragma pylint: disable=wildcard-import
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import *

# pragma pylint: enable=redefined-builtin
# pragma pylint: enable=unused-wildcard-import
# pragma pylint: enable=wildcard-import
import os

import eta.core.image as etai
import eta.core.serial as etas

import fiftyone.core.document as voxd
import fiftyone.core.label as voxl


class Sample(voxd.Document):
    def __init__(self, filepath, tags=None, labels=None):
        self.filepath = os.path.abspath(filepath)
        self.filename = os.path.basename(filepath)
        self.tags = tags or []

        if isinstance(labels, voxl.LabelSet):
            self.labels = labels
        elif isinstance(labels, voxl.Label):
            self.labels = voxl.LabelSet(labels=[labels])
        elif labels is None:
            self.labels = voxl.LabelSet()
        else:
            raise ValueError("Unexpected labels type: %s" % type(labels))

    @property
    def dataset(self):
        # @todo(Tyler) This could be stored similar to how I originally
        # implemented ingest_time
        raise NotImplementedError("TODO")

    def add_label(self, label):
        # @todo(Tyler) this does not write to the database
        self.labels.add(label)

    @classmethod
    def validate(cls, sample):
        if not isinstance(sample, cls):
            raise ValueError(
                "Unexpected 'sample' type: '%s', expected: '%s'"
                % (type(sample), cls)
            )
        return sample

    @classmethod
    def _from_dict(cls, d, *args, **kwargs):
        sample = cls(**cls._parse_kwargs_from_dict(d))

        return sample

    # PRIVATE #################################################################

    @classmethod
    def _parse_kwargs_from_dict(cls, d):
        kwargs = {
            "filepath": d["filepath"],
            "tags": d.get("tags", None),
        }

        if "label" in d:
            kwargs["label"] = etas.Serializable.from_dict(d["label"])

        return kwargs


class ImageSample(Sample):

    def __init__(self, metadata=None, *args, **kwargs):
        super(ImageSample, self).__init__(*args, **kwargs)
        self.metadata = metadata or etai.ImageMetadata.build_for(self.filepath)

    def load_image(self):
        return etai.read(self.filepath)

    # PRIVATE #################################################################

    @classmethod
    def _parse_kwargs_from_dict(cls, d):
        kwargs = super(ImageSample, cls)._parse_kwargs_from_dict(d)

        if "metadata" in d:
            kwargs["metadata"] = etai.ImageMetadata.from_dict(d["metadata"])

        return kwargs
