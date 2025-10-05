import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
import argparse
import math

class DiplomaGenerator:
    def __init__(self, portada_template, contraportada_template, output_dir="diplomas_generados"):
        """
        Inicializa el generador de diplomas
        
        Args:
            portada_template (str): Ruta de la imagen template de la portada
            contraportada_template (str): Ruta de la imagen template de la contraportada
            output_dir (str): Directorio donde se guardarán los diplomas generados
        """
        self.portada_template = portada_template
        self.contraportada_template = contraportada_template
        self.output_dir = output_dir
        
        # Crear directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/png", exist_ok=True)
        os.makedirs(f"{output_dir}/pdf", exist_ok=True)
        
        # ============================================================
        # CONFIGURACIÓN DE FUENTES Y COLORES
        # ============================================================
        
        # CONFIGURACIÓN PARA EL NOMBRE
        self.nombre_config = {
            'size': 95,  # Tamaño de fuente para el nombre
            #'color': (0, 63, 136),  # Color RGB Diplomado IA
            'color': (10, 98, 126),  # Color RGB Diplomado Innovación
            'font_name': 'MeaCulpa-Regular.ttf'  # Nombre del archivo de fuente
        }
        
        # CONFIGURACIÓN PARA EL FOLIO
        self.folio_config = {
            'size': 24,  # Tamaño de fuente para el folio
            'color': (150, 150, 150),  # Color RGB
            'font_name': 'Poppins-Regular.ttf'  # Nombre del archivo de fuente
        }
        
        # CONFIGURACIÓN PARA MÓDULOS Y HORAS (comparten configuración)
        self.modulos_config = {
            'size': 18,  # Tamaño de fuente para módulos y horas
            'color': (64, 64, 64),  # Color RGB (gris oscuro por defecto)
            'font_name': 'Poppins-Regular.ttf'  # Nombre del archivo de fuente
        }
        
        # CONFIGURACIÓN PARA EL TOTAL DE HORAS
        self.total_horas_config = {
            'size': 18,  # Tamaño de fuente para el total de horas
            'color': (0, 0, 0),  # Color RGB (negro por defecto)
            'font_name': 'Poppins-Regular.ttf'  # Nombre del archivo de fuente
        }

        # CONFIGURACIÓN PARA EL PROMEDIO FINAL
        self.promedio_final_config = {
            'size': 18,  # Tamaño de fuente para el promedio final
            'color': (0, 0, 0),  # Color RGB (negro por defecto)
            'font_name': 'Poppins-Regular.ttf'  # Nombre del archivo de fuente
        }
        
        # Cargar las fuentes con las configuraciones
        self.fonts = {
            'nombre': self.get_system_font(self.nombre_config['font_name'], self.nombre_config['size']),
            'folio': self.get_system_font(self.folio_config['font_name'], self.folio_config['size']),
            'modulos': self.get_system_font(self.modulos_config['font_name'], self.modulos_config['size']),
            'total_horas': self.get_system_font(self.total_horas_config['font_name'], self.total_horas_config['size']),
            'promedio_final': self.get_system_font(self.promedio_final_config['font_name'], self.promedio_final_config['size'])
        }
        
    def get_system_font(self, font_name, size):
        """Intenta cargar una fuente del sistema, usa fuente por defecto si falla"""
        try:
            # Rutas comunes de fuentes en diferentes sistemas
            font_paths = [
                f"/System/Library/Fonts/{font_name}",  # macOS
                f"/usr/share/fonts/truetype/dejavu/{font_name}",  # Linux
                f"C:/Windows/Fonts/{font_name}",  # Windows
                font_name  # Intenta cargar directamente
            ]
            
            for path in font_paths:
                try:
                    return ImageFont.truetype(path, size)
                except:
                    continue
            
            # Si no encuentra ninguna fuente, usa la por defecto
            print(f"Advertencia: No se pudo cargar la fuente {font_name}, usando fuente por defecto")
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def set_font_config(self, element, size=None, color=None, font_name=None):
        """
        Método para actualizar la configuración de fuentes programáticamente
        
        Args:
            element (str): 'nombre', 'folio', 'modulos', o 'total_horas'
            size (int): Tamaño de la fuente
            color (tuple): Color RGB como tupla (r, g, b)
            font_name (str): Nombre del archivo de fuente
        """
        configs = {
            'nombre': self.nombre_config,
            'folio': self.folio_config,
            'modulos': self.modulos_config,
            'total_horas': self.total_horas_config,
            'promedio_final': self.promedio_final_config
        }
        
        if element not in configs:
            print(f"Error: Elemento '{element}' no válido")
            return
        
        config = configs[element]
        
        if size is not None:
            config['size'] = size
        if color is not None:
            config['color'] = color
        if font_name is not None:
            config['font_name'] = font_name
        
        # Recargar la fuente con la nueva configuración
        self.fonts[element] = self.get_system_font(config['font_name'], config['size'])
    
    def load_csv_data(self, csv_path):
        """
        Carga los datos del CSV
        
        Formato esperado del CSV (simplificado - solo calificaciones):
        nombre,folio,modulo1_calificacion,modulo2_calificacion,modulo3_calificacion,modulo4_calificacion
        """
        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as e:
            print(f"Error al cargar el archivo CSV: {e}")
            return None
    
    def create_portada(self, nombre, folio, output_path):
        """
        Genera la portada del diploma
        
        Args:
            nombre (str): Nombre del estudiante
            folio (str): Número de folio
            output_path (str): Ruta donde guardar la imagen
        """
        # Abrir imagen template
        img = Image.open(self.portada_template)
        draw = ImageDraw.Draw(img)
        
        # Obtener dimensiones de la imagen
        width, height = img.size
        
        # CONFIGURAR ESTAS POSICIONES SEGÚN TU PLANTILLA DE PORTADA
        # =========================================================
        # Posición Y para el nombre del estudiante (se centra automáticamente en X)
        nombre_pos_y = height // 2 - 295  # Ajustar según tu plantilla
        
        # Posición Y para el folio (se centra automáticamente en X)
        folio_pos_y = height // 2 - 150  # Ajustar según tu plantilla
        
        # Texto del folio - puedes cambiar el formato aquí
        folio_text = f"Folio: {folio}"  # Cambiar formato si es necesario
        
        # Dibujar nombre (centrado horizontalmente) con color personalizado
        nombre_bbox = draw.textbbox((0, 0), nombre, font=self.fonts['nombre'])
        nombre_width = nombre_bbox[2] - nombre_bbox[0]
        nombre_x = (width - nombre_width) // 2
        draw.text((nombre_x, nombre_pos_y), nombre, 
                 fill=self.nombre_config['color'], 
                 font=self.fonts['nombre'])
        
        # Dibujar folio (centrado horizontalmente) con color personalizado
        folio_bbox = draw.textbbox((0, 0), folio_text, font=self.fonts['folio'])
        folio_width = folio_bbox[2] - folio_bbox[0]
        folio_x = (width - folio_width) // 2
        draw.text((folio_x, folio_pos_y), folio_text, 
                 fill=self.folio_config['color'], 
                 font=self.fonts['folio'])
        
        # Guardar imagen
        img.save(output_path)
        print(f"Portada creada: {output_path}")
    
    def create_contraportada(self, datos_estudiante, output_path):
        """
        Genera la contraportada del diploma con 30 horas fijas por módulo
        
        Args:
            datos_estudiante (dict): Diccionario con todos los datos del estudiante
            output_path (str): Ruta donde guardar la imagen
        """
        # Abrir imagen template
        img = Image.open(self.contraportada_template)
        draw = ImageDraw.Draw(img)

        # CONFIGURAR ESTAS POSICIONES SEGÚN TU PLANTILLA
        pos_mod_base = (870, 450)
        incremento = 120

        horas_positions = {f'modulo{i}': (pos_mod_base[0], pos_mod_base[1] + incremento * (i - 1)) for i in range(1, 5)}
        pos_calif_base = (1100, 450)
        calificaciones_positions = {f'modulo{i}': (pos_calif_base[0], pos_calif_base[1] + incremento * (i - 1)) for i in range(1, 5)}

        total_horas_position = (pos_mod_base[0], pos_mod_base[1] + incremento * 4 - 15)
        promedio_final_position = (pos_mod_base[0] + 160, pos_mod_base[1] + incremento * 4 - 15)

        # Procesar módulos con 30 horas fijas
        calificaciones = []
        for i in range(1, 5):
            # Siempre 30 horas por módulo
            horas_val = "30 horas"
            calif_val = datos_estudiante.get(f'modulo{i}_calificacion', '0')
            
            # Dibujar horas (siempre 30)
            draw.text(horas_positions[f'modulo{i}'], horas_val,
                      fill=self.modulos_config['color'], font=self.fonts['modulos'])
            
            # Dibujar calificación
            draw.text(calificaciones_positions[f'modulo{i}'], str(calif_val),
                      fill=self.modulos_config['color'], font=self.fonts['modulos'])
            
            # Agregar calificación a la lista para el promedio
            try:
                calificaciones.append(float(calif_val))
            except ValueError:
                pass

        # Total de horas (4 módulos x 30 horas = 120 horas)
        draw.text(total_horas_position, "120 horas",
                  fill=self.total_horas_config['color'], font=self.fonts['total_horas'])

        # Calcular y dibujar promedio final
        promedio_final = "{:.2f}".format(sum(calificaciones) / len(calificaciones)) if calificaciones else "0.00"
        draw.text(promedio_final_position, f"Promedio Final: {promedio_final}",
                  fill=self.promedio_final_config['color'], font=self.fonts['promedio_final'])

        img.save(output_path)
        print(f"Contraportada creada: {output_path}")
    
    def create_pdf(self, portada_path, contraportada_path, output_pdf_path):
        """
        Convierte las imágenes PNG a un PDF con dos páginas
        
        Args:
            portada_path (str): Ruta de la imagen de la portada
            contraportada_path (str): Ruta de la imagen de la contraportada
            output_pdf_path (str): Ruta donde guardar el PDF
        """
        try:
            from reportlab.lib.utils import ImageReader
            
            c = canvas.Canvas(output_pdf_path, pagesize=A4)
            page_width, page_height = A4
            
            # Agregar portada
            portada_img = ImageReader(portada_path)
            c.drawImage(portada_img, 0, 0, width=page_width, height=page_height, preserveAspectRatio=True)
            c.showPage()
            
            # Agregar contraportada
            contraportada_img = ImageReader(contraportada_path)
            c.drawImage(contraportada_img, 0, 0, width=page_width, height=page_height, preserveAspectRatio=True)
            
            c.save()
            print(f"PDF creado: {output_pdf_path}")
            
        except Exception as e:
            print(f"Error al crear PDF: {e}")
    
    def generate_diplomas(self, csv_path):
        """
        Genera todos los diplomas basados en los datos del CSV
        
        Args:
            csv_path (str): Ruta del archivo CSV con los datos
        """
        # Cargar datos
        df = self.load_csv_data(csv_path)
        if df is None:
            return
        
        print(f"Procesando {len(df)} diplomas...")
        
        for index, row in df.iterrows():
            try:
                # Obtener datos del estudiante
                nombre = row['nombre']
                folio = str(row['folio'])  # Convertir a string por si es numérico
                
                # Crear nombres de archivos
                safe_name = "".join(c for c in nombre if c.isalnum() or c in (' ', '-', '_')).rstrip()
                portada_png = f"{self.output_dir}/png/{safe_name}_portada.png"
                contraportada_png = f"{self.output_dir}/png/{safe_name}_contraportada.png"
                diploma_pdf = f"{self.output_dir}/pdf/{safe_name}_diploma.pdf"
                
                # Generar portada
                self.create_portada(nombre, folio, portada_png)
                
                # Generar contraportada
                self.create_contraportada(row.to_dict(), contraportada_png)
                
                # Generar PDF
                self.create_pdf(portada_png, contraportada_png, diploma_pdf)
                
                print(f"Diploma completado para: {nombre}")
                
            except Exception as e:
                print(f"Error procesando diploma para {row.get('nombre', 'desconocido')}: {e}")
        
        print("¡Proceso completado!")

def main():
    parser = argparse.ArgumentParser(description='Generador de Diplomas Automatizado')
    parser.add_argument('--csv', required=True, help='Ruta del archivo CSV con los datos')
    parser.add_argument('--portada', required=True, help='Ruta del template de portada PNG')
    parser.add_argument('--contraportada', required=True, help='Ruta del template de contraportada PNG')
    parser.add_argument('--output', default='diplomas_generados', help='Directorio de salida')
    
    args = parser.parse_args()
    
    # Verificar que los archivos existan
    if not os.path.exists(args.csv):
        print(f"Error: No se encuentra el archivo CSV: {args.csv}")
        return
    
    if not os.path.exists(args.portada):
        print(f"Error: No se encuentra el template de portada: {args.portada}")
        return
    
    if not os.path.exists(args.contraportada):
        print(f"Error: No se encuentra el template de contraportada: {args.contraportada}")
        return
    
    # Crear generador y procesar diplomas
    generator = DiplomaGenerator(args.portada, args.contraportada, args.output)
    
    # ============================================================
    # EJEMPLO DE PERSONALIZACIÓN DE COLORES Y TAMAÑOS
    # ============================================================
    # Puedes descomentar y modificar estas líneas para personalizar:
    
    # generator.set_font_config('nombre', size=60, color=(0, 0, 255))  # Nombre azul, tamaño 60
    # generator.set_font_config('folio', size=28, color=(255, 0, 0))  # Folio rojo, tamaño 28
    # generator.set_font_config('modulos', size=20, color=(0, 128, 0))  # Módulos verde, tamaño 20
    # generator.set_font_config('total_horas', size=32, color=(128, 0, 128))  # Total púrpura, tamaño 32
    
    generator.generate_diplomas(args.csv)

if __name__ == "__main__":
    main()

"""
============================================================
GUÍA DE USO Y CONFIGURACIÓN
============================================================

FORMATO DEL CSV (SIMPLIFICADO):
===============================
Ahora el CSV solo necesita las calificaciones, ya que las horas son fijas (30 por módulo):

nombre,folio,modulo1_calificacion,modulo2_calificacion,modulo3_calificacion,modulo4_calificacion
Juan Pérez,001,9.5,8.8,9.2,9.0
María García,002,8.7,9.1,8.9,9.3
Carlos López,003,9.2,9.5,8.5,9.8
Ana Martínez,004,8.0,8.5,9.0,8.8

INFORMACIÓN SOBRE LOS MÓDULOS:
==============================
- Cada módulo tiene exactamente 30 horas (fijo)
- Total del diploma: 120 horas (4 módulos x 30 horas)
- Solo se requieren las calificaciones en el CSV
- El promedio final se calcula automáticamente

CONFIGURACIÓN DE COLORES Y TAMAÑOS DE FUENTE:
=============================================

1. NOMBRE DEL ESTUDIANTE:
   self.nombre_config = {
       'size': 95,              # Tamaño de fuente
       'color': (0, 63, 136),   # Color RGB - Azul oscuro
       'font_name': 'MeaCulpa-Regular.ttf'
   }

2. FOLIO:
   self.folio_config = {
       'size': 24,              # Tamaño de fuente
       'color': (150, 150, 150), # Color RGB - Gris
       'font_name': 'Poppins-Regular.ttf'
   }

3. MÓDULOS (HORAS Y CALIFICACIONES):
   self.modulos_config = {
       'size': 18,              # Tamaño de fuente
       'color': (64, 64, 64),   # Color RGB - Gris oscuro
       'font_name': 'Poppins-Regular.ttf'
   }

4. TOTAL DE HORAS:
   self.total_horas_config = {
       'size': 18,              # Tamaño de fuente
       'color': (0, 0, 0),      # Color RGB - Negro
       'font_name': 'Poppins-Regular.ttf'
   }

5. PROMEDIO FINAL:
   self.promedio_final_config = {
       'size': 18,              # Tamaño de fuente
       'color': (0, 0, 0),      # Color RGB - Negro
       'font_name': 'Poppins-Regular.ttf'
   }

EJEMPLOS DE COLORES RGB:
========================
- Negro: (0, 0, 0)
- Blanco: (255, 255, 255)
- Rojo: (255, 0, 0)
- Verde: (0, 255, 0)
- Azul: (0, 0, 255)
- Azul marino: (0, 0, 128)
- Azul oscuro: (0, 63, 136)
- Dorado: (255, 215, 0)
- Plateado: (192, 192, 192)
- Gris: (150, 150, 150)
- Gris oscuro: (64, 64, 64)
- Púrpura: (128, 0, 128)
- Naranja: (255, 165, 0)

INSTALACIÓN DE DEPENDENCIAS:
============================
pip install pillow pandas reportlab

EJECUCIÓN:
=========
python diploma_generator.py --csv Innovacion_diplomas.csv --portada portada_template_innov.png --contraportada contraportada_template_innov.png --output diplomas_generados

USO DESDE OTRO SCRIPT:
=====================
from diploma_generator import DiplomaGenerator

# Crear generador
gen = DiplomaGenerator("portada.png", "contraportada.png")

# Personalizar colores y tamaños (opcional)
gen.set_font_config('nombre', size=72, color=(255, 215, 0))  # Dorado grande
gen.set_font_config('folio', size=24, color=(0, 0, 0))       # Negro pequeño

# Generar diplomas
gen.generate_diplomas("estudiantes.csv")

NOTAS:
======
- Todos los módulos tienen 30 horas fijas
- El total siempre será 120 horas
- Solo se requieren las calificaciones en el CSV
- El promedio se calcula automáticamente con 2 decimales
"""