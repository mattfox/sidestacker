from django import forms


class MoveForm(forms.Form):
    x = forms.IntegerField(widget=forms.HiddenInput)
    y = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, game, player, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        self.player = player

    def clean(self, *args, **kwargs):
        """Make the move or handle errors."""
        cleaned_data = super().clean(*args, **kwargs)

        try:
            self.game.move(self.player, cleaned_data['x'], cleaned_data['y'])
            self.game.save()
        except ValueError as e:
            # Re-raise as a ValidationError
            raise forms.ValidationError(str(e), code="invalid")

        return cleaned_data
