# -*- coding: utf-8 -*-
import cv2
import numpy as np
from deepface import DeepFace
import time
import random
import threading
import queue
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageFont, ImageDraw
import sys
import os


class NeoFlexEmotionGame:
    def __init__(self, root):
        self.root = root
        self.root.title("NeoFlex Emotion AI")
        self.root.geometry("1200x800")

        # Настройка кодировки для Windows
        if sys.platform == 'win32':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleCP(65001)
                kernel32.SetConsoleOutputCP(65001)
            except:
                pass

        # Цветовая палитра Neoflex
        self.COLORS = {
            'primary': '#00305E',
            'secondary': '#005C97',
            'accent': '#FF6B35',
            'background': '#F5F7FA',
            'text': '#2D3436'
        }

        # Шрифты с поддержкой кириллицы
        self.FONTS = {
            'h1': ('Arial', 24, 'bold'),
            'h2': ('Arial', 18),
            'body': ('Arial', 12),
            'button': ('Arial', 14, 'bold')
        }

        # Инициализация параметров
        self.emotions_list = ['злость', 'страх', 'радость', 'грусть', 'удивление', 'нейтральность']
        self.emotion_translations = {
            'angry': 'злость',
            'fear': 'страх',
            'happy': 'радость',
            'sad': 'грусть',
            'surprise': 'удивление',
            'neutral': 'нейтральность'
        }

        self.cap = cv2.VideoCapture(0)
        self._stop_event = threading.Event()
        self.current_emotion = None
        self.game_active = False
        self.target_emotion = None
        self.face_region = None
        self.frame_queue = queue.Queue(maxsize=1)
        self.emotion_labels = {}

        # Параметры режима дуэли
        self.player_scores = [0, 0]
        self.current_player = 0
        self.round_number = 1
        self.duel_emotions = []
        self.duel_rounds = 3

        # Параметры квеста
        self.quest_stage = 0
        self.quest_scenes = {
            0: {
                'text': "Вы стоите перед закрытой дверью секретной лаборатории NeoFlex.\n"
                        "Охранник с подозрением смотрит на вас. Какой эмоцией вы попытаетесь его убедить?",
                'emotions': {
                    'злость': 1,
                    'радость': 2,
                    'удивление': 3,
                    'нейтральность': 4
                },
                'image': 'lab_door.jpg'
            },
            1: {
                'text': "Охранник нахмурился и достал электрошокер!\n"
                        "Ваша агрессия только ухудшила ситуацию. Как теперь успокоить охранника?",
                'emotions': {
                    'грусть': 5,
                    'страх': 6,
                    'нейтральность': 7
                },
                'image': 'angry_guard.jpg'
            },
            2: {
                'text': "Ваша искренняя улыбка растопила лед! Охранник пропускает вас.\n"
                        "Внутри темно - выразите страх чтобы включить аварийное освещение.",
                'emotions': {
                    'страх': 8,
                    'удивление': 9
                },
                'image': 'happy_guard.jpg'
            },
            3: {
                'text': "Вы сделали удивленные глаза - охранник решил, что вы потерянный новичок\n"
                        "и ведет вас к начальнику охраны. Как вы отреагируете?",
                'emotions': {
                    'радость': 10,
                    'страх': 11,
                    'нейтральность': 12
                },
                'image': 'security_chief.jpg'
            },
            4: {
                'text': "Ваша нейтральность убедила охранника, что вы техник по обслуживанию.\n"
                        "Он пропускает вас. В коридоре сработала сигнализация! Как реагируем?",
                'emotions': {
                    'страх': 13,
                    'удивление': 14
                },
                'image': 'alarm.jpg'
            },
            5: {
                'text': "Вы показали грусть - охранник смягчился и решил вас выслушать.\n"
                        "Теперь убедите его, что вам действительно нужно внутрь!",
                'emotions': {
                    'радость': 15,
                    'нейтральность': 16
                },
                'image': 'listening_guard.jpg'
            },
            6: {
                'text': "Вы испугались - охранник решил, что вы заблудившийся сотрудник.\n"
                        "Он ведет вас к выходу. Попробуйте изменить ситуацию!",
                'emotions': {
                    'радость': 17,
                    'удивление': 18
                },
                'image': 'exit.jpg'
            },
            7: {
                'text': "Вы сохранили спокойствие - охранник потерял к вам интерес.\n"
                        "Теперь нужно незаметно проникнуть в серверную. Какое выражение лица сделаем?",
                'emotions': {
                    'нейтральность': 19,
                    'страх': 20
                },
                'image': 'server_room.jpg'
            },
            8: {
                'text': "Свет включился! Перед вами три двери с символами.\n"
                        "Выберите эмоцию для выбора пути:",
                'emotions': {
                    'радость': 21,
                    'грусть': 22,
                    'удивление': 23
                },
                'image': 'three_doors.jpg'
            },
            9: {
                'text': "Вы выглядели удивленными - охранник решил проверить вашу карту доступа.\n"
                        "Нужно срочно придумать оправдание!",
                'emotions': {
                    'радость': 24,
                    'грусть': 25
                },
                'image': 'access_card.jpg'
            },
            21: {
                'text': "Вы выбрали дверь с солнцем - путь оптимизма!\n"
                        "Внутри яркий свет и панель с кнопками. Какую эмоцию покажем?",
                'emotions': {
                    'радость': 26,
                    'удивление': 27
                },
                'image': 'sunny_path.jpg'
            },
            22: {
                'text': "Вы выбрали дверь с тучей - путь реализма.\n"
                        "Внутри лаборатория с хмурыми учеными. Ваши действия?",
                'emotions': {
                    'нейтральность': 28,
                    'грусть': 29
                },
                'image': 'lab.jpg'
            },
            23: {
                'text': "Вы выбрали дверь с молнией - путь неожиданностей!\n"
                        "Внутри мигающие экраны и робот-охранник. Как реагируем?",
                'emotions': {
                    'удивление': 30,
                    'страх': 31
                },
                'image': 'robot_guard.jpg'
            },
            26: {
                'text': "Ваша радость активировала дружелюбный ИИ!\n"
                        "Он предлагает доступ к секретным данным. Как ответим?",
                'emotions': {
                    'радость': 32,
                    'удивление': 33
                },
                'image': 'friendly_ai.jpg'
            },
            32: {
                'text': "ПОЗДРАВЛЯЕМ! Вы успешно завершили квест!\n"
                        "ИИ передал вам секретные данные NeoFlex и даже предложил работу!",
                'emotions': {},
                'image': 'success.jpg',
                'final': True
            },
            28: {
                'text': "Ваша нейтральность убедила ученых, что вы проверяющий.\n"
                        "Они показывают вам секретный проект. Ваша реакция?",
                'emotions': {
                    'удивление': 34,
                    'нейтральность': 35
                },
                'image': 'secret_project.jpg'
            },
            35: {
                'text': "ПОЗДРАВЛЯЕМ! Вы сохранили хладнокровие и получили\n"
                        "доступ ко всем данным проекта! Миссия выполнена!",
                'emotions': {},
                'image': 'success2.jpg',
                'final': True
            },
            30: {
                'text': "Робот сканирует ваше лицо! Ваше удивление его сбило с толку.\n"
                        "Он просит подтвердить личность. Как ответим?",
                'emotions': {
                    'радость': 36,
                    'страх': 37
                },
                'image': 'robot_scan.jpg'
            },
            36: {
                'text': "ПОЗДРАВЛЯЕМ! Ваша позитивная реакция взломала\n"
                        "систему защиты! Робот теперь под вашим контролем!",
                'emotions': {},
                'image': 'robot_friend.jpg',
                'final': True
            },
            37: {
                'text': "К сожалению, ваш страх активировал систему защиты.\n"
                        "Миссия провалена! Попробуйте еще раз!",
                'emotions': {},
                'image': 'failure.jpg',
                'final': True
            },
            33: {
                'text': "ИИ счел ваше удивление подозрительным и заблокировал доступ.\n"
                        "Миссия провалена! Попробуйте другой подход!",
                'emotions': {},
                'image': 'ai_blocked.jpg',
                'final': True
            }
        }
        self.quest_window = None
        self.quest_image_label = None
        self.quest_text_label = None
        self.quest_timer_label = None

        # Настройка стилей
        self.setup_styles()
        self.setup_gui()

        # Запуск потоков
        self.camera_thread = threading.Thread(target=self._camera_loop)
        self.camera_thread.start()
        self.root.after(10, self.update_frame)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Настройка цветов
        style.configure('TFrame', background=self.COLORS['background'])
        style.configure('TLabel',
                        background=self.COLORS['background'],
                        foreground=self.COLORS['text'],
                        font=self.FONTS['body'])

        style.configure('Neo.TButton',
                        font=self.FONTS['button'],
                        foreground='white',
                        background=self.COLORS['primary'],
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor=self.COLORS['secondary'])

        style.map('Neo.TButton',
                  background=[('active', self.COLORS['secondary']),
                              ('disabled', '#CCCCCC')])

        style.configure('Neo.TRadiobutton',
                        font=self.FONTS['body'],
                        foreground=self.COLORS['text'],
                        background=self.COLORS['background'])

        style.configure('Header.TLabel',
                        font=self.FONTS['h1'],
                        foreground=self.COLORS['primary'])

    def setup_gui(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(header_frame,
                  text="NeoFlex Emotion AI",
                  style='Header.TLabel').pack(side=tk.LEFT)

        # Основное содержимое
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Панель видео
        video_frame = ttk.Frame(content_frame, width=800)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.video_label = ttk.Label(video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Панель списка эмоций
        self.emotion_panel = ttk.Frame(video_frame)
        self.emotion_panel.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Создание индикаторов эмоций
        for emotion in self.emotions_list:
            frame = ttk.Frame(self.emotion_panel)
            frame.pack(side=tk.LEFT, padx=5)

            label = ttk.Label(frame, text=emotion.upper(),
                              font=self.FONTS['body'],
                              foreground=self.COLORS['text'])
            label.pack(side=tk.LEFT)

            indicator = ttk.Label(frame, width=3, background='white',
                                  relief='solid')
            indicator.pack(side=tk.LEFT, padx=2)

            self.emotion_labels[emotion] = indicator

        # Панель управления
        control_frame = ttk.Frame(content_frame, width=300)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        ttk.Label(control_frame,
                  text="Режимы анализа",
                  font=self.FONTS['h2']).pack(pady=20)

        # Радиокнопки выбора режима
        self.mode_var = tk.StringVar()
        modes = [
            ("Максимум эмоций (30 сек)", "max"),
            ("Имитация эмоций", "random"),
            ("Удержание эмоции", "hold"),
            ("Дуэль эмоций (2 игрока)", "duel"),
            ("Эмоциональный квест", "quest")
        ]

        for text, mode in modes:
            rb = ttk.Radiobutton(control_frame,
                                 text=text,
                                 variable=self.mode_var,
                                 value=mode,
                                 style='Neo.TRadiobutton')
            rb.pack(anchor=tk.W, pady=8, padx=10)

        # Кнопки управления
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame,
                   text="Начать анализ",
                   style='Neo.TButton',
                   command=self.start_game).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                   text="Выход",
                   style='Neo.TButton',
                   command=self.stop).pack(side=tk.RIGHT, padx=5)

        # Статусная панель
        self.status_var = tk.StringVar()
        status_frame = ttk.Frame(main_frame, height=40)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(status_frame,
                  textvariable=self.status_var,
                  background=self.COLORS['primary'],
                  foreground='white',
                  anchor=tk.CENTER,
                  font=self.FONTS['body']).pack(fill=tk.BOTH, expand=True)

    def _camera_loop(self):
        while not self._stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret: continue

            processed_frame = self.process_frame(frame)

            try:
                self.frame_queue.put_nowait(processed_frame)
            except queue.Full:
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
                self.frame_queue.put_nowait(processed_frame)

    def process_frame(self, frame):
        # Конвертируем BGR в RGB сразу после получения кадра
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        original_height, original_width = frame_rgb.shape[:2]
        small_frame = cv2.resize(frame_rgb, (0, 0), fx=0.5, fy=0.5)

        try:
            # Для анализа DeepFace конвертируем обратно в BGR
            result = DeepFace.analyze(
                cv2.cvtColor(small_frame, cv2.COLOR_RGB2BGR),
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='ssd',
                silent=True
            )

            analysis = result[0] if isinstance(result, list) else result
            english_emotion = analysis['dominant_emotion']
            self.current_emotion = self.emotion_translations.get(english_emotion, 'неизвестно')
            region = analysis['region']

            scale_x = original_width / small_frame.shape[1]
            scale_y = original_height / small_frame.shape[0]

            self.face_region = (
                int(region['x'] * scale_x),
                int(region['y'] * scale_y),
                int(region['w'] * scale_x),
                int(region['h'] * scale_y)
            )

        except Exception as e:
            self.current_emotion = None
            self.face_region = None

        # Работаем с RGB изображением для рисования
        pil_img = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(pil_img)

        # Пытаемся загрузить шрифт, если не получается - используем стандартный
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 24)
            except:
                font = ImageFont.load_default()

        if self.face_region:
            x, y, w, h = self.face_region
            draw.rectangle([(x, y), (x + w, y + h)],
                           outline=self.hex_to_rgb(self.COLORS['accent']),
                           width=2)

        if self.game_active and self.target_emotion:
            draw.text((20, frame.shape[0] - 40),
                      f"Цель: {self.target_emotion.upper()}",
                      font=font,
                      fill=self.hex_to_rgb(self.COLORS['primary']))

        text = self.current_emotion or "Лицо не обнаружено"
        draw.text((20, 60),
                  f"Текущая: {text.upper()}",
                  font=font,
                  fill=self.hex_to_rgb(self.COLORS['secondary']))

        if self.game_active and self.mode_var.get() == "duel":
            draw.text((frame.shape[1] - 200, 60),
                      f"Игрок {self.current_player + 1}",
                      font=font,
                      fill=self.hex_to_rgb(self.COLORS['accent']))

            draw.text((frame.shape[1] - 250, 100),
                      f"Счет: {self.player_scores[0]} - {self.player_scores[1]}",
                      font=font,
                      fill=self.hex_to_rgb(self.COLORS['secondary']))

            draw.text((frame.shape[1] - 200, 140),
                      f"Раунд {self.round_number}/3",
                      font=font,
                      fill=self.hex_to_rgb(self.COLORS['primary']))

        # Конвертируем обратно в BGR перед возвращением кадра
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def update_frame(self):
        try:
            frame = self.frame_queue.get_nowait()
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        except queue.Empty:
            pass
        finally:
            self.root.after(15, self.update_frame)

    def start_game(self):
        mode = self.mode_var.get()
        if not mode:
            self.status_var.set("Сначала выберите режим!")
            return

        # Остановка предыдущей игры
        self.game_active = False
        time.sleep(0.1)  # Даем время для остановки предыдущего потока

        self.game_active = True
        self.target_emotion = None
        self.player_scores = [0, 0]
        self.current_player = 0
        self.round_number = 1
        self.quest_stage = 0

        if mode == "max":
            threading.Thread(target=self.mode_max_emotions).start()
        elif mode == "random":
            threading.Thread(target=self.mode_random_emotions).start()
        elif mode == "hold":
            self.show_emotion_selection()
        elif mode == "duel":
            threading.Thread(target=self.mode_duel).start()
        elif mode == "quest":
            self.start_emotion_quest()

    def show_emotion_selection(self):
        selection_win = tk.Toplevel(self.root)
        selection_win.title("Выбор эмоции")
        selection_win.geometry("300x400")

        ttk.Label(selection_win,
                  text="Выберите эмоцию для удержания:",
                  font=self.FONTS['h2']).pack(pady=10)

        for emotion in self.emotions_list:
            btn = ttk.Button(selection_win,
                             text=emotion.upper(),
                             style='Neo.TButton',
                             command=lambda e=emotion: self.start_hold_mode(e, selection_win))
            btn.pack(pady=5, fill=tk.X, padx=20)

    def start_hold_mode(self, emotion, win):
        win.destroy()
        self.target_emotion = emotion
        threading.Thread(target=self.mode_hold_emotion).start()

    def update_emotion_indicator(self, emotion, active=True):
        """Обновление индикатора эмоции"""
        color = self.COLORS['accent'] if active else 'white'
        self.emotion_labels[emotion].configure(background=color)

    def mode_max_emotions(self):
        self.target_emotion = "Показывайте разные эмоции!"
        start_time = time.time()
        emotions = set()

        for emotion in self.emotions_list:
            self.root.after(0, self.update_emotion_indicator, emotion, False)

        while (time.time() - start_time) < 30 and self.game_active:
            if self.current_emotion in self.emotions_list:
                if self.current_emotion not in emotions:
                    emotions.add(self.current_emotion)
                    self.root.after(0, self.update_emotion_indicator,
                                    self.current_emotion, True)

            remaining = int(30 - (time.time() - start_time))
            self.status_var.set(f"Осталось: {remaining} сек | Уникальных эмоций: {len(emotions)}")
            time.sleep(0.1)

        self.game_active = False
        self.status_var.set(f"Игра окончена! Показано {len(emotions)} различных эмоций!")

    def mode_random_emotions(self):
        self.target_emotion = random.choice(self.emotions_list)
        correct = 0

        for _ in range(3):
            self.status_var.set(f"Покажите: {self.target_emotion.upper()}!")
            start_time = time.time()

            while (time.time() - start_time) < 10 and self.game_active:
                if self.current_emotion == self.target_emotion:
                    correct += 1
                    self.target_emotion = random.choice(self.emotions_list)
                    break
                time.sleep(0.1)

        self.game_active = False
        self.status_var.set(f"Правильных ответов: {correct} из 3")

    def mode_hold_emotion(self):
        for i in range(3, 0, -1):
            if not self.game_active:
                return
            self.status_var.set(f"Приготовьтесь... {i}")
            time.sleep(1)

        start_time = time.time()
        max_duration = 0
        self.status_var.set("Начали! Держите эмоцию!")

        while self.game_active:
            if self.current_emotion != self.target_emotion:
                break

            current_time = time.time()
            duration = current_time - start_time
            max_duration = max(max_duration, duration)

            self.status_var.set(f"Удержано: {duration:.1f} сек | Рекорд: {max_duration:.1f} сек")
            time.sleep(0.1)

        self.game_active = False
        self.status_var.set(f"Финальный результат: {max_duration:.1f} секунд!")

    def mode_duel(self):
        self.duel_emotions = random.sample(self.emotions_list, 3)
        self.status_var.set("Дуэль начинается! Приготовьтесь!")
        time.sleep(2)

        for i, emotion in enumerate(self.duel_emotions, 1):
            if not self.game_active:
                break

            self.round_number = i
            for player in [0, 1]:
                if not self.game_active:
                    break

                self.current_player = player
                self.status_var.set(f"Раунд {i} | Игрок {player + 1} | Покажите: {emotion.upper()}!")
                start_time = time.time()
                success = False

                while (time.time() - start_time) < 10 and self.game_active:
                    if self.current_emotion == emotion:
                        self.player_scores[player] += 1
                        success = True
                        break
                    time.sleep(0.1)

                feedback = "Успешно!" if success else "Время вышло!"
                self.status_var.set(f"Игрок {player + 1}: {feedback}")
                time.sleep(2 if success else 1)

        winner = "Ничья!"
        if self.player_scores[0] > self.player_scores[1]:
            winner = "Победил Игрок 1!"
        elif self.player_scores[1] > self.player_scores[0]:
            winner = "Победил Игрок 2!"

        self.status_var.set(f"Дуэль завершена! {winner} Счет: {self.player_scores[0]} - {self.player_scores[1]}")
        self.game_active = False

    def show_quest_scene(self):
        # Закрываем предыдущее окно квеста
        if self.quest_window:
            self.quest_window.destroy()

        # Создаем новое окно квеста
        self.quest_window = tk.Toplevel(self.root)
        self.quest_window.title("Эмоциональный квест")
        self.quest_window.geometry("600x500")
        self.quest_window.transient(self.root)
        self.quest_window.grab_set()

        scene = self.quest_scenes.get(self.quest_stage, None)
        if not scene:
            return

        # Текст сцены
        self.quest_text_label = ttk.Label(
            self.quest_window,
            text=scene['text'],
            font=self.FONTS['h2'],
            wraplength=550,
            background=self.COLORS['primary'],
            foreground='white',
            padding=20
        )
        self.quest_text_label.pack(pady=20, fill=tk.X)

        # Изображение сцены
        try:
            img = Image.open(scene['image'])
            img = img.resize((400, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.quest_image_label = ttk.Label(self.quest_window, image=photo)
            self.quest_image_label.image = photo
            self.quest_image_label.pack()
        except Exception as e:
            print(f"Ошибка загрузки изображения: {str(e)}")

        # Добавляем сообщение о необходимости показать эмоцию
        self.quest_timer_label = ttk.Label(
            self.quest_window,
            text="Подготовьтесь... Анализ эмоций начнется через 3 секунды",
            font=self.FONTS['h2'],
            foreground=self.COLORS['accent'],
            padding=10
        )
        self.quest_timer_label.pack(pady=10)

    def start_emotion_quest(self):
        self.game_active = True
        self.quest_stage = 0
        self.show_quest_scene()
        threading.Thread(target=self.quest_logic).start()

    def quest_logic(self):
        while self.game_active and self.quest_stage in self.quest_scenes:
            current_scene = self.quest_scenes[self.quest_stage]
            required_emotions = current_scene['emotions'].keys()

            # Показываем сцену
            self.root.after(0, self.show_quest_scene)

            # Даем 3 секунды на чтение сцены перед началом анализа
            time.sleep(3)

            # Обновляем сообщение о начале анализа
            self.root.after(0, lambda: self.quest_timer_label.config(
                text="Покажите нужную эмоцию! У вас есть 10 секунд",
                foreground=self.COLORS['accent']
            ))

            # Даем 10 секунд на реакцию
            start_time = time.time()
            reaction_time = 10
            success = False

            while (time.time() - start_time) < reaction_time and self.game_active:
                if self.current_emotion in required_emotions:
                    next_stage = current_scene['emotions'][self.current_emotion]
                    self.quest_stage = next_stage
                    success = True
                    break

                # Обновляем оставшееся время
                remaining = int(reaction_time - (time.time() - start_time))
                self.root.after(0, lambda r=remaining: self.quest_timer_label.config(
                    text=f"Осталось времени: {r} сек",
                    foreground='red' if r < 5 else self.COLORS['accent']
                ))
                time.sleep(0.1)

            if success:
                if current_scene.get('final', False):
                    self.root.after(0, lambda: self.status_var.set(
                        "Квест завершен! Нажмите 'Начать анализ' для повторения."))
                    self.game_active = False
                    break
                else:
                    self.root.after(0, lambda: self.status_var.set("Успешно! Переход к следующей сцене..."))
                    time.sleep(2)  # Пауза перед следующей сценой
            else:
                self.root.after(0, lambda: self.status_var.set(
                    f"Время вышло! Попробуйте еще раз с начала квеста."
                ))
                self.quest_stage = 0  # Начинаем заново
                time.sleep(3)

        if not current_scene.get('final', False):
            self.game_active = False
            if self.quest_window:
                self.quest_window.destroy()
            self.status_var.set("Квест завершен! Спасибо за игру!")

    def stop(self):
        self._stop_event.set()
        self.cap.release()
        if self.quest_window:
            self.quest_window.destroy()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = NeoFlexEmotionGame(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()