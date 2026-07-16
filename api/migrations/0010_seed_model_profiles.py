from django.db import migrations


def seed_model_profiles(apps, schema_editor):
    ModelProfile = apps.get_model('api', 'ModelProfile')
    ModelPhoto = apps.get_model('api', 'ModelPhoto')

    if ModelProfile.objects.exists():
        return

    seed_data = [
        {
            'name': 'Queen',
            'profile': 'hight 4.4\rbrown eye\rblack beauty \rmy hobbies :Playing tennis',
            'main_image': 'models/main/afr6.avif',
            'photos': [
                'models/main/afr4.webp',
                'models/main/afr5.webp',
            ],
        },
        {
            'name': 'diana',
            'profile': 'hight 4.5\rhobbies : love cooking',
            'main_image': 'models/main/afr4.webp',
            'photos': [
                'models/main/afri7.avif',
            ],
        },
        {
            'name': 'blove',
            'profile': 'height 4.4\ris all about loving me',
            'main_image': 'models/main/afr4.webp',
            'photos': [
                'models/main/afr6.avif',
            ],
        },
        {
            'name': 'Janie',
            'profile': '',
            'main_image': 'models/main/afr5.webp',
            'photos': [
                'models/main/afri8.webp',
            ],
        },
        {
            'name': 'Catrine',
            'profile': '',
            'main_image': 'models/main/afri8.webp',
            'photos': [
                'models/main/afri7.avif',
            ],
        },
        {
            'name': 'afi lee',
            'profile': 'hight 4.4',
            'main_image': 'models/main/afri7.avif',
            'photos': [
                'models/main/afr_6qkBrb7.webp',
            ],
        },
        {
            'name': 'linda',
            'profile': '',
            'main_image': 'models/main/afr_6qkBrb7.webp',
            'photos': [
                'models/main/afr5.webp',
            ],
        },
    ]

    for index, item in enumerate(seed_data, start=1):
        profile = ModelProfile.objects.create(
            name=item['name'],
            profile=item['profile'],
            main_image=item['main_image'],
        )

        for photo_index, photo_path in enumerate(item['photos']):
            ModelPhoto.objects.create(
                model=profile,
                image=photo_path,
                order=(index * 10) + photo_index,
            )


def unseed_model_profiles(apps, schema_editor):
    ModelPhoto = apps.get_model('api', 'ModelPhoto')
    ModelProfile = apps.get_model('api', 'ModelProfile')
    ModelPhoto.objects.all().delete()
    ModelProfile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_contactmessage_main_photo'),
    ]

    operations = [
        migrations.RunPython(seed_model_profiles, unseed_model_profiles),
    ]