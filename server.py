import tkinter as tk
from tkinter import filedialog, scrolledtext
import json
import os
import threading
from pythonosc import dispatcher, osc_server

class BeatSpaceBridgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BeatSpace Multitouch Bridge")
        # Larghezza raddoppiata a 1000px
        self.root.geometry("1000x650")

        # Variabili GUI
        self.port_var = tk.StringVar(value="9000")
        self.multiplier_var = tk.StringVar(value="999.0")
        self.file_path_var = tk.StringVar(value="latentPoints.json")
        
        # Stato interno: 8 canali [x, y]
        self.points = [[500, 500] for _ in range(8)]
        self.server = None
        self.server_thread = None

        # --- Layout GUI ---
        frame_top = tk.Frame(root, padx=10, pady=10)
        frame_top.pack(fill='x')

        tk.Label(frame_top, text="OSC Port:").grid(row=0, column=0, sticky='w')
        tk.Entry(frame_top, textvariable=self.port_var, width=15).grid(row=0, column=1, padx=5)

        tk.Label(frame_top, text="Multiplier:").grid(row=1, column=0, sticky='w', pady=5)
        tk.Entry(frame_top, textvariable=self.multiplier_var, width=15).grid(row=1, column=1, padx=5)

        tk.Button(frame_top, text="Select JSON File", command=self.browse_file).grid(row=2, column=0, pady=5)
        # Colore cambiato in bianco come richiesto
        tk.Label(frame_top, textvariable=self.file_path_var, fg="white").grid(row=2, column=1, sticky='w')

        # Pulsanti Controllo
        frame_btn = tk.Frame(root, padx=10)
        frame_btn.pack(fill='x', pady=5)
        
        self.btn_start = tk.Button(frame_btn, text="Start Server", command=self.start_server, bg="#aaffaa", height=2)
        self.btn_start.pack(side='left', expand=True, fill='x', padx=5)
        
        self.btn_stop = tk.Button(frame_btn, text="Stop Server", command=self.stop_server, state='disabled', bg="#ffaaaa", height=2)
        self.btn_stop.pack(side='right', expand=True, fill='x', padx=5)

        self.status_label = tk.Label(root, text="Status: Stopped", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=5)

        # Area Log
        tk.Label(root, text="OSC Log:").pack(anchor='w', padx=10)
        self.log_area = scrolledtext.ScrolledText(root, height=20, state='disabled', bg="#111111", fg="#00FF00")
        self.log_area.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def browse_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="latentPoints.json"
        )
        if filename:
            self.file_path_var.set(filename)

    def log_message(self, msg):
        def append():
            self.log_area.config(state='normal')
            self.log_area.insert('end', msg + "\n")
            self.log_area.see('end')
            self.log_area.config(state='disabled')
        self.root.after(0, append)

    def save_json(self):
        """Scrive il file JSON atomicamente."""
        filepath = self.file_path_var.get()
        temp_path = filepath + ".tmp"
        try:
            with open(temp_path, 'w') as f:
                json.dump(self.points, f)
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_path, filepath)
        except Exception as e:
            self.log_message(f"Write error: {e}")

    def handle_multitouch(self, address, *args):
        # Formato atteso: 
        # address: /myMultiTouch
        # args[0]: "touchesByTime"
        # args[1...]: sequenza di [ID, X, Y] ripetuti
        
        if len(args) < 4 or args[0] != "touchesByTime":
            return

        try:
            mult = float(self.multiplier_var.get())
        except ValueError:
            mult = 999.0

        log_str = "Received MultiTouch: "
        updated_indices = []

        i = 1
        while i + 2 < len(args):
            try:
                idx = int(args[i])         # ID dito
                x = float(args[i+1])       # X
                y = float(args[i+2])       # Y

                # Converti ID (1-based) a indice array (0-based)
                array_idx = idx - 1

                if 0 <= array_idx < 8:
                    # Inversione Y (1.0 - y) e moltiplicazione
                    val_x = int(x * mult)
                    val_y = int((1.0 - y) * mult)
                    
                    # Clamp valori
                    self.points[array_idx][0] = max(0, min(999, val_x))
                    self.points[array_idx][1] = max(0, min(999, val_y))
                    
                    updated_indices.append(idx)
                    i += 3
                else:
                    i += 1
            
            except ValueError:
                i += 1
        
        if updated_indices:
            self.log_message(f"{log_str} Updated indices: {updated_indices}")
            self.save_json()

    def default_handler(self, address, *args):
        # Per debug se arrivano messaggi strani
        if address != "/myMultiTouch":
            self.log_message(f"Other OSC: {address} {args}")

    def start_server(self):
        try:
            port = int(self.port_var.get())
            
            disp = dispatcher.Dispatcher()
            disp.map("/myMultiTouch", self.handle_multitouch)
            disp.set_default_handler(self.default_handler)
            
            self.server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", port), disp)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()

            self.status_label.config(text=f"Status: LISTENING on port {port}", fg="green")
            self.log_message(f"--- Server started. Waiting for /myMultiTouch ---")
            self.btn_start.config(state='disabled')
            self.btn_stop.config(state='normal')
            
        except Exception as e:
            self.log_message(f"STARTUP ERROR: {e}")

    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server = None
            self.status_label.config(text="Status: Stopped", fg="black")
            self.log_message("--- Server stopped ---")
            self.btn_start.config(state='normal')
            self.btn_stop.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = BeatSpaceBridgeApp(root)
    root.mainloop()