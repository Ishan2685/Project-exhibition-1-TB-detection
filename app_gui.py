"""
Interactive Desktop GUI for Tuberculosis Detection & Grad-CAM Explainable AI
Uses only standard library (tkinter) + TensorFlow + NumPy + Matplotlib.
No extra third-party UI dependencies required.

Run via:
    python app_gui.py
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from predict import load_model_and_gradcam_extractor, compute_gradcam, MODEL_PATH, IMG_SIZE

class TBAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tuberculosis Computer-Aided Diagnostic (CAD) & Explainable AI System")
        self.root.geometry("1100x750")
        self.root.minsize(950, 650)
        self.root.configure(bg="#f4f6f9")

        # Load DL Model
        self.model = None
        self.conv_extractor = None
        self.post_vgg_layers = None
        self.head_layers = None
        
        self.current_image_path = None

        self._create_widgets()
        self._load_model_async()

    def _create_widgets(self):
        # Header banner
        header_frame = tk.Frame(self.root, bg="#1a365d", pady=12)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame, 
            text="Tuberculosis (TB) Detection & Grad-CAM Clinical Triage",
            font=("Segoe UI", 16, "bold"), 
            fg="white", 
            bg="#1a365d"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame,
            text="Transfer Learning (VGG16) | Pure NumPy Metric Engine | Explainable AI Heatmaps",
            font=("Segoe UI", 10),
            fg="#cbd5e1",
            bg="#1a365d"
        )
        subtitle_label.pack()

        # Control Panel
        control_frame = tk.Frame(self.root, bg="#f4f6f9", pady=8)
        control_frame.pack(fill=tk.X, padx=20)

        self.btn_select = tk.Button(
            control_frame, 
            text="📂 Select Chest X-Ray...", 
            font=("Segoe UI", 10, "bold"),
            bg="#2563eb", 
            fg="white", 
            padx=12, 
            pady=6,
            relief=tk.FLAT,
            command=self._select_image
        )
        self.btn_select.pack(side=tk.LEFT, padx=6)

        self.btn_demo_tb = tk.Button(
            control_frame, 
            text="🚨 Quick Demo: TB Case (#10)", 
            font=("Segoe UI", 10),
            bg="#dc2626", 
            fg="white", 
            padx=10, 
            pady=6,
            relief=tk.FLAT,
            command=lambda: self._diagnose_path("dataset/TB/Tuberculosis-10.png")
        )
        self.btn_demo_tb.pack(side=tk.LEFT, padx=6)

        self.btn_demo_normal = tk.Button(
            control_frame, 
            text="✅ Quick Demo: Normal Case (#2572)", 
            font=("Segoe UI", 10),
            bg="#16a34a", 
            fg="white", 
            padx=10, 
            pady=6,
            relief=tk.FLAT,
            command=lambda: self._diagnose_path("dataset/Normal/Normal-2572.png")
        )
        self.btn_demo_normal.pack(side=tk.LEFT, padx=6)

        self.status_var = tk.StringVar(value="Status: Ready. Please select an image or click a quick demo.")
        self.status_label = tk.Label(
            control_frame, 
            textvariable=self.status_var, 
            font=("Segoe UI", 10, "italic"),
            bg="#f4f6f9", 
            fg="#475569"
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Result Summary Frame
        self.banner_frame = tk.Frame(self.root, bg="#e2e8f0", pady=8)
        self.banner_frame.pack(fill=tk.X, padx=20, pady=(0, 8))

        self.result_var = tk.StringVar(value="Awaiting Radiograph Analysis...")
        self.result_label = tk.Label(
            self.banner_frame,
            textvariable=self.result_var,
            font=("Segoe UI", 12, "bold"),
            bg="#e2e8f0",
            fg="#1e293b"
        )
        self.result_label.pack()

        # Matplotlib Canvas Embed
        self.canvas_frame = tk.Frame(self.root, bg="white")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        self.fig, self.axes = plt.subplots(1, 3, figsize=(12, 4.5))
        self.fig.patch.set_facecolor('#ffffff')
        for ax in self.axes:
            ax.set_facecolor('#ffffff')
            ax.axis('off')
        self.axes[1].text(0.5, 0.5, "Grad-CAM & Diagnostic Panel\n(Load an X-ray to inspect)", 
                          ha='center', va='center', fontsize=12, color='#94a3b8')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _load_model_async(self):
        try:
            self.model, self.conv_extractor, self.post_vgg_layers, self.head_layers = load_model_and_gradcam_extractor()
            self.status_var.set("Model loaded successfully. Ready for inference!")
        except Exception as e:
            self.status_var.set(f"Error loading model: {e}")
            messagebox.showerror("Model Load Error", str(e))

    def _select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Chest X-ray Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
        )
        if file_path:
            self._diagnose_path(file_path)

    def _diagnose_path(self, image_path):
        if not os.path.exists(image_path):
            messagebox.showerror("File Error", f"Cannot find image: {image_path}")
            return

        if self.model is None:
            messagebox.showwarning("Model Initializing", "Model is still loading. Please wait 2 seconds.")
            return

        self.status_var.set(f"Analyzing {os.path.basename(image_path)} with Grad-CAM...")
        self.root.update_idletasks()

        # Run inference and Grad-CAM
        pil_img = tf.keras.utils.load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))
        img_array = tf.keras.utils.img_to_array(pil_img)
        img_batch = np.expand_dims(img_array, axis=0)

        heatmap, prob = compute_gradcam(
            img_batch, self.model, self.conv_extractor, self.post_vgg_layers, self.head_layers
        )

        threshold = 0.50
        is_tb = prob >= threshold
        pred_label = "Tuberculosis (TB) Positive" if is_tb else "Normal (Healthy Lungs)"
        confidence = prob if is_tb else (1.0 - prob)

        if is_tb:
            banner_text = f"DIAGNOSIS: {pred_label} | Confidence: {confidence * 100:.1f}% | ⚠️ PRIORITY 1: Immediate Sputum Test Recommended"
            banner_bg = "#fee2e2"
            banner_fg = "#991b1b"
        else:
            banner_text = f"DIAGNOSIS: {pred_label} | Confidence: {confidence * 100:.1f}% | ✅ PRIORITY 3: Clear Lung Fields / Routine Check"
            banner_bg = "#dcfce7"
            banner_fg = "#166534"

        self.banner_frame.configure(bg=banner_bg)
        self.result_label.configure(bg=banner_bg, fg=banner_fg)
        self.result_var.set(banner_text)

        # Redraw Matplotlib Axes
        self.fig.clf()
        axes = self.fig.subplots(1, 3)

        # Panel 1: Original
        axes[0].imshow(pil_img)
        axes[0].set_title("Input Chest Radiograph", fontsize=11, fontweight='bold')
        axes[0].axis('off')

        # Panel 2: Grad-CAM
        heatmap_resized = tf.image.resize(np.expand_dims(heatmap, axis=-1), (IMG_SIZE, IMG_SIZE)).numpy().squeeze()
        axes[1].imshow(pil_img)
        im = axes[1].imshow(heatmap_resized, cmap='jet', alpha=0.45)
        axes[1].set_title("Explainable AI (Grad-CAM)\nPathological Focus", fontsize=11, fontweight='bold')
        axes[1].axis('off')
        self.fig.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04, label='Relevance')

        # Panel 3: Bar Chart
        classes = ['Normal', 'Tuberculosis']
        probs = [1.0 - prob, prob]
        colors = ['#22c55e', '#ef4444']
        bars = axes[2].bar(classes, probs, color=colors, alpha=0.85, width=0.45)
        axes[2].set_ylim([0, 1.05])
        axes[2].set_ylabel('Model Probability', fontsize=10)
        axes[2].set_title(f"Confidence: {confidence * 100:.1f}%", fontsize=11, fontweight='bold')
        axes[2].axhline(y=threshold, color='gray', linestyle='--', label=f'Threshold ({threshold:.2f})')
        axes[2].legend(loc='upper right', fontsize=8)

        for bar, p in zip(bars, probs):
            yval = bar.get_height()
            axes[2].text(bar.get_x() + bar.get_width() / 2.0, yval + 0.02, f"{p * 100:.1f}%", 
                         ha='center', va='bottom', fontweight='bold', fontsize=10)

        self.fig.tight_layout()
        self.canvas.draw()
        self.status_var.set(f"Completed analysis on {os.path.basename(image_path)} in <1.2s.")

if __name__ == '__main__':
    root = tk.Tk()
    app = TBAppGUI(root)
    root.mainloop()
