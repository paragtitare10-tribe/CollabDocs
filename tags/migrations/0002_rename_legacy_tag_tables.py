from django.db import migrations


LEGACY_TAG_TABLE = "auditAndTag_tag"
LEGACY_THROUGH_TABLE = "auditAndTag_tag_documents"


def rename_table(schema_editor, model, old_name, new_name):
	table_names = set(schema_editor.connection.introspection.table_names())
	if old_name in table_names and new_name not in table_names:
		schema_editor.alter_db_table(model, old_name, new_name)


def forwards(apps, schema_editor):
	Tag = apps.get_model("tags", "Tag")
	through_model = Tag._meta.get_field("documents").remote_field.through
	rename_table(schema_editor, Tag, LEGACY_TAG_TABLE, Tag._meta.db_table)
	rename_table(
		schema_editor,
		through_model,
		LEGACY_THROUGH_TABLE,
		through_model._meta.db_table,
	)


def backwards(apps, schema_editor):
	Tag = apps.get_model("tags", "Tag")
	through_model = Tag._meta.get_field("documents").remote_field.through
	rename_table(schema_editor, Tag, Tag._meta.db_table, LEGACY_TAG_TABLE)
	rename_table(
		schema_editor,
		through_model,
		through_model._meta.db_table,
		LEGACY_THROUGH_TABLE,
	)


class Migration(migrations.Migration):
	dependencies = [("tags", "0001_initial")]

	operations = [migrations.RunPython(forwards, backwards)]