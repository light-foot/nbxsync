from django.db import migrations


def remove_stale_contenttypes(apps, schema_editor):
    """
    ZabbixEvent and ZabbixProblem are abstract models (synthetic table schemas for
    live Zabbix API data, never persisted) with no FilterSet. A stale ContentType
    row for either -- left over from an earlier plugin version -- has no resolvable
    model_class() and crashes NetBox's permission-constraint form when someone adds
    a constraint scoped to it. Abstract models never get a ContentType row on a
    fresh install, so this only needs to clean up any pre-existing stale rows.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='nbxsync', model__in=['zabbixevent', 'zabbixproblem']).delete()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('nbxsync', '0012_zabbixserver_skip_version_check'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(remove_stale_contenttypes, noop_reverse),
    ]
