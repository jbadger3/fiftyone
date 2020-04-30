"""
Core Module for `fiftyone` Session class

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
import fiftyone.core.client as voxc
import fiftyone.core.query as voxq


def update_state(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._update_state()
        return result

    return wrapper


class Session(voxc.HasClient):
    """Sessions have a 1-to-1 shared state with the GUI."""

    _HC_NAMESPACE = "state"
    _HC_ATTR_NAME = "state"

    DEFAULT_OFFSET = 0
    DEFAULT_LIMIT = 10

    @update_state
    def __init__(self, offset=DEFAULT_OFFSET, limit=DEFAULT_LIMIT):
        super(Session, self).__init__()
        self._offset = offset
        self._limit = limit

    # GETTERS #################################################################

    @property
    def offset(self):
        return self._offset

    @property
    def limit(self):
        return self._limit

    @property
    def dataset(self):
        if not hasattr(self, "_dataset"):
            self._dataset = None
        return self._dataset

    @property
    def view(self):
        if not hasattr(self, "_view"):
            self._view = None
        return self._view

    @property
    def query(self):
        if not hasattr(self, "_query"):
            self._query = None
        return self._query

    # SETTERS #################################################################

    @offset.setter
    @update_state
    def offset(self, offset):
        self._offset = offset

    @limit.setter
    @update_state
    def limit(self, limit):
        self._limit = limit

    @dataset.setter
    @update_state
    def dataset(self, dataset):
        self._dataset = dataset

    @view.setter
    @update_state
    def view(self, view):
        self._view = view
        self._dataset = self._view.dataset

    @query.setter
    @update_state
    def query(self, query):
        self._query = query

    # CLEAR STATE #############################################################

    @update_state
    def clear_offset(self):
        self._offset = self.DEFAULT_OFFSET

    @update_state
    def clear_limit(self):
        self._limit = self.clear_limit

    @update_state
    def clear_dataset(self):
        self._dataset = None
        self._view = None

    @update_state
    def clear_view(self):
        self._view = None

    @update_state
    def clear_query(self):
        self._query = None

    # PRIVATE #################################################################

    def _update_state(self):
        self.state = {
            "dataset_name": self.dataset.name if self.dataset else None,
            "view_tag": self.view.tag if self.view else None,
            "query": self.query._pipeline if self.query else None,
            "page": {
                "offset": self.offset,
                "limit": self.limit,
                "count": self._compute_count(),
            },
            "samples": self._compute_samples(),
        }

    def _get_dataset_or_view(self):
        # view takes precedence over dataset if set
        return self.view if self.view else self.dataset

    def _compute_count(self):
        dataset_or_view = self._get_dataset_or_view()
        if self.query and dataset_or_view:
            return self.query.count(dataset_or_view)
        if dataset_or_view:
            return len(dataset_or_view)
        return 0

    def _compute_samples(self):
        dataset_or_view = self._get_dataset_or_view()

        if not dataset_or_view:
            return {}

        query = self.query if self.query else voxq.DatasetQuery()

        return {
            query_idx: sample.serialize()
            for query_idx, sample in (
                query.offset(self.offset)
                .limit(self.limit)
                .iter_samples(dataset_or_view)
            )
        }