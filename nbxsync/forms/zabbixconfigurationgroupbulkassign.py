from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, VirtualDeviceContext
from virtualization.models import VirtualMachine
from utilities.forms.fields import DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet

__all__ = ('ZabbixConfigurationGroupBulkAssignForm',)


class ZabbixConfigurationGroupBulkAssignForm(forms.Form):
    """
    Assign many hosts to a Configuration Group in one operation. The dynamic
    fields support NetBox's full search and filter UI, so members can be
    picked by name, site, role and so on.
    """

    fieldsets = (FieldSet('devices', 'virtualdevicecontexts', 'virtualmachines', name=_('Members to assign')),)

    devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label=_('Devices'))
    virtualdevicecontexts = DynamicModelMultipleChoiceField(queryset=VirtualDeviceContext.objects.all(), required=False, label=_('Virtual Device Contexts'))
    virtualmachines = DynamicModelMultipleChoiceField(queryset=VirtualMachine.objects.all(), required=False, label=_('Virtual Machines'))

    def clean(self):
        super().clean()
        if not any((self.cleaned_data.get('devices'), self.cleaned_data.get('virtualdevicecontexts'), self.cleaned_data.get('virtualmachines'))):
            raise forms.ValidationError(_('Select at least one device, virtual device context, or virtual machine.'))
        return self.cleaned_data
