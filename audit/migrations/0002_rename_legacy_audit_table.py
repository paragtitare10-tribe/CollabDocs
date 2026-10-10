from django.db import migrations


LEGACY_TABLE = "auditAndTag_auditlog"


def rename_table(apps, schema_editor, old_name, new_name):
	AuditLog = apps.get_model("audit", "AuditLog")
	table_names = set(schema_editor.connection.introspection.table_names())
	if old_name in table_names and new_name not in table_names:
		schema_editor.alter_db_table(AuditLog, old_name, new_name)


def forwards(apps, schema_editor):
	AuditLog = apps.get_model("audit", "AuditLog")
	rename_table(apps, schema_editor, LEGACY_TABLE, AuditLog._meta.db_table)


def backwards(apps, schema_editor):
	AuditLog = apps.get_model("audit", "AuditLog")
	rename_table(apps, schema_editor, AuditLog._meta.db_table, LEGACY_TABLE)


class Migration(migrations.Migration):
	dependencies = [("audit", "0001_initial")]

	operations = [migrations.RunPython(forwards, backwards)]