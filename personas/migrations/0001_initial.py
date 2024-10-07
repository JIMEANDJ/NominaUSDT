# Generated by Django 5.0.6 on 2024-10-04 16:20

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('es_empresa', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='usuario_groups', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='usuario_user_permissions', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_documento', models.CharField(choices=[('CC', 'Cédula de Ciudadanía'), ('CE', 'Cédula de Extranjería'), ('PASSPORT', 'Pasaporte'), ('PPT', 'Permiso por Protección Temporal')], max_length=50)),
                ('documento_identidad', models.CharField(max_length=100, unique=True)),
                ('numero_telefono', models.CharField(max_length=20)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='empleado', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CuentaBancaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banco', models.CharField(max_length=100)),
                ('tipo_cuenta', models.CharField(choices=[('corriente', 'Corriente'), ('ahorros', 'Ahorros')], max_length=10)),
                ('numero_cuenta', models.CharField(max_length=50)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuentas_bancarias', to='personas.empleado')),
            ],
        ),
        migrations.CreateModel(
            name='EmpleadoEmpresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='empleado_empresa', to='personas.empleado')),
                ('usuario', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='usuario_empresa', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(default='', max_length=255)),
                ('direccion', models.CharField(default='', max_length=255)),
                ('telefono', models.CharField(default='', max_length=20)),
                ('creador', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='empresas_creadas', to=settings.AUTH_USER_MODEL)),
                ('usuarios', models.ManyToManyField(related_name='empresas', through='personas.EmpleadoEmpresa', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='empleadoempresa',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='empresa_empleado', to='personas.empresa'),
        ),
        migrations.CreateModel(
            name='OrdenDePago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_usdt', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cantidad_cop', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personas.empleado')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personas.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='ComprobanteDePago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(upload_to='comprobantes/')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('orden_de_pago', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='personas.ordendepago')),
            ],
        ),
        migrations.CreateModel(
            name='RecargaUSDT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
