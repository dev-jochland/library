from django.forms import ModelForm
from django import forms
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy
from .models import BookInstance


# Creating a Form class using this (forms.Form) approach described below is very
# flexible, allowing you to create whatever sort of form page you like and associate
# it with any model or models.


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text="Enter a date between now and 4 weeks (default 3).")

# Django provides numerous places where you can validate your data. The easiest way to
# validate a single field is to override the method clean_<fieldname>() for the field
# you want to check
    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(ugettext_lazy(
                'Invalid date: Renewal in past'))

        # check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(ugettext_lazy(
                'Invalid date: Renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data
        return data


# However, if you just need a form to map the fields of a single model then your model will
# already define most of the information that you need in your form: fields, labels, help
# text and so on. Rather than recreating the model definitions in your form, it is easier
# to use the ModelForm helper class to create the form from your model. This ModelForm can
# then be used within your views in exactly the same way as an ordinary Form.


class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
        data = self.cleaned_data['due_back']

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(ugettext_lazy('Invalid date - renewal in past'))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(ugettext_lazy('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data

    class Meta:
        model = BookInstance

        # you can include all fields using fields = '__all__', or you can use exclude (instead of
        # fields) to specify the fields not to include from the model
        fields = ['due_back']

        # Field 'due_back' in models.py didn't define any of the model definition overridden below.
        # The rest of the information comes from the model field definitions
        # (e.g. labels, widgets, help text, error messages). If these aren't quite right, then
        # override them in class Meta here as done below, specifying a dictionary containing
        # the field to change and its new value
        labels = {'due_back': ugettext_lazy('Renewal date')}
        help_texts = {'due_back': ugettext_lazy('Enter a date between now and 4 weeks (default 3).')}


# ARGUMENTS COMMON TO MOST FIELDS
# 1. required: If True, the field may not be left blank or given a None value. Fields are
# required by default, so you would set required=False to allow blank values in the form.

# 2. label: The label to use when rendering the field in HTML. If a label is not specified,
# Django will create one from the field name by capitalizing the first letter and replacing
# underscores with spaces (e.g. Renewal date).

# 3. label_suffix: By default, a colon is displayed after the label (e.g. Renewal date:).
# This argument allows you to specify a different suffix containing other character(s).

# 4. initial: The initial value for the field when the form is displayed.

# 5. widget: The display widget to use.

# 6. help_text (as seen in the example above): Additional text that can be displayed in
# forms to explain how to use the field.

# 7. error_messages: A list of error messages for the field. You can override these with
# your own messages if needed.

# 8. validators: A list of functions that will be called on the field when it is validated.

# 9. localize: Enables the localization of form data input (see link for more information).

# 10. disabled: The field is displayed but its value cannot be edited if this is True. The
# default is False.
