from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from nbxsync.forms import ZabbixConfigurationGroupBulkAssignForm
from nbxsync.models import ZabbixConfigurationGroup, ZabbixConfigurationGroupAssignment

__all__ = ('ConfigGroupBulkAssignView', 'ConfigGroupQuickAssignView')


class ConfigGroupQuickAssignView(PermissionRequiredMixin, View):
    """
    Inline assignment of a Configuration Group to a Device, VDC or VM,
    posted from the Zabbix tab without leaving the page.
    """

    permission_required = 'nbxsync.add_zabbixconfigurationgroupassignment'

    def post(self, request):
        ct = get_object_or_404(ContentType, pk=request.POST.get('assigned_object_type'))
        try:
            target = ct.get_object_for_this_type(pk=request.POST.get('assigned_object_id'))
        except Exception:
            messages.error(request, 'Assignment target not found.')
            return redirect('/')

        group = get_object_or_404(ZabbixConfigurationGroup, pk=request.POST.get('zabbixconfigurationgroup'))

        _assignment, created = ZabbixConfigurationGroupAssignment.objects.get_or_create(
            zabbixconfigurationgroup=group,
            assigned_object_type=ct,
            assigned_object_id=target.pk,
        )
        if created:
            messages.success(request, f'Assigned {target} to configuration group "{group.name}".')
        else:
            messages.info(request, f'{target} is already a member of "{group.name}".')

        return_url = request.POST.get('return_url')
        if return_url and url_has_allowed_host_and_scheme(return_url, allowed_hosts={request.get_host()}):
            return redirect(return_url)
        return redirect(target.get_absolute_url())


class ConfigGroupBulkAssignView(PermissionRequiredMixin, View):
    """
    Assign many devices, VDCs or VMs to a Configuration Group at once.
    """

    permission_required = 'nbxsync.add_zabbixconfigurationgroupassignment'
    template_name = 'nbxsync/zabbixconfigurationgroup_bulkassign.html'

    def get(self, request, pk):
        group = get_object_or_404(ZabbixConfigurationGroup, pk=pk)
        form = ZabbixConfigurationGroupBulkAssignForm()
        return render(request, self.template_name, {'object': group, 'form': form, 'return_url': group.get_absolute_url()})

    def post(self, request, pk):
        group = get_object_or_404(ZabbixConfigurationGroup, pk=pk)
        form = ZabbixConfigurationGroupBulkAssignForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'object': group, 'form': form, 'return_url': group.get_absolute_url()})

        created = 0
        skipped = 0
        targets = list(form.cleaned_data['devices']) + list(form.cleaned_data['virtualdevicecontexts']) + list(form.cleaned_data['virtualmachines'])
        for target in targets:
            ct = ContentType.objects.get_for_model(target)
            _assignment, was_created = ZabbixConfigurationGroupAssignment.objects.get_or_create(
                zabbixconfigurationgroup=group,
                assigned_object_type=ct,
                assigned_object_id=target.pk,
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        if skipped:
            messages.success(request, f'Assigned {created} host(s) to "{group.name}" ({skipped} already assigned).')
        else:
            messages.success(request, f'Assigned {created} host(s) to "{group.name}".')
        return redirect(group.get_absolute_url())
