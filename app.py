#!/usr/bin/env python

from data_fetcher import QuestionFetcher
from data_fetcher import DataFetcher

class BayesianMBTIApp:
    def __init__(self):
        self.name: str = "guest"
        self.email: str = "guest"
        self.telp: str = ""

        # All 16 possible MBTI types
        self.mbti_types = [
            "ISTJ", "ISFJ", "INFJ", "INTJ",
            "ISTP", "ISFP", "INFP", "INTP",
            "ESTP", "ESFP", "ENFP", "ENTP",
            "ESTJ", "ESFJ", "ENFJ", "ENTJ"
        ]

        # Initialize equal prior probabilities for each type (1/16)
        self.type_probabilities = {}
        for i in range(0, len(self.mbti_types)):
            self.type_probabilities[self.mbti_types[i]] = 1/16
        # self.type_probabilities = {mbti_type: 1/16 for mbti_type in self.mbti_types}

        # Questions with associated trait likelihoods
        qfetch = QuestionFetcher()
        qfetch.parse("./data/question.csv")
        self.questions = qfetch.question

        jfetch = DataFetcher()
        jfetch.read_file("./data/raw_mbti.csv")
        self.job_data = jfetch.data

        # TODO: Will use the POWER OF AI for this.
        self.personality_descriptions = {
            "ISTJ": "ISTJ adalah pribadi yang terstruktur, berorientasi pada detail, dan berpijak pada kenyataan. Fungsi introverted sensing (Si) mereka membuat mereka unggul dalam mengingat data masa lalu dan menerapkan metode yang telah terbukti. Introversi mereka cocok untuk tugas-tugas yang membutuhkan fokus mendalam tanpa gangguan.",
            "ISFJ": "ISFJ menggabungkan empati dengan rasa tanggung jawab yang tinggi. Kombinasi fungsi Si-Fe mereka membuat mereka sangat perhatian terhadap kebutuhan pengguna sekaligus menghargai ketelitian dan tradisi. Introversi mereka membantu mereka menangani masalah kompleks dengan sabar dan hati-hati.",
            "INFJ": "INFJ adalah idealis visioner dengan nilai-nilai internal yang kuat dan pemikiran yang berorientasi pada masa depan (Ni-Fe). Introversi dan introspeksi mereka memungkinkan mereka mengenali pola-pola halus dan membayangkan dampak jangka panjang, menjadikan mereka unik dalam advokasi inovasi etis dan desain yang empatik.",
            "INTJ": "INTJ adalah visioner strategis yang digerakkan oleh wawasan dan logika (Ni-Te). Introversi mereka mendukung jam-jam panjang perencanaan, pembuatan prototipe, dan pekerjaan teoritis yang intens. Mereka sering memimpin melalui kompetensi, bukan karisma, dan unggul dalam lingkungan yang meritokratis.",
            "ISTP": "ISTP adalah pemecah masalah pragmatis yang senang bekerja dengan sistem dunia nyata. Kombinasi Ti-Se mereka membuat mereka unggul dalam menganalisis cara kerja suatu hal. Mereka menyukai kemandirian dan tidak menyukai pengawasan ketat, membuat introversi sangat cocok dengan kebutuhan mereka untuk bereksperimen tanpa gangguan. Ketegangan mereka di bawah tekanan membuat mereka andal dalam tugas operasional yang krusial.",
            "ISFP": "ISFP adalah kreator yang sensitif dan peduli akan keindahan, pengalaman pengguna, dan dampak emosional (Fi-Se). Perasaan introvert mereka memungkinkan mereka mempertimbangkan secara mendalam bagaimana teknologi memengaruhi perasaan pengguna, sementara sensing mereka membantu menciptakan pengalaman yang mendetail dan imersif. Mereka sering lebih suka peran di mana kreativitas mereka berbicara lebih keras daripada kata-kata mereka.",
            "INFP": "INFP adalah idealis imajinatif yang mencari makna dalam pekerjaan mereka (Fi-Ne). Mereka cenderung memilih peran kreatif atau berdampak sosial. Introversi mereka mendukung jam-jam panjang dalam pengkodean proyek solo atau mengeksplorasi masalah abstrak, sementara pola pikir yang digerakkan oleh nilai memastikan pekerjaan mereka selaras dengan misi pribadi atau cerita.",
            "INTP": "INTP adalah penjelajah analitis dengan minat pada sistem teoretis dan pemecahan masalah abstrak (Ti-Ne). Introversi mereka menumbuhkan kecintaan pada kesendirian dan kedalaman intelektual, memungkinkan mereka menyelami ide-ide kompleks tanpa membutuhkan validasi eksternal. Mereka unggul dalam lingkungan yang mendorong inovasi independen.",
            "ESTP": "ESTP adalah realis penuh energi yang senang tantangan nyata yang serba cepat (Se-Ti). Mereka unggul dalam bidang teknik lapangan, penjualan teknologi, atau operasi startup, di mana pemikiran cepat dan tindakan langsung sangat penting. Ekstroversi mereka membantu menjalin hubungan dengan tim dan klien yang beragam, sementara sensing mereka membuat mereka tangkas dalam merespons situasi secara langsung.",
            "ESFP": "ESFP adalah pelaksana yang karismatik yang membawa kehangatan dan spontanitas ke dalam tim (Se-Fi). Ekstroversi mereka membuat mereka ideal sebagai duta platform teknologi, sementara kepekaan mereka membantu memenuhi kebutuhan pengguna secara intuitif. Mereka bersinar ketika teknologi menjadi sarana untuk koneksi dan ekspresi.",
            "ENFP": "ENFP adalah inovator antusias yang digerakkan oleh visi dan potensi manusia (Ne-Fi). Ekstroversi mereka mendukung sesi brainstorming dinamis dan keterlibatan dengan pemangku kepentingan, sementara intuisi mereka melihat koneksi yang sering luput dari orang lain. Mereka menyukai lingkungan berbasis tujuan di mana adaptabilitas dan kreativitas sangat dibutuhkan.",
            "ENTP": "ENTP adalah pemecah masalah yang cerdas dan inventif (Ne-Ti), cocok untuk peran yang melibatkan disrupsi, eksplorasi. Ekstroversi mereka memberi energi dalam diskusi cepat dan kolaborasi multidisipliner, sementara rasa ingin tahu mereka menjaga semangat iterasi. Mereka tidak hanya beradaptasi terhadap perubahan—mereka menciptakannya, menantang norma, dan mengusulkan alternatif radikal dengan logika dan pesona.",
            "ESTJ": "ESTJ adalah pengatur alami yang unggul dalam efisiensi, struktur, dan ketegasan (Te-Si). Ekstroversi mereka menjadikan mereka komunikator tegas dan pengambil keputusan yang andal, sementara sensing mereka membantu menegakkan metode yang praktis dan telah teruji. Mereka membawa keteraturan dalam kekacauan dan memastikan standar dipenuhi secara konsisten.",
            "ESFJ": "ESFJ adalah koordinator yang peduli dan mengutamakan harmoni serta tanggung jawab (Fe-Si). Ekstroversi mereka mendukung pembangunan tim dan pendekatan proaktif, sementara sensing mereka memastikan tidak ada detail yang terlewat. Mereka unggul dalam menerjemahkan kompleksitas teknis menjadi solusi yang mudah didekati (end-user).",
            "ENFJ": "ENFJ adalah mentor inspiratif yang membimbing orang lain dengan visi dan kepedulian (Fe-Ni). Ekstroversi mereka memungkinkan mereka memotivasi dan menyatukan tim, sementara intuisi mereka membantu mengantisipasi kebutuhan jangka panjang pengguna dan tim. Mereka melihat teknologi sebagai alat untuk mengangkat manusia dan ide, bukan sekadar memecahkan masalah.",
            "ENTJ": "ENTJ adalah ahli strategi yang tegas dan unggul dalam kepemimpinan serta perencanaan jangka panjang (Te-Ni). Ekstroversi mereka memungkinkan mereka menggerakkan tim dan pemangku kepentingan, sementara intuisi mereka mendorong inovasi. Mereka lebih menyukai lingkungan yang menghargai ambisi, berpikir sistemik, dan hasil nyata, seringkali naik ke puncak struktur teknologi secara alami."
        }

    def set_email(self, email:str):
        self.email = email

    def set_name(self, name:str):
        self.name = name

    def set_telp(self, telp: str):
        self.telp = telp

    def reset(self):
        for mbti_type in self.mbti_types:
            self.type_probabilities[mbti_type] = 1/16
