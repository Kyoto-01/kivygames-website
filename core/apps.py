from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        
        @receiver(post_migrate)
        def create_superuser(sender, **kwargs):
            from django.contrib.auth.models import User
            
            # Só cria se não existir
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='12345678'
                )
                print("✓ Admin criado: admin / 12345678")
