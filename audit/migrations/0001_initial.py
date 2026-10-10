import django.db.models.deletion
import uuid
from django.db import migrations, models


def ensure_audit_log_table(apps, schema_editor):
	AuditLog = apps.get_model("audit", "AuditLog")
	table_names = set(schema_editor.connection.introspection.table_names())
	new_table = AuditLog._meta.db_table
	legacy_table = "auditAndTag_auditlog"

	if new_table in table_names:
		return
	if legacy_table in table_names:
		schema_editor.alter_db_table(AuditLog, legacy_table, new_table)
	else:
		schema_editor.create_model(AuditLog)


class Migration(migrations.Migration):
	initial = True

	dependencies = [
		("contenttypes", "0002_remove_content_type_name"),
		("user", "0001_initial"),
	]

	operations = [
		migrations.SeparateDatabaseAndState(
			database_operations=[],
			state_operations=[
				migrations.CreateModel(
					name="AuditLog",
					fields=[
						(
							"id",
						models.UUIDField(
							default=uuid.uuid4,
							editable=False,
							primary_key=True,
							serialize=False,
						),
						),
						("action", models.CharField(max_length=255)),
						("model_name", models.CharField(max_length=100)),
						("object_id", models.UUIDField()),
						("timestamp", models.DateTimeField(auto_now_add=True)),
						(
							"actor",
							models.ForeignKey(
								null=True,
								on_delete=django.db.models.deletion.SET_NULL,
								related_name="audit_logs",
								to="user.user",
							),
						),
					],
				),
			],
		),
		migrations.RunPython(ensure_audit_log_table, migrations.RunPython.noop),
	]