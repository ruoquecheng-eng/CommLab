"""Shared Streamlit controls and metric capture for the legacy lab renderers."""

from __future__ import annotations

from collections.abc import Callable


WIDGETS = {"checkbox", "number_input", "select_slider", "selectbox", "slider"}


class Controls:
    def __init__(self, form):
        self.form = form
        self.values: dict[str, object] = {}

    def __getattr__(self, name: str) -> Callable:
        method = getattr(self.form, name)
        if name not in WIDGETS:
            return method

        def capture(label, *args, **kwargs):
            value = method(label, *args, **kwargs)
            self.values[str(label)] = value
            return value

        return capture


class MetricColumn:
    def __init__(self, column, metrics: list[dict]):
        self.column = column
        self.metrics = metrics

    def metric(self, label, value, *args, **kwargs):
        self.metrics.append({"name": str(label), "value": str(value)})
        return self.column.metric(label, value, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.column, name)


def captured_columns(streamlit, metrics: list[dict]):
    def make_columns(*args, **kwargs):
        return [MetricColumn(column, metrics) for column in streamlit.columns(*args, **kwargs)]

    return make_columns
