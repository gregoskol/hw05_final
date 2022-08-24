from django import forms


def clean_post(text):
    if text == '':
        raise forms.ValidationError(
            'Текст сообщения не может быть пустым',
            params={'text': text}
        )
