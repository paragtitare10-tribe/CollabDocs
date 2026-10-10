import uuid
from django.db import migrations, models


def ensure_tag_tables(apps, schema_editor):
	Tag = apps.get_model("tags", "Tag")
	through_model = Tag._meta.get_field("documents").remote_field.through
	table_names = set(schema_editor.connection.introspection.table_names())
	new_tag_table = Tag._meta.db_table
	new_through_table = through_model._meta.db_table
	legacy_tag_table = "auditAndTag_tag"
	legacy_through_table = "auditAndTag_tag_documents"

	if new_tag_table not in table_names:
		if legacy_tag_table in table_names:
			schema_editor.alter_db_table(Tag, legacy_tag_table, new_tag_table)
		else:
			schema_editor.create_model(Tag)

	table_names = set(schema_editor.connection.introspection.table_names())
	if new_through_table not in table_names:
		if legacy_through_table in table_names:
			schema_editor.alter_db_table(
				through_model, legacy_through_table, new_through_table
			)
		else:
			schema_editor.create_model(through_model)


class Migration(migrations.Migration):
	initial = True

	dependencies = [
		("contenttypes", "0002_remove_content_type_name"),
		("document", "0001_initial"),
	]

	operations = [
		migrations.SeparateDatabaseAndState(
			database_operations=[],
			state_operations=[
				migrations.CreateModel(
					name="Tag",
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
						("name", models.CharField(max_length=100, unique=True)),
						(
							"documents",
							models.ManyToManyField(
								blank=True,
								related_name="tags",
								to="document.document",
							),
						),
					],
				),
			],
		),
		migrations.RunPython(ensure_tag_tables, migrations.RunPython.noop),
	]