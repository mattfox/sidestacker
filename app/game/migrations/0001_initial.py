# Generated by Django 4.2.3 on 2023-07-08 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(default='match making', max_length=20)),
                ('next_player', models.CharField(choices=[('1', 'player 1'), ('2', 'player 2')], default='1', max_length=10)),
                ('winner', models.CharField(blank=True, choices=[('1', 'player 1'), ('2', 'player 2')], max_length=10, null=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='GameMove',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player', models.CharField(choices=[('1', 'player 1'), ('2', 'player 2')], max_length=10)),
                ('x_coord', models.SmallIntegerField()),
                ('y_coord', models.SmallIntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.game')),
            ],
        ),
        migrations.AddConstraint(
            model_name='gamemove',
            constraint=models.UniqueConstraint(fields=('game', 'x_coord', 'y_coord'), name='unique_game_move'),
        ),
    ]
