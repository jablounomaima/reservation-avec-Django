from appointments.models import Pet


def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)
    if user:
        self.fields['pet'].queryset = Pet.objects.filter(owner=user)