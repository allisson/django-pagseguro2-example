import apps.tickets.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=apps.tickets.models.generate_code, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('closed', models.BooleanField(db_index=True, default=False, verbose_name='carrinho finalizado')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to=settings.AUTH_USER_MODEL, verbose_name='usuário')),
            ],
            options={
                'verbose_name': 'carrinho de compra',
                'verbose_name_plural': 'carrinhos de compra',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.UUIDField(default=apps.tickets.models.generate_code, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('quantity', models.SmallIntegerField(default=1, verbose_name='quantidade')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='preço unitário')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='tickets.Cart', verbose_name='carrinho')),
            ],
            options={
                'verbose_name': 'item do carrinho de compra',
                'verbose_name_plural': 'itens do carrinho de compra',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.UUIDField(default=apps.tickets.models.generate_code, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=128, verbose_name='título')),
                ('description', models.TextField(verbose_name='descrição')),
            ],
            options={
                'verbose_name': 'evento',
                'verbose_name_plural': 'eventos',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.UUIDField(default=apps.tickets.models.generate_code, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='preço')),
                ('status', models.CharField(choices=[('pending', 'Pendente'), ('paid', 'Pago'), ('canceled', 'Cancelado')], default='pending', max_length=16, verbose_name='status da compra')),
                ('pagseguro_redirect_url', models.URLField(blank=True, max_length=255, verbose_name='url do pagseguro')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='tickets.Cart', verbose_name='carrinho')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to=settings.AUTH_USER_MODEL, verbose_name='usuário')),
            ],
            options={
                'verbose_name': 'compra',
                'verbose_name_plural': 'compras',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.UUIDField(default=apps.tickets.models.generate_code, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=128, verbose_name='título')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='preço')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='tickets.Event', verbose_name='evento')),
            ],
            options={
                'verbose_name': 'ticket',
                'verbose_name_plural': 'tickets',
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='cartitem',
            name='ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='tickets.Ticket', verbose_name='ticket'),
        ),
    ]
