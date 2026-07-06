import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from courses.models import Course, Section, Lesson

def generate_long_text(title, course_title):
    return f"""
    <h3>Panduan Komprehensif: {title}</h3>
    <p>Selamat datang di sesi pembahasan mendalam mengenai <strong>{title}</strong>. Dalam bagian dari kursus <em>{course_title}</em> ini, kita akan membedah secara rinci konsep-konsep esensial yang tidak hanya akan menambah wawasan teoritis Anda, tetapi juga memberikan landasan praktis yang kuat untuk diterapkan di lingkungan kerja nyata.</p>
    
    <h4>1. Mengapa Topik ini Sangat Krusial?</h4>
    <p>Di era industri modern, pemahaman permukaan saja tidak lagi cukup. Banyak praktisi gagal di tengah jalan karena mereka melewatkan fondasi utama dari konsep ini. Mari kita ambil contoh nyata: ketika sistem dihadapkan pada beban kerja yang tinggi, ketidaktahuan akan struktur dasar dapat menyebabkan keruntuhan arsitektur secara masif. Oleh karena itu, penguasaan materi ini adalah investasi jangka panjang untuk karir Anda.</p>
    
    <div style='background-color: #f8fafc; padding: 15px; border-left: 5px solid #3b82f6; margin: 20px 0;'>
        <strong>Fakta Industri:</strong> Lebih dari 70% masalah teknis skala Enterprise bermula dari pengabaian praktik dasar yang akan kita pelajari pada bab ini.
    </div>

    <h4>2. Penjelasan Konsep Inti (Core Concept)</h4>
    <p>Konsep ini bekerja berdasarkan tiga pilar utama: Kecepatan, Keandalan, dan Skalabilitas. Jika kita bedah lebih jauh, alur kerjanya dimulai dari inisiasi sistem, pemrosesan aliran data, hingga terminasi logika. Sangat disarankan bagi Anda untuk tidak sekadar menghafal, melainkan memahami <em>'mengapa'</em> sebuah keputusan teknis diambil.</p>
    <p>Mari kita lihat contoh penerapan pseudo-code di bawah ini yang menggambarkan logika dasarnya:</p>
    <pre style='background: #1e293b; color: #f8fafc; padding: 15px; border-radius: 8px;'><code>
// Contoh Implementasi Standar
function processData(input) {{
    if (!input) return "Data tidak valid";
    
    // Inisiasi pemrosesan
    let result = sanitize(input);
    result = applyBusinessLogic(result);
    
    return optimize(result);
}}
    </code></pre>
    
    <h4>3. Tantangan dan Kesalahan Umum (Common Pitfalls)</h4>
    <p>Para pemula seringkali melakukan kesalahan dengan melewati tahap pengujian. Mereka berasumsi bahwa jika kode atau desain berjalan satu kali, maka itu sudah sempurna. Padahal, <em>edge cases</em> (kasus ekstrem) selalu bersembunyi di sudut-sudut sistem. Pastikan Anda selalu memvalidasi setiap tahapan kerja yang Anda lakukan.</p>
    
    <h4>4. Ringkasan dan Tindakan Selanjutnya</h4>
    <p>Sebagai kesimpulan, {title} adalah pilar yang menopang keseluruhan keahlian Anda di bidang ini. Setelah menyelesaikan materi ini, pastikan Anda mengambil waktu sejenak untuk mempraktekkan contoh di atas secara mandiri. Cobalah untuk mengubah beberapa variabel dan lihat bagaimana sistem bereaksi.</p>
    <hr style='margin: 30px 0;'/>
    <p><em>Tugas Mandiri: Silakan tuliskan pemahaman Anda di catatan pribadi, dan bersiaplah untuk materi selanjutnya yang akan jauh lebih menantang!</em></p>
    """

def generate_pro_content():
    print("Meningkatkan kualitas konten materi (Text-Only, Sangat Panjang & Profesional)...")
    
    from courses.models import Category
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        
    # Membuat 3 Instruktur
    instructors = []
    for i in range(1, 4):
        inst, created = User.objects.get_or_create(username=f'instruktur{i}', email=f'instruktur{i}@lms.com')
        if created:
            inst.role = 'instructor'
            inst.set_password('instruktur123')
            inst.save()
        instructors.append(inst)

    # Membuat 3 Student
    students = []
    for i in range(1, 4):
        stu, created = User.objects.get_or_create(username=f'student{i}', email=f'student{i}@lms.com')
        if created:
            stu.role = 'student'
            stu.set_password('student123')
            stu.save()
        students.append(stu)

    cat, _ = Category.objects.get_or_create(name="Pemrograman Web", slug="web", description="Kategori Web Development")
    
    Course.objects.get_or_create(slug='html-css', defaults={'title': 'Dasar-Dasar HTML & CSS', 'category': cat, 'instructor': instructors[0], 'difficulty': 'beginner', 'is_published': True})
    Course.objects.get_or_create(slug='django', defaults={'title': 'Backend dengan Python Django', 'category': cat, 'instructor': instructors[1], 'difficulty': 'intermediate', 'is_published': True})
    Course.objects.get_or_create(slug='enterprise', defaults={'title': 'Arsitektur Web Enterprise', 'category': cat, 'instructor': instructors[2], 'difficulty': 'advanced', 'is_published': True})
    Course.objects.get_or_create(slug='js-modern', defaults={'title': 'Penguasaan JavaScript Modern', 'category': cat, 'instructor': instructors[0], 'difficulty': 'intermediate', 'is_published': True})
    Course.objects.get_or_create(slug='devops-web', defaults={'title': 'DevOps untuk Web Developer', 'category': cat, 'instructor': instructors[1], 'difficulty': 'advanced', 'is_published': True})
    
    courses = Course.objects.all()
        
    course_structures = {
        "beginner": [
            {"title": "Bab 1: Pengenalan & Setup Fundamental", "lessons": [
                "1.1 Apa itu dan mengapa ini penting?",
                "1.2 Instalasi & Persiapan Lingkungan Kerja",
                "1.3 Mindset Sukses Seorang Profesional"
            ]},
            {"title": "Bab 2: Konsep Dasar & Sintaks (Core Principles)", "lessons": [
                "2.1 Memahami Struktur Dasar",
                "2.2 Praktik Terbaik (Best Practices)",
                "2.3 Studi Kasus Sederhana",
                "2.4 Evaluasi Pemahaman Bab 2"
            ]},
            {"title": "Bab 3: Implementasi Nyata (Real-world Application)", "lessons": [
                "3.1 Membangun Proyek Pertama Anda",
                "3.2 Debugging & Penyelesaian Masalah Umum",
                "3.3 Review Hasil Proyek"
            ]}
        ],
        "intermediate": [
            {"title": "Bab 1: Review Fundamental & Transisi Menengah", "lessons": [
                "1.1 Mengingat Kembali Konsep Dasar",
                "1.2 Arsitektur Sistem Skala Menengah"
            ]},
            {"title": "Bab 2: Desain Pola & Optimasi Kinerja", "lessons": [
                "2.1 Pengenalan Design Patterns",
                "2.2 Menerapkan DRY & SOLID Principles",
                "2.3 Analisis Kinerja Sistem"
            ]},
            {"title": "Bab 3: Manajemen Proyek & Kolaborasi Tim", "lessons": [
                "3.1 Menggunakan Git & Version Control Lanjutan",
                "3.2 Code Review & Standarisasi",
                "3.3 Integrasi Berkelanjutan (CI/CD) Dasar"
            ]},
            {"title": "Bab 4: Proyek Skala Menengah (Portfolio)", "lessons": [
                "4.1 Blueprint Proyek Akhir",
                "4.2 Live Coding: Pembangunan Fitur Utama",
                "4.3 Refactoring Kode Akhir"
            ]}
        ],
        "advanced": [
            {"title": "Bab 1: Arsitektur Skala Besar (Enterprise Level)", "lessons": [
                "1.1 Microservices vs Monolith",
                "1.2 Skalabilitas Horizontal & Vertikal"
            ]},
            {"title": "Bab 2: Keamanan & Enkripsi Tingkat Lanjut", "lessons": [
                "2.1 Mencegah Serangan OWASP Top 10",
                "2.2 Implementasi OAuth2 & JWT",
                "2.3 Penetration Testing Dasar"
            ]},
            {"title": "Bab 3: Cloud Deployment & DevOps Masterclass", "lessons": [
                "3.1 Docker & Containerization",
                "3.2 Orkestrasi dengan Kubernetes",
                "3.3 Serverless Architecture (AWS Lambda/GCP)"
            ]},
            {"title": "Bab 4: Optimasi Database Lanjutan", "lessons": [
                "4.1 Sharding & Replication",
                "4.2 Caching Strategies (Redis/Memcached)"
            ]},
            {"title": "Bab 5: Ujian Sertifikasi Akhir", "lessons": [
                "5.1 Persiapan Sertifikasi",
                "5.2 Proyek Akhir Enterprise"
            ]}
        ]
    }

    for course in courses:
        Section.objects.filter(course=course).delete()
        
        diff = course.difficulty.lower()
        if diff not in course_structures:
            diff = "intermediate"
            
        structure = course_structures[diff]
        
        for sec_idx, sec_data in enumerate(structure):
            section = Section.objects.create(
                course=course,
                title=sec_data['title'],
                order=sec_idx + 1
            )
            
            for les_idx, title in enumerate(sec_data['lessons']):
                Lesson.objects.create(
                    section=section,
                    title=title,
                    content_format="text",
                    content=generate_long_text(title, course.title),
                    order=les_idx + 1
                )
        print(f"✅ [{course.difficulty.upper()}] Kursus '{course.title}' berhasil diisi dengan materi TEXT panjang ({len(structure)} Bab).")

    print("Selesai! Semua kursus sekarang berfokus murni pada materi bacaan berbobot tinggi.")

if __name__ == "__main__":
    generate_pro_content()
