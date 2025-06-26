import cv2
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk


class ImageEditor:
    def __init__(self, master):
        self.master = master
        master.title("Редактор изображений")

        self.history = []

        self.image = None
        self.photo = None

        # Buttons
        btn_frame = tk.Frame(master)
        btn_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(btn_frame, text="Загрузить изображение", command=self.load_image).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Сделать фото", command=self.capture_image).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Размытие (Гаусс)", command=self.gaussian_blur).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Оттенки серого", command=self.to_grayscale).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Нарисовать линию", command=self.draw_line).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Показать канал", command=self.show_channel).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Показать изображение", command=self.show_image).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Отменить", command=self.undo_action).pack(side=tk.LEFT)

        self.image_label = tk.Label(master)
        self.image_label.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        try:
            if self.image is not None:
                self.history.append(self.image.copy())
            self.image = cv2.imread(file_path)
            if self.image is None:
                raise ValueError("Ошибка загрузки изображения")
            self.show_image()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def capture_image(self):
        try:
            if self.image is not None:
                self.history.append(self.image.copy())
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise ValueError("Не удалось открыть веб-камеру. Убедитесь, что она подключена и не используется другим приложением.")
            ret, frame = cap.read()
            cap.release()
            if not ret:
                raise ValueError("Не удалось получить изображение с веб-камеры.")
            self.image = frame
            self.show_image()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def gaussian_blur(self):
        if self.image is None:
            messagebox.showwarning("Ошибка", "Изображение не загружено")
            return
        try:
            ksize = simpledialog.askinteger("Размытие по Гауссу", "Размер ядра (нечётное число):", minvalue=1)
            if ksize is None:
                return
            if ksize % 2 == 0:
                messagebox.showerror("Ошибка", "Размер ядра должен быть нечётным числом")
                return
            self.history.append(self.image.copy())
            self.image = cv2.GaussianBlur(self.image, (ksize, ksize), 0)
            self.show_image()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить размытие: {e}")

    def to_grayscale(self):
        if self.image is None:
            messagebox.showwarning("Предупреждение", "Изображение не загружено")
            return
        try:
            self.history.append(self.image.copy())
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.show_image(gray=True)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def draw_line(self):
        if self.image is None:
            messagebox.showwarning("Предупреждение", "Изображение не загружено")
            return
        try:
            x1 = simpledialog.askinteger("Нарисовать линию", "x1:")
            y1 = simpledialog.askinteger("Нарисовать линию", "y1:")
            x2 = simpledialog.askinteger("Нарисовать линию", "x2:")
            y2 = simpledialog.askinteger("Нарисовать линию", "y2:")
            thickness = simpledialog.askinteger("Нарисовать линию", "Толщина:")
            if None in (x1, y1, x2, y2, thickness):
                return
            self.history.append(self.image.copy())
            cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), thickness)
            self.show_image()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_channel(self):
        if self.image is None:
            messagebox.showwarning("Предупреждение", "Изображение не загружено")
            return
        try:
            channel = simpledialog.askstring("Показать канал", "Выберите канал: R, G или B")
            if channel is None:
                return
            channel = channel.strip().upper()
            if channel not in ("R", "G", "B"):
                messagebox.showerror("Ошибка", "Недопустимый канал")
                return
            b, g, r = cv2.split(self.image)
            if channel == "R":
                self.show_image_from_array(r)
            elif channel == "G":
                self.show_image_from_array(g)
            else:
                self.show_image_from_array(b)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_image_from_array(self, array):
        self.history.append(self.image.copy())
        if len(array.shape) == 2:
            img = Image.fromarray(array)
        else:
            img = Image.fromarray(cv2.cvtColor(array, cv2.COLOR_BGR2RGB))
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.photo)
        self.image_label.image = self.photo

    def show_image(self, gray=False):
        if self.image is None:
            return
        if gray:
            img = Image.fromarray(self.image)
        else:
            img = Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.photo)
        self.image_label.image = self.photo

    def undo_action(self):
        if not self.history:
            messagebox.showwarning("Предупреждение", "Нет предыдущего изображения")
            return
        self.image = self.history.pop()
        gray = len(self.image.shape) == 2
        self.show_image(gray=gray)


def main():
    try:
        root = tk.Tk()
    except tk.TclError as e:
        print(f"Не удалось запустить графический интерфейс: {e}\nУбедитесь, что доступен дисплей.")
        return
    ImageEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()