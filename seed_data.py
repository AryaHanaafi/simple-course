import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import User, Faculty, StudyProgram, AcademicTerm, Subject, Course, Enrollment, InstructorProfile, StudentProfile

dosen_names = [
    "Dr. Andi Wibowo, S.Kom., M.T.", "Prof. Siti Aminah, Ph.D.", 
    "Budi Santoso, M.Kom.", "Dr. Eng. Rina Yuliana", 
    "Hendra Saputra, S.T., M.Eng.", "Dr. Maya Sari, S.Si., M.Kom.", 
    "Prof. Dr. Agus Salim", "Fajar Nugroho, M.Cs.",
    "Dr. Laila Rahmawati, S.T., M.T.", "Dodi Pratama, M.Kom.",
    "Reni Wijaya, S.Kom., M.Sc.", "Dr. Kurniawan Dwi, M.T.",
    "Bambang Hermanto, Ph.D.", "Sri Mulyani, M.Eng.",
    "Dr. Reza Fahlevi, S.Kom.", "Yudi Setiawan, M.Cs.",
    "Dr. Ir. Wahyu Hidayat", "Ratna Dewi, S.T., M.T.",
    "Prof. Johan Kusuma", "Eka Putri, M.Kom."
]

student_first_names = ["Adi", "Bayu", "Citra", "Dewi", "Eko", "Fitri", "Gilang", "Hana", "Indra", "Joko", "Rina", "Siti", "Budi", "Agus", "Dina", "Rizky", "Putri", "Dicky", "Fajar", "Lestari", "Kevin", "Bintang", "Maulana", "Arya"]
student_last_names = ["Pratama", "Saputra", "Wibowo", "Kusuma", "Santoso", "Setiawan", "Wijaya", "Nugroho", "Sari", "Rahmawati", "Hidayat", "Ramadhan", "Siregar", "Lubis", "Nasution"]

def seed_master_data():
    print("Seeding Master Data...")
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@kampus.ac.id", "1234", role="admin")

    fac_ilkom, _ = Faculty.objects.get_or_create(name="Fakultas Ilmu Komputer")
    fac_ekbis, _ = Faculty.objects.get_or_create(name="Fakultas Ekonomi dan Bisnis")

    prodi_ti, _ = StudyProgram.objects.get_or_create(name="Teknik Informatika", faculty=fac_ilkom)
    prodi_si, _ = StudyProgram.objects.get_or_create(name="Sistem Informasi", faculty=fac_ilkom)
    prodi_mnj, _ = StudyProgram.objects.get_or_create(name="Manajemen", faculty=fac_ekbis)

    term_ganjil, _ = AcademicTerm.objects.get_or_create(name="2026/2027 Ganjil", is_active=True)
    term_genap, _ = AcademicTerm.objects.get_or_create(name="2025/2026 Genap", is_active=False)

    Subject.objects.get_or_create(code="TI101", name="Algoritma dan Pemrograman", credits=3, study_program=prodi_ti)
    Subject.objects.get_or_create(code="TI201", name="Struktur Data", credits=3, study_program=prodi_ti)
    Subject.objects.get_or_create(code="TI301", name="Kecerdasan Buatan", credits=3, study_program=prodi_ti)
    Subject.objects.get_or_create(code="SI101", name="Sistem Basis Data", credits=3, study_program=prodi_si)
    Subject.objects.get_or_create(code="MNJ101", name="Pengantar Manajemen", credits=2, study_program=prodi_mnj)
    
    print("Master data seeded.")

def seed_users():
    print("Seeding Instructors & Students...")
    for i, name in enumerate(dosen_names):
        clean_name = name.split(',')[0].replace('Dr. ', '').replace('Prof. ', '').replace('Eng. ', '').replace('Ir. ', '').strip()
        username = clean_name.lower().replace(' ', '_') + str(i)
        email = f"{username}@kampus.ac.id"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password="password123", email=email, role="instructor", first_name=clean_name)
            InstructorProfile.objects.create(user=user, nidn=username)
    
    base_nim = 1112023000
    for i in range(100):
        first_name = random.choice(student_first_names)
        last_name = random.choice(student_last_names)
        nim = str(base_nim + i + 1)
        username = nim
        email = f"{nim}@student.kampus.ac.id"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password="password123", email=email, role="student", first_name=first_name, last_name=last_name)
            StudentProfile.objects.create(user=user, nim=nim)
    print("Users seeded.")

def seed_classes():
    print("Seeding Parallel Classes...")
    term = AcademicTerm.objects.get(is_active=True)
    instructors = list(User.objects.filter(role="instructor"))
    subjects = list(Subject.objects.all())
    sections = ['A', 'B']

    for subject in subjects:
        for sec in sections:
            inst = random.choice(instructors)
            Course.objects.get_or_create(
                subject=subject,
                term=term,
                section_code=sec,
                instructor=inst,
                description=f"Kelas {sec} untuk mata kuliah {subject.name}.",
                status='published',
                has_rps=random.choice([True, False])
            )
    print("Classes seeded.")

if __name__ == '__main__':
    print("Starting database seeder...")
    seed_master_data()
    seed_users()
    seed_classes()
    print("Seeding complete!")
