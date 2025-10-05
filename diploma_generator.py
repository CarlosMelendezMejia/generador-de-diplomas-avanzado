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
            'size': 95,
            'color': (10, 98, 126),
            'font_name': 'MeaCulpa-Regular.ttf'
        }
        
        # CONFIGURACIÓN PARA EL FOLIO
        self.folio_config = {
            'size': 24,
            'color': (150, 150, 150),
            'font_name': 'Poppins-Regular.ttf'
        }
        
        # CONFIGURACIÓN PARA MÓDULOS Y HORAS
        self.modulos_config = {
            'size': 18,
            'color': (64, 64, 64),
            'font_name': 'Poppins-Regular.ttf'
        }
        
        # CONFIGURACIÓN PARA EL TOTAL DE HORAS
        self.total_horas_config = {
            'size': 18,
            'color': (0, 0, 0),
            'font_name': 'Poppins-Regular.ttf'
        }

        # CONFIGURACIÓN PARA EL PROMEDIO FINAL
        self.promedio_final_config = {
            'size': 18,
            'color': (0, 0, 0),
            'font_name': 'Poppins-Regular.ttf'
        }
        
        # ============================================================
        # CONFIGURACIÓN DE COORDENADAS - PORTADA
        # ============================================================
        self.portada_coords = {
            'nombre_x': None,  # Se calculará como centro si es None
            'nombre_y': None,  # Valor por defecto si es None
            'folio_x': None,
            'folio_y': None
        }
        
        # ============================================================
        # CONFIGURACIÓN DE COORDENADAS - CONTRAPORTADA
        # ============================================================
        self.contraportada_coords = {
            'mod_base_x': 870,
            'mod_base_y': 450,
            'calif_base_x': 1100,
            'calif_base_y': 450,
            'incremento_y': 120,
            'total_x': 870,
            'total_y': 930,
            'promedio_x': 1030,
            'promedio_y': 930
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
            font_paths = [
                f"/System/Library/Fonts/{font_name}",
                f"/usr/share/fonts/truetype/dejavu/{font_name}",
                f"C:/Windows/Fonts/{font_name}",
                font_name
            ]
            
            for path in font_paths:
                try:
                    return ImageFont.truetype(path, size)
                except:
                    continue
            
            print(f"Advertencia: No se pudo cargar la fuente {font_name}, usando fuente por defecto")
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def set_font_config(self, element, size=None, color=None, font_name=None):
        """
        Método para actualizar la configuración de fuentes programáticamente
        
        Args:
            element (str): 'nombre', 'folio', 'modulos', 'total_horas', 'promedio_final'
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
    
    def set_portada_coordinates(self, nombre_x=None, nombre_y=None, folio_x=None, folio_y=None):
        """
        Configura las coordenadas para la portada
        
        Args:
            nombre_x (int): Posición X para el nombre (se centra respecto a esta)
            nombre_y (int): Posición Y para el nombre
            folio_x (int): Posición X para el folio (se centra respecto a esta)
            folio_y (int): Posición Y para el folio
        """
        if nombre_x is not None:
            self.portada_coords['nombre_x'] = nombre_x
        if nombre_y is not None:
            self.portada_coords['nombre_y'] = nombre_y
        if folio_x is not None:
            self.portada_coords['folio_x'] = folio_x
        if folio_y is not None:
            self.portada_coords['folio_y'] = folio_y
    
    def set_contraportada_coordinates(self, mod_base_x=None, mod_base_y=None, 
                                     calif_base_x=None, calif_base_y=None,
                                     incremento_y=None, total_x=None, total_y=None,
                                     promedio_x=None, promedio_y=None):
        """
        Configura las coordenadas para la contraportada
        
        Args:
            mod_base_x (int): X inicial para módulos (horas)
            mod_base_y (int): Y inicial para módulos (horas)
            calif_base_x (int): X inicial para calificaciones
            calif_base_y (int): Y inicial para calificaciones
            incremento_y (int): Incremento en Y entre módulos
            total_x (int): X para total de horas
            total_y (int): Y para total de horas
            promedio_x (int): X para promedio final
            promedio_y (int): Y para promedio final
        """
        if mod_base_x is not None:
            self.contraportada_coords['mod_base_x'] = mod_base_x
        if mod_base_y is not None:
            self.contraportada_coords['mod_base_y'] = mod_base_y
        if calif_base_x is not None:
            self.contraportada_coords['calif_base_x'] = calif_base_x
        if calif_base_y is not None:
            self.contraportada_coords['calif_base_y'] = calif_base_y
        if incremento_y is not None:
            self.contraportada_coords['incremento_y'] = incremento_y
        if total_x is not None:
            self.contraportada_coords['total_x'] = total_x
        if total_y is not None:
            self.contraportada_coords['total_y'] = total_y
        if promedio_x is not None:
            self.contraportada_coords['promedio_x'] = promedio_x
        if promedio_y is not None:
            self.contraportada_coords['promedio_y'] = promedio_y
    
    def load_csv_data(self, csv_path):
        """Carga los datos del CSV"""
        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as e:
            print(f"Error al cargar el archivo CSV: {e}")
            return None
    
    def create_portada(self, nombre, folio, output_path):
        """
        Genera la portada del diploma con coordenadas configurables
        
        Args:
            nombre (str): Nombre del estudiante
            folio (str): Número de folio
            output_path (str): Ruta donde guardar la imagen
        """
        img = Image.open(self.portada_template)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Usar coordenadas configuradas o valores por defecto
        nombre_pos_x = self.portada_coords['nombre_x'] if self.portada_coords['nombre_x'] is not None else width // 2
        nombre_pos_y = self.portada_coords['nombre_y'] if self.portada_coords['nombre_y'] is not None else height // 2 - 295
        folio_pos_x = self.portada_coords['folio_x'] if self.portada_coords['folio_x'] is not None else width // 2
        folio_pos_y = self.portada_coords['folio_y'] if self.portada_coords['folio_y'] is not None else height // 2 - 150
        
        folio_text = f"Folio: {folio}"
        
        # Dibujar nombre (centrado horizontalmente respecto a nombre_pos_x)
        nombre_bbox = draw.textbbox((0, 0), nombre, font=self.fonts['nombre'])
        nombre_width = nombre_bbox[2] - nombre_bbox[0]
        nombre_x = nombre_pos_x - (nombre_width // 2)
        draw.text((nombre_x, nombre_pos_y), nombre, 
                 fill=self.nombre_config['color'], 
                 font=self.fonts['nombre'])
        
        # Dibujar folio (centrado horizontalmente respecto a folio_pos_x)
        folio_bbox = draw.textbbox((0, 0), folio_text, font=self.fonts['folio'])
        folio_width = folio_bbox[2] - folio_bbox[0]
        folio_x = folio_pos_x - (folio_width // 2)
        draw.text((folio_x, folio_pos_y), folio_text, 
                 fill=self.folio_config['color'], 
                 font=self.fonts['folio'])
        
        img.save(output_path)
        print(f"Portada creada: {output_path}")
    
    def create_contraportada(self, datos_estudiante, output_path):
        """
        Genera la contraportada del diploma con coordenadas configurables
        
        Args:
            datos_estudiante (dict): Diccionario con todos los datos del estudiante
            output_path (str): Ruta donde guardar la imagen
        """
        img = Image.open(self.contraportada_template)
        draw = ImageDraw.Draw(img)

        # Usar coordenadas configuradas
        coords = self.contraportada_coords
        
        # Calcular posiciones de módulos
        horas_positions = {
            f'modulo{i}': (coords['mod_base_x'], coords['mod_base_y'] + coords['incremento_y'] * (i - 1))
            for i in range(1, 5)
        }
        
        calificaciones_positions = {
            f'modulo{i}': (coords['calif_base_x'], coords['calif_base_y'] + coords['incremento_y'] * (i - 1))
            for i in range(1, 5)
        }

        # Procesar módulos
        calificaciones = []
        for i in range(1, 5):
            horas_val = "30 horas"
            calif_val = datos_estudiante.get(f'modulo{i}_calificacion', '0')
            
            # Dibujar horas
            draw.text(horas_positions[f'modulo{i}'], horas_val,
                      fill=self.modulos_config['color'], font=self.fonts['modulos'])
            
            # Dibujar calificación
            draw.text(calificaciones_positions[f'modulo{i}'], str(calif_val),
                      fill=self.modulos_config['color'], font=self.fonts['modulos'])
            
            try:
                calificaciones.append(float(calif_val))
            except ValueError:
                pass

        # Total de horas
        draw.text((coords['total_x'], coords['total_y']), "120 horas",
                  fill=self.total_horas_config['color'], font=self.fonts['total_horas'])

        # Promedio final
        promedio_final = "{:.2f}".format(sum(calificaciones) / len(calificaciones)) if calificaciones else "0.00"
        draw.text((coords['promedio_x'], coords['promedio_y']), f"Promedio Final: {promedio_final}",
                  fill=self.promedio_final_config['color'], font=self.fonts['promedio_final'])

        img.save(output_path)
        print(f"Contraportada creada: {output_path}")
    
    def create_pdf(self, portada_path, contraportada_path, output_pdf_path):
        """Convierte las imágenes PNG a un PDF con dos páginas"""
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
        """Genera todos los diplomas basados en los datos del CSV"""
        df = self.load_csv_data(csv_path)
        if df is None:
            return
        
        print(f"Procesando {len(df)} diplomas...")
        
        for index, row in df.iterrows():
            try:
                nombre = row['nombre']
                folio = str(row['folio'])
                
                safe_name = "".join(c for c in nombre if c.isalnum() or c in (' ', '-', '_')).rstrip()
                portada_png = f"{self.output_dir}/png/{safe_name}_portada.png"
                contraportada_png = f"{self.output_dir}/png/{safe_name}_contraportada.png"
                diploma_pdf = f"{self.output_dir}/pdf/{safe_name}_diploma.pdf"
                
                self.create_portada(nombre, folio, portada_png)
                self.create_contraportada(row.to_dict(), contraportada_png)
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
    
    if not os.path.exists(args.csv):
        print(f"Error: No se encuentra el archivo CSV: {args.csv}")
        return
    
    if not os.path.exists(args.portada):
        print(f"Error: No se encuentra el template de portada: {args.portada}")
        return
    
    if not os.path.exists(args.contraportada):
        print(f"Error: No se encuentra el template de contraportada: {args.contraportada}")
        return
    
    generator = DiplomaGenerator(args.portada, args.contraportada, args.output)
    generator.generate_diplomas(args.csv)

if __name__ == "__main__":
    main()