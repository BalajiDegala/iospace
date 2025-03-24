from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with Bootstrap styling."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class ProjectForm(forms.Form):
    """Form for creating and updating projects."""
    name = forms.CharField(
        label="Project Name",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    code = forms.CharField(
        label="Project Code",
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    library = forms.BooleanField(
        label="Library Project",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    active = forms.BooleanField(
        label="Active",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    deadline = forms.DateField(
        label="Deadline",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class SequenceForm(forms.Form):
    """Form for creating and updating sequences (folders)."""
    name = forms.CharField(
        label="Sequence Name",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    label = forms.CharField(
        label="Display Label",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    parent_id = forms.CharField(
        label="Parent Folder ID",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    def __init__(self, *args, **kwargs):
        folders = kwargs.pop('folders', None)
        super(SequenceForm, self).__init__(*args, **kwargs)
        
        if folders:
            # Replace the parent_id field with a select field
            choices = [('', '-- Root --')] + [(folder['id'], folder['name']) for folder in folders]
            self.fields['parent_id'] = forms.ChoiceField(
                label="Parent Folder",
                required=False,
                choices=choices,
                widget=forms.Select(attrs={'class': 'form-control'})
            )


class ShotForm(forms.Form):
    """Form for creating and updating shots (products)."""
    name = forms.CharField(
        label="Shot Name",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    label = forms.CharField(
        label="Display Label",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    folder_id = forms.CharField(
        label="Sequence (Folder) ID",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    status = forms.CharField(
        label="Status",
        max_length=50,
        initial="in_progress",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    frame_start = forms.IntegerField(
        label="Start Frame",
        initial=1001,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    frame_end = forms.IntegerField(
        label="End Frame",
        initial=1100,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        folders = kwargs.pop('folders', None)
        super(ShotForm, self).__init__(*args, **kwargs)
        
        if folders:
            # Replace the folder_id field with a select field
            choices = [(folder['id'], folder['name']) for folder in folders]
            self.fields['folder_id'] = forms.ChoiceField(
                label="Sequence",
                choices=choices,
                widget=forms.Select(attrs={'class': 'form-control'})
            )


class TaskForm(forms.Form):
    """Form for creating and updating tasks."""
    name = forms.CharField(
        label="Task Name",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    label = forms.CharField(
        label="Display Label",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    product_id = forms.CharField(
        label="Shot (Product) ID",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    task_type = forms.CharField(
        label="Task Type",
        max_length=50,
        initial="Compositing",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    status = forms.CharField(
        label="Status",
        max_length=50,
        initial="todo",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    assignees = forms.CharField(
        label="Assignees (comma-separated)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        products = kwargs.pop('products', None)
        task_types = kwargs.pop('task_types', None)
        statuses = kwargs.pop('statuses', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        
        if products:
            # Replace the product_id field with a select field
            choices = [(product['id'], product['name']) for product in products]
            self.fields['product_id'] = forms.ChoiceField(
                label="Shot",
                choices=choices,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        
        if task_types:
            # Replace the task_type field with a select field
            choices = [(tt, tt) for tt in task_types]
            self.fields['task_type'] = forms.ChoiceField(
                label="Task Type",
                choices=choices,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        
        if statuses:
            # Replace the status field with a select field
            choices = [(status, status) for status in statuses]
            self.fields['status'] = forms.ChoiceField(
                label="Status",
                choices=choices,
                widget=forms.Select(attrs={'class': 'form-control'})
            )