import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from PIL import Image, ImageTk
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

# Configuraciones de Azure
ENDPOINT = "https://australiaeast.api.cognitive.microsoft.com/"  # URL base del servicio de Azure Custom Vision
prediction_key = "4754198085de42f09991c4dd092e6eab"  # Clave de predicción de Azure
project_id = "85532228-2138-4ed8-9d42-4a9429e8add4"  # ID del proyecto en Azure Custom Vision
publish_iteration_name = "JardinBotanico"  # Nombre de la iteración publicada

# Crear el cliente de predicción con las credenciales API
credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT, credentials)

# Directorio donde se guardarán las imágenes clasificadas
base_folder_path = os.path.join(os.path.expanduser("~"), "Escritorio", "flores")

def classify_image(image_path):
    """Clasifica una imagen utilizando el modelo de Azure."""
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
    
    results = predictor.classify_image(project_id, publish_iteration_name, image_data)
    
    if results:
        return results
    else:
        messagebox.showerror("Error", "No se pudo clasificar la imagen.")
        return None

def reset_interface():
    """Reinicia la interfaz a su estado original."""
    panel.config(image='')
    result_label.config(text="")
    load_button.pack(pady=30)
    back_button.pack_forget()

def open_image():
    """Abre un diálogo para seleccionar una imagen y la clasifica."""
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        img = Image.open(file_path)
        img.thumbnail((400, 400))
        img = ImageTk.PhotoImage(img)
        panel.config(image=img)
        panel.image = img
        classify_and_save(file_path)
        load_button.pack_forget()
        back_button.pack(pady=30)

def classify_and_save(image_path):
    """Clasifica la imagen y la guarda en la carpeta correspondiente."""
    predictions = classify_image(image_path)
    if predictions:
        best_prediction = max(predictions.predictions, key=lambda x: x.probability)
        
        # Verificar si la imagen es reconocida como una flor
        if best_prediction.probability > 0.5:  # Umbral de confianza
            tag_name = best_prediction.tag_name
            
            folder_path = os.path.join(base_folder_path, tag_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            destination_path = os.path.join(folder_path, os.path.basename(image_path))
            
            try:
                shutil.move(image_path, destination_path)
                result_label.config(text=f"Imagen clasificada como {tag_name} y guardada en {folder_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo mover la imagen: {e}")
        else:
            result_label.config(text="La imagen no parece ser de una flor, Carga una imagen de una flor.")
    else:
        result_label.config(text="No se pudo clasificar la imagen.")

# Crear la ventana principal
root = tk.Tk()
root.title("Clasificación de Imágenes de Flores")
root.attributes('-fullscreen', True)  # Pantalla completa

# Añadir una imagen de fondo
bg_image = Image.open("jardim-botanico039-francisco-correia.jpg")
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), 
                           resample=Image.BILINEAR)
bg_image = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

# Frame para contener los elementos de la interfaz
content_frame = tk.Frame(root, bg='white')
content_frame.place(relx=0.5, rely=0.5, anchor='center')

# Título
title_label = tk.Label(content_frame, text="Jardín Botánico Nacional", 
                       font=("Helvetica", 48, "bold"), fg="#006400", 
                       bg='white')
title_label.pack(pady=40)

# Descripción
description_label = tk.Label(content_frame, 
                             text="Sube una imagen de tu flor y se clasificará automáticamente.",
                             font=("Helvetica", 24), fg="#2E8B57", 
                             bg='white')
description_label.pack(pady=20)

# Panel para mostrar la imagen seleccionada
panel = tk.Label(content_frame, bg="white", width=80, height=30)
panel.pack(pady=20)

# Botón para cargar imagen
load_button = tk.Button(content_frame, text="Cargar Imagen", command=open_image, 
                        font=("Helvetica", 18, "bold"), bg="#4CAF50", fg="white", 
                        padx=20, pady=10)
load_button.pack(pady=30)

# Botón para volver (inicialmente oculto)
back_button = tk.Button(content_frame, text="Volver", command=reset_interface, 
                        font=("Helvetica", 18, "bold"), bg="#4CAF50", fg="white", 
                        padx=20, pady=10)

# Etiqueta para mostrar resultados
result_label = tk.Label(content_frame, text="", font=("Helvetica", 18), 
                        bg="white", justify=tk.LEFT, wraplength=1000)
result_label.pack(pady=20)

# Botón para cerrar la aplicación
close_button = tk.Button(root, text="X", command=root.quit, 
                         font=("Helvetica", 16), bg="red", fg="white")
close_button.place(x=10, y=10)

# Iniciar el loop de la aplicación
root.mainloop()
