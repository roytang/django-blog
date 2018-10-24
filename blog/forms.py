from django.forms import forms, fields, widgets

class PostForm(forms.Form):
	title = fields.CharField()
	content = fields.CharField(widget=widgets.Textarea)
	tags = fields.CharField()
	
	def __str__(self):
		return self.title