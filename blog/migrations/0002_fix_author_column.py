from django.db import migrations


def ensure_author_column(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info('blog_blogpost')")
        cols = [row[1] for row in cursor.fetchall()]  # row[1] is column name
        if 'author' not in cols:
            cursor.execute("ALTER TABLE blog_blogpost ADD COLUMN author varchar(150) NOT NULL DEFAULT ''")


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(ensure_author_column, reverse_code=migrations.RunPython.noop),
    ]
