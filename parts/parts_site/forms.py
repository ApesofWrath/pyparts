# import form class from django
from django import forms
import os
 
# import GeeksModel from models.py
from .models import *
 
# create a ModelForm
class ProjectForm(forms.ModelForm):
    # specify the name of model to use
    create_onshape_project = forms.BooleanField(required=False, label="Create Onshape Project")
    class Meta:
        model = Project
        fields = ["name", "description", "prefix"]

class AssemblyForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Assembly
        fields = ["name", "description"]

class AssemblyFormEdit(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Assembly
        fields = "__all__"

class SubAssemblyForm(AssemblyForm):
    # specify the name of model to use
    class Meta:
        model = SubAssembly
        fields = ["name", "description"]

class PartForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Part
        fields = ["assembly", "name", "description"]

class PartFormEdit(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Part
        fields = ["name", "description"]

class PartRevisionForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = PartRevision
        fields = ["status", "drawing", "material", "quantity", "mfg_type", "owner", "notes"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_drawing(self):
        drawing = self.cleaned_data.get('drawing')
        if drawing:
            allowed_extensions = ['.pdf', '.dwg', '.dxf', '.step', '.stp', '.iges', '.stl', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.nc', '.gcode']
            file_extension = os.path.splitext(drawing.name)[1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_extensions)}")
        return drawing

    def clean(self):
        super().clean()

        if self.cleaned_data.get("status") >= PartStatus.MFG_REVIEWED:
            if self.cleaned_data.get("drawing") == None:
                self._errors["drawing"] = self.error_class(["Drawing required to advance status"])
            if self.cleaned_data.get("material") == None:
                self._errors["material"] = self.error_class(["Material required to advance status"])
            if self.cleaned_data.get("quantity") == None:
                self._errors["quantity"] = self.error_class(["Quantity required to advance status"])
            if self.cleaned_data.get("mfg_type") == None:
                self._errors["mfg_type"] = self.error_class(["Manufacturing method required to advance status"])

        if self.cleaned_data.get("status") == PartStatus.DESIGN_REVIEWED:
            if not self.user.groups.filter(name='mentors').exists():
                self._errors["Status"] = self.error_class(["Only a mentor can complete this step"])
        if self.cleaned_data.get("status") in [PartStatus.MFG_REVIEWED, PartStatus.QUALITY_CHECKED] :
            if not self.user.groups.filter(name='leads').exists():
                self._errors["Status"] = self.error_class(["Only a lead can complete this step"])

        return self.cleaned_data

class PartRevisionCreateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = PartRevision
        fields = ["revision_number", "status", "drawing", "material", "quantity", "mfg_type", "owner", "notes"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_drawing(self):
        drawing = self.cleaned_data.get('drawing')
        if drawing:
            allowed_extensions = ['.pdf', '.dwg', '.dxf', '.step', '.stp', '.iges', '.stl', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.nc', '.gcode']
            file_extension = os.path.splitext(drawing.name)[1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_extensions)}")
        return drawing

    def clean(self):
        super().clean()

        if self.cleaned_data.get("status") >= PartStatus.MFG_REVIEWED:
            if self.cleaned_data.get("drawing") == None:
                self._errors["drawing"] = self.error_class(["Drawing required to advance status"])
            if self.cleaned_data.get("material") == None:
                self._errors["material"] = self.error_class(["Material required to advance status"])
            if self.cleaned_data.get("quantity") == None:
                self._errors["quantity"] = self.error_class(["Quantity required to advance status"])
            if self.cleaned_data.get("mfg_type") == None:
                self._errors["mfg_type"] = self.error_class(["Manufacturing method required to advance status"])

        if self.cleaned_data.get("status") == PartStatus.DESIGN_REVIEWED:
            if not self.user.groups.filter(name='mentors').exists():
                self._errors["Status"] = self.error_class(["Only a mentor can complete this step"])
        if self.cleaned_data.get("status") in [PartStatus.MFG_REVIEWED, PartStatus.QUALITY_CHECKED] :
            if not self.user.groups.filter(name='leads').exists():
                self._errors["Status"] = self.error_class(["Only a lead can complete this step"])

        return self.cleaned_data

class ItemForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Item
        fields = ["name", "vendor", "part_number", "link", "unit_price", "quantity", "justification"]

class OrderFormEdit(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Order
        fields = ["order_id","order_placed_date","order_recv_date","tracking","status"]

    def clean(self):
        super().clean()

        if self.cleaned_data.get("status") >= OrderStatus.PLACED:
            if self.cleaned_data.get("order_placed_date") == None:
                self._errors["order_placed_date"] = self.error_class(["Order Placed Date required to advance status"])
        if self.cleaned_data.get("status") >= OrderStatus.RECEIVED:
            if self.cleaned_data.get("order_recv_date") == None:
                self._errors["order_recv_date"] = self.error_class(["Order Received Date required to advance status"])

        return self.cleaned_data