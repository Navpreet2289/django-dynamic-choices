from __future__ import unicode_literals

from django.forms.models import ModelForm

from .fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField  # NOQA


__all__ = ('DynamicModelForm', 'dynamic_model_form_factory')


def original_dynamic_model_form_factory(model_form_cls):
    class cls(model_form_cls):

        def __init__(self, *args, **kwargs):
            super(cls, self).__init__(*args, **kwargs)

            # Fetch initial data for initial
            data = self.initial.copy()

            # Update data if it's available
            for field in self.fields:
                raw_value = self._raw_value(field)
                if raw_value is not None:
                    if raw_value:
                        data[field] = raw_value
                    elif field in data:
                        del data[field]

            # Bind instances to dynamic fields
            for field in self.fields.values():
                if isinstance(field, DynamicModelChoiceField):
                    field.set_choice_data(self.instance, data)

        def get_dynamic_relationships(self):
            rels = {}
            opts = self.instance._meta
            for name, field in self.fields.items():
                # TODO: check for excludes?
                if isinstance(field, DynamicModelChoiceField):
                    for choice in opts.get_field(name).choices_relationships:
                        if not (choice in rels):
                            rels[choice] = set()
                        rels[choice].add(name)
            return rels

    cls.__name__ = str("Dynamic%s" % model_form_cls.__name__)
    return cls

DynamicModelForm = original_dynamic_model_form_factory(ModelForm)


def dynamic_model_form_factory(model_form_cls):
    cls = original_dynamic_model_form_factory(model_form_cls)
    cls.__bases__ += (DynamicModelForm,)
    return cls
