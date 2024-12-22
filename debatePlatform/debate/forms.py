from django.forms import ModelForm, ValidationError
from .models import Debate, Argument
from django.utils import timezone

class CreateDebateForm(ModelForm):
    class Meta:
        model = Debate
        fields = ['title', 'description', 'category', 'start_time', 'end_time']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time >= end_time:
            raise ValidationError({"start_time": "Start time must be before end time."})

        if start_time <= timezone.now():
            raise ValidationError({"start_time": "Start time must be in the future."})

        return cleaned_data


class CreateArgumentForm(ModelForm):
    class Meta:
        model = Argument
        fields = ['side', 'text']


