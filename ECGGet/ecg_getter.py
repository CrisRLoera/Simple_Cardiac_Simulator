import pandas as pd
import numpy as np
import wfdb
import ast
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import customtkinter as ctk
from tkinter import filedialog
import os

class ValveDetectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Detección de válvulas cardíacas")
        self.geometry("600x400")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.sampling_rate = 100
        self.latido = []

        # Cargar datos
        self.path = '/home/crisdev/Escritorio/UACH/9no Semestre/Sim/PA/ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3/'
        self.Y = pd.read_csv(self.path + 'ptbxl_database.csv', index_col='ecg_id')
        self.Y.scp_codes = self.Y.scp_codes.apply(lambda x: ast.literal_eval(x))
        self.X_test = self.load_raw_data(self.Y, self.sampling_rate, self.path)
        #self.X_test = self.X[np.where(self.Y.strat_fold == 1)]

        # Interfaz
        self.create_widgets()

    def create_widgets(self):
        self.sample_label = ctk.CTkLabel(self, text=f"Índice de muestra 0-{len(self.X_test)}:")
        self.sample_label.pack(pady=5)
        self.sample_entry = ctk.CTkEntry(self)
        self.sample_entry.pack(pady=5)

        self.channel_label = ctk.CTkLabel(self, text="Canal (0-11):")
        self.channel_label.pack(pady=5)
        self.channel_entry = ctk.CTkEntry(self)
        self.channel_entry.pack(pady=5)

        self.process_button = ctk.CTkButton(self, text="Procesar latido", command=self.process_beat_gui)
        self.process_button.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=5)

    def load_raw_data(self, df, sampling_rate, path):
        print("Cargando datos de ECG...")
        if sampling_rate == 100:
            data = [wfdb.rdsamp(path + f) for f in df.filename_lr]
        else:
            data = [wfdb.rdsamp(path + f) for f in df.filename_hr]
        data = np.array([signal for signal, meta in data])
        return data

    def process_beat_gui(self):
        try:
            idx = int(self.sample_entry.get())
            ch = int(self.channel_entry.get())
            if idx >= len(self.X_test) or ch > 11 or ch < 0:
                raise ValueError("Índice o canal fuera de rango.")
            self.r_idx, self.t_idx = self.process_beat(idx, ch)
            self.graf_beat(idx, self.r_idx, self.t_idx)
            self.guardar_eventos(idx, self.r_idx, self.t_idx)
            self.status_label.configure(text="Latido procesado, graficado y guardado", text_color="green")
        except Exception as e:
            self.status_label.configure(text=str(e), text_color="red")

    def process_beat(self, idx, channel):
        ecg_signal = self.X_test[idx][:, channel]
        peaks_r, _ = find_peaks(ecg_signal, height=0.5, distance=50)
        if len(peaks_r) == 0:
            raise ValueError("No se detectó ningún pico R.")
        r_peak = peaks_r[0]

        pulse_window = 50
        start = r_peak - pulse_window
        end = r_peak + pulse_window
        self.latido = ecg_signal[start:end]
        r_idx = r_peak - start

        t_search_start = r_idx + 20
        t_search_end = min(r_idx + 100, len(self.latido))
        peaks_t, _ = find_peaks(self.latido[t_search_start:t_search_end], height=0.1)
        t_idx = peaks_t[0] + t_search_start if len(peaks_t) > 0 else None
        return r_idx, t_idx

    def graf_beat(self, idx, r_idx, t_idx):
        tipo_ecg = list(self.Y.iloc[idx].scp_codes.keys())

        plt.figure(figsize=(12, 6))
        plt.plot(self.latido, label=f"ECG canal seleccionado - Tipo: {tipo_ecg}")
        plt.axvline(r_idx, color='red', linestyle='--', label="Cierre Mitral y Tricúspide (S1)")
        plt.axvline(r_idx + 3, color='orange', linestyle='--', label="Apertura Aórtica y Pulmonar")

        if t_idx:
            plt.axvline(t_idx, color='green', linestyle='--', label="Cierre Aórtica (S2)")
            plt.axvline(t_idx + 2, color='darkgreen', linestyle='--', label="Cierre Pulmonar")
            plt.axvline(t_idx + 8, color='blue', linestyle='--', label="Apertura Mitral y Tricúspide")

        plt.title("Latido cardíaco con eventos de las 4 válvulas")
        plt.xlabel("# Muestras")
        plt.ylabel("mV")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if filename:
            plt.savefig(filename)
        plt.show()

    def guardar_eventos(self, idx, r_idx, t_idx):
        tipo_ecg = list(self.Y.iloc[idx].scp_codes.keys())
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Texto", "*.txt"), ("CSV", "*.csv")])
        if not save_path:
            return  # Cancelado

        with open(save_path, 'w') as f:
            f.write(f"Tipo de ECG: {tipo_ecg}\n")
            f.write(f"Índice pico R (S1): {r_idx}\n")
            f.write(f"Apertura Aórtica y Pulmonar: {r_idx + 3}\n")
            if t_idx:
                f.write(f"Índice pico T (S2): {t_idx}\n")
                f.write(f"Cierre Pulmonar: {t_idx + 2}\n")
                f.write(f"Apertura Mitral y Tricúspide: {t_idx + 8}\n")

if __name__ == "__main__":
    app = ValveDetectorApp()
    app.mainloop()
