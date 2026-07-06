import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import User, Category, Course, Lesson

def populate():
    print("Sedang mengisi data otomatis...")
    
    # 1. Buat Users
    inst, _ = User.objects.get_or_create(username='pak_sultan', role='instructor')
    inst.set_password('1234')
    inst.save()

    admin, _ = User.objects.get_or_create(username='admin', role='admin', is_superuser=True, is_staff=True)
    admin.set_password('1234')
    admin.save()

    student, _ = User.objects.get_or_create(username='student', role='student')
    student.set_password('1234')
    student.save()

    # 2. Buat Kategori
    cat1, _ = Category.objects.get_or_create(name='Backend Development')
    cat2, _ = Category.objects.get_or_create(name='Mobile Apps')
    cat3, _ = Category.objects.get_or_create(name='Data Science')

    # 3. Buat 5 Course (Biar N+1 kelihatan jelas)
    titles = [
        ('Belajar Docker Pro', cat1),
        ('Mastering Django', cat1),
        ('Flutter Basic', cat2),
        ('Analisis Data Python', cat3),
        ('Sistem Terdistribusi', cat1),
    ]

    for title, cat in titles:
        c, created = Course.objects.get_or_create(
            title=title, 
            category=cat, 
            instructor=inst,
            defaults={'description': 'Deskripsi kursus otomatis'}
        )
        if created:
            Lesson.objects.create(course=c, title='Pendahuluan', content='Isi materi', order=1)

    print("Data berhasil dimasukkan! Password default semua user: 1234")

if __name__ == "__main__":
    populate()