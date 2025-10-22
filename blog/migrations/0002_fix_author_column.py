from django.db import migrations

def ensure_author_column(apps, schema_editor):
    connection = schema_editor.connection
    table_name = 'blog_blogpost'

    with connection.cursor() as cursor:
        # Deteksi jenis database
        engine = connection.vendor

        if engine == 'sqlite':
            # Cek kolom via PRAGMA (SQLite)
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            cols = [row[1] for row in cursor.fetchall()]  # row[1] = column name
        elif engine == 'postgresql':
            # Cek kolom via information_schema (PostgreSQL)
            cursor.execute(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{table_name}';
            """)
            cols = [row[0] for row in cursor.fetchall()]
        else:
            raise RuntimeError(f"Unsupported database backend: {engine}")

        # Tambahkan kolom kalau blm belum ada
        if 'author' not in cols:
            cursor.execute(
                f'ALTER TABLE {table_name} ADD COLUMN author VARCHAR(150) NOT NULL DEFAULT \'\''
            )

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(ensure_author_column, reverse_code=migrations.RunPython.noop),
    ]
