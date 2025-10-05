import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import shutil
import zipfile
from datetime import datetime
from diploma_generator import DiplomaGenerator

# Configuración de la página
st.set_page_config(
    page_title="Generador de Diplomas",
    page_icon="🎓",
    layout="wide"
)

# Título principal
st.title("🎓 Generador Automático de Diplomas")
st.markdown("---")

# Inicializar session state
if 'generator' not in st.session_state:
    st.session_state.generator = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'show_coordinates_portada' not in st.session_state:
    st.session_state.show_coordinates_portada = False
if 'show_coordinates_contra' not in st.session_state:
    st.session_state.show_coordinates_contra = False

# Función para convertir hex a RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Función para dibujar preview con coordenadas
def draw_preview_with_coords(image, coords_dict, texts_dict):
    """Dibuja un preview de la imagen con las coordenadas marcadas"""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    
    for key, (x, y) in coords_dict.items():
        # Dibujar cruz en las coordenadas
        size = 20
        draw.line([(x-size, y), (x+size, y)], fill='red', width=3)
        draw.line([(x, y-size), (x, y+size)], fill='red', width=3)
        
        # Dibujar círculo
        draw.ellipse([(x-5, y-5), (x+5, y+5)], outline='red', width=2)
        
        # Dibujar etiqueta
        label = texts_dict.get(key, key)
        draw.text((x+15, y-15), label, fill='red')
    
    return img_copy

# Función para limpiar directorio de salida
def limpiar_directorio_salida(output_dir):
    """Elimina todos los archivos generados previamente"""
    try:
        if os.path.exists(output_dir):
            # Eliminar todo el contenido del directorio
            shutil.rmtree(output_dir)
        # Recrear los directorios
        os.makedirs(f"{output_dir}/png", exist_ok=True)
        os.makedirs(f"{output_dir}/pdf", exist_ok=True)
        return True
    except Exception as e:
        st.error(f"Error al limpiar directorio: {e}")
        return False

# Función para crear archivo ZIP con los diplomas
def crear_zip_diplomas(output_dir):
    """Crea un archivo ZIP con todos los diplomas generados"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"diplomas_{timestamp}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Agregar todos los PDFs
            pdf_dir = os.path.join(output_dir, 'pdf')
            if os.path.exists(pdf_dir):
                for filename in os.listdir(pdf_dir):
                    if filename.endswith('.pdf'):
                        file_path = os.path.join(pdf_dir, filename)
                        zipf.write(file_path, os.path.join('pdf', filename))
            
            # Agregar todos los PNGs
            png_dir = os.path.join(output_dir, 'png')
            if os.path.exists(png_dir):
                for filename in os.listdir(png_dir):
                    if filename.endswith('.png'):
                        file_path = os.path.join(png_dir, filename)
                        zipf.write(file_path, os.path.join('png', filename))
        
        return zip_path
    except Exception as e:
        st.error(f"Error al crear ZIP: {e}")
        return None

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Sección de archivos
    st.subheader("📁 Archivos")
    
    portada_file = st.file_uploader("Plantilla Portada (PNG)", type=['png'], key='portada')
    contraportada_file = st.file_uploader("Plantilla Contraportada (PNG)", type=['png'], key='contraportada')
    csv_file = st.file_uploader("Archivo CSV con datos", type=['csv'], key='csv')
    
    output_dir = st.text_input("Directorio de salida", value="diplomas_generados")
    
    st.markdown("---")
    
    # Personalización de fuentes y colores
    st.subheader("🎨 Personalización")
    
    with st.expander("Nombre del Estudiante"):
        nombre_size = st.slider("Tamaño fuente", 30, 150, 95, key='nombre_size')
        nombre_color = st.color_picker("Color", "#0A627E", key='nombre_color')
    
    with st.expander("Folio"):
        folio_size = st.slider("Tamaño fuente", 12, 50, 24, key='folio_size')
        folio_color = st.color_picker("Color", "#969696", key='folio_color')
    
    with st.expander("Módulos y Calificaciones"):
        modulos_size = st.slider("Tamaño fuente", 10, 40, 18, key='modulos_size')
        modulos_color = st.color_picker("Color", "#404040", key='modulos_color')
    
    with st.expander("Total de Horas"):
        total_size = st.slider("Tamaño fuente", 10, 40, 18, key='total_size')
        total_color = st.color_picker("Color", "#000000", key='total_color')
    
    with st.expander("Promedio Final"):
        promedio_size = st.slider("Tamaño fuente", 10, 40, 18, key='promedio_size')
        promedio_color = st.color_picker("Color", "#000000", key='promedio_color')

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📋 Datos CSV", "📐 Coordenadas Portada", "📐 Coordenadas Contraportada", "🚀 Generar"])

# TAB 1: Datos CSV
with tab1:
    st.subheader("📋 Vista Previa de Datos")
    
    if csv_file is not None:
        try:
            df = pd.read_csv(csv_file)
            st.session_state.df = df
            st.dataframe(df, use_container_width=True)
            
            st.info(f"✅ {len(df)} diplomas para generar")
            
            # Validar columnas
            required_cols = ['nombre', 'folio', 'modulo1_calificacion', 'modulo2_calificacion', 
                           'modulo3_calificacion', 'modulo4_calificacion']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Faltan columnas: {', '.join(missing_cols)}")
            else:
                st.success("✅ Formato del CSV correcto")
                
        except Exception as e:
            st.error(f"Error al leer CSV: {e}")
    else:
        st.info("👆 Sube un archivo CSV para comenzar")
        
        # Mostrar ejemplo de formato
        with st.expander("Ver formato del CSV requerido"):
            ejemplo_df = pd.DataFrame({
                'nombre': ['Juan Pérez', 'María García'],
                'folio': ['001', '002'],
                'modulo1_calificacion': [9.5, 8.7],
                'modulo2_calificacion': [8.8, 9.1],
                'modulo3_calificacion': [9.2, 8.9],
                'modulo4_calificacion': [9.0, 9.3]
            })
            st.dataframe(ejemplo_df)

# TAB 2: Coordenadas Portada
with tab2:
    st.subheader("📐 Configurar Coordenadas - Portada")
    
    if portada_file is not None:
        portada_image = Image.open(portada_file)
        img_width, img_height = portada_image.size
        
        st.info(f"Dimensiones de la imagen: {img_width} x {img_height} píxeles")
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.markdown("### 🎯 Coordenadas")
            
            st.markdown("**Nombre del Estudiante:**")
            nombre_x = st.number_input("X (horizontal)", value=img_width//2, min_value=0, max_value=img_width, key='nombre_x')
            nombre_y = st.number_input("Y (vertical)", value=img_height//2 - 295, min_value=0, max_value=img_height, key='nombre_y')
            st.caption("El nombre se centrará horizontalmente respecto a esta X")
            
            st.markdown("**Folio:**")
            folio_x = st.number_input("X (horizontal)", value=img_width//2, min_value=0, max_value=img_width, key='folio_x')
            folio_y = st.number_input("Y (vertical)", value=img_height//2 - 150, min_value=0, max_value=img_height, key='folio_y')
            st.caption("El folio se centrará horizontalmente respecto a esta X")
            
            if st.button("🔄 Actualizar Vista Previa", key='update_portada'):
                st.session_state.show_coordinates_portada = True
        
        with col1:
            st.markdown("### 👁️ Vista Previa")
            
            if st.session_state.show_coordinates_portada:
                coords = {
                    'nombre': (nombre_x, nombre_y),
                    'folio': (folio_x, folio_y)
                }
                labels = {
                    'nombre': 'Nombre',
                    'folio': 'Folio'
                }
                preview_img = draw_preview_with_coords(portada_image, coords, labels)
                st.image(preview_img, use_column_width=True)
                st.caption("🔴 Las cruces rojas indican dónde se colocarán los elementos")
            else:
                st.image(portada_image, use_column_width=True)
                st.caption("👆 Haz clic en 'Actualizar Vista Previa' para ver las coordenadas")
    else:
        st.warning("⚠️ Primero carga la imagen de la portada en el panel lateral")

# TAB 3: Coordenadas Contraportada
with tab3:
    st.subheader("📐 Configurar Coordenadas - Contraportada")
    
    if contraportada_file is not None:
        contraportada_image = Image.open(contraportada_file)
        img_width, img_height = contraportada_image.size
        
        st.info(f"Dimensiones de la imagen: {img_width} x {img_height} píxeles")
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.markdown("### 🎯 Coordenadas Base")
            
            st.markdown("**Posición inicial (Módulo 1 - Horas):**")
            mod_base_x = st.number_input("X base", value=870, min_value=0, max_value=img_width, key='mod_base_x')
            mod_base_y = st.number_input("Y base", value=450, min_value=0, max_value=img_height, key='mod_base_y')
            
            incremento_y = st.number_input("Incremento Y entre módulos", value=120, min_value=0, max_value=500, key='incremento_y')
            
            st.markdown("**Posición Calificaciones (Módulo 1):**")
            calif_base_x = st.number_input("X calificaciones", value=1100, min_value=0, max_value=img_width, key='calif_base_x')
            calif_base_y = st.number_input("Y calificaciones", value=450, min_value=0, max_value=img_height, key='calif_base_y')
            
            st.markdown("**Total y Promedio:**")
            total_x = st.number_input("X Total Horas", value=870, min_value=0, max_value=img_width, key='total_x')
            total_y = st.number_input("Y Total Horas", value=930, min_value=0, max_value=img_height, key='total_y')
            
            promedio_x = st.number_input("X Promedio", value=1030, min_value=0, max_value=img_width, key='promedio_x')
            promedio_y = st.number_input("Y Promedio", value=930, min_value=0, max_value=img_height, key='promedio_y')
            
            if st.button("🔄 Actualizar Vista Previa", key='update_contra'):
                st.session_state.show_coordinates_contra = True
        
        with col1:
            st.markdown("### 👁️ Vista Previa")
            
            if st.session_state.show_coordinates_contra:
                coords = {
                    'mod1_horas': (mod_base_x, mod_base_y),
                    'mod2_horas': (mod_base_x, mod_base_y + incremento_y),
                    'mod3_horas': (mod_base_x, mod_base_y + incremento_y * 2),
                    'mod4_horas': (mod_base_x, mod_base_y + incremento_y * 3),
                    'mod1_calif': (calif_base_x, calif_base_y),
                    'mod2_calif': (calif_base_x, calif_base_y + incremento_y),
                    'mod3_calif': (calif_base_x, calif_base_y + incremento_y * 2),
                    'mod4_calif': (calif_base_x, calif_base_y + incremento_y * 3),
                    'total': (total_x, total_y),
                    'promedio': (promedio_x, promedio_y)
                }
                labels = {
                    'mod1_horas': 'Mod1-H',
                    'mod2_horas': 'Mod2-H',
                    'mod3_horas': 'Mod3-H',
                    'mod4_horas': 'Mod4-H',
                    'mod1_calif': 'Mod1-C',
                    'mod2_calif': 'Mod2-C',
                    'mod3_calif': 'Mod3-C',
                    'mod4_calif': 'Mod4-C',
                    'total': 'Total',
                    'promedio': 'Promedio'
                }
                preview_img = draw_preview_with_coords(contraportada_image, coords, labels)
                st.image(preview_img, use_column_width=True)
                st.caption("🔴 Las cruces rojas indican dónde se colocarán los elementos")
            else:
                st.image(contraportada_image, use_column_width=True)
                st.caption("👆 Haz clic en 'Actualizar Vista Previa' para ver las coordenadas")
    else:
        st.warning("⚠️ Primero carga la imagen de la contraportada en el panel lateral")

# TAB 4: Generar
with tab4:
    st.subheader("🚀 Generar Diplomas")
    
    # Verificar que todo esté listo
    ready_checks = {
        "Portada cargada": portada_file is not None,
        "Contraportada cargada": contraportada_file is not None,
        "CSV cargado": csv_file is not None
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Checklist:")
        for check, status in ready_checks.items():
            if status:
                st.success(f"✅ {check}")
            else:
                st.error(f"❌ {check}")
    
    with col2:
        st.markdown("### 📊 Resumen:")
        if csv_file and st.session_state.df is not None:
            st.info(f"📄 {len(st.session_state.df)} diplomas para generar")
        st.info(f"📁 Guardar en: `{output_dir}/`")
    
    st.markdown("---")
    
    if all(ready_checks.values()):
        generate_btn = st.button("🎓 Generar Todos los Diplomas", type="primary", use_container_width=True)
        
        if generate_btn:
            try:
                # Limpiar diplomas anteriores para no desbordar la memoria
                with st.spinner('🗑️ Limpiando diplomas anteriores...'):
                    if not limpiar_directorio_salida(output_dir):
                        st.error("No se pudo limpiar el directorio. Abortando generación.")
                        st.stop()
                    st.success("✅ Directorio limpiado correctamente")
                
                # Guardar archivos temporalmente
                os.makedirs("temp", exist_ok=True)
                
                portada_path = "temp/portada_temp.png"
                contraportada_path = "temp/contraportada_temp.png"
                csv_path = "temp/data_temp.csv"
                
                with open(portada_path, "wb") as f:
                    f.write(portada_file.getbuffer())
                
                with open(contraportada_path, "wb") as f:
                    f.write(contraportada_file.getbuffer())
                
                with open(csv_path, "wb") as f:
                    f.write(csv_file.getbuffer())
                
                # Crear generador
                generator = DiplomaGenerator(portada_path, contraportada_path, output_dir)
                
                # Aplicar personalizaciones de colores y fuentes
                generator.set_font_config('nombre', size=nombre_size, color=hex_to_rgb(nombre_color))
                generator.set_font_config('folio', size=folio_size, color=hex_to_rgb(folio_color))
                generator.set_font_config('modulos', size=modulos_size, color=hex_to_rgb(modulos_color))
                generator.set_font_config('total_horas', size=total_size, color=hex_to_rgb(total_color))
                generator.set_font_config('promedio_final', size=promedio_size, color=hex_to_rgb(promedio_color))
                
                # Aplicar coordenadas personalizadas - PORTADA
                generator.set_portada_coordinates(
                    nombre_x=nombre_x,
                    nombre_y=nombre_y,
                    folio_x=folio_x,
                    folio_y=folio_y
                )
                
                # Aplicar coordenadas personalizadas - CONTRAPORTADA
                generator.set_contraportada_coordinates(
                    mod_base_x=mod_base_x,
                    mod_base_y=mod_base_y,
                    calif_base_x=calif_base_x,
                    calif_base_y=calif_base_y,
                    incremento_y=incremento_y,
                    total_x=total_x,
                    total_y=total_y,
                    promedio_x=promedio_x,
                    promedio_y=promedio_y
                )
                
                # Generar diplomas con barra de progreso
                with st.spinner('Generando diplomas...'):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    df = pd.read_csv(csv_path)
                    total = len(df)
                    
                    for index, row in df.iterrows():
                        try:
                            nombre = row['nombre']
                            folio = str(row['folio'])
                            
                            safe_name = "".join(c for c in nombre if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            portada_png = f"{output_dir}/png/{safe_name}_portada.png"
                            contraportada_png = f"{output_dir}/png/{safe_name}_contraportada.png"
                            diploma_pdf = f"{output_dir}/pdf/{safe_name}_diploma.pdf"
                            
                            generator.create_portada(nombre, folio, portada_png)
                            generator.create_contraportada(row.to_dict(), contraportada_png)
                            generator.create_pdf(portada_png, contraportada_png, diploma_pdf)
                            
                            progress = (index + 1) / total
                            progress_bar.progress(progress)
                            status_text.text(f"Procesando: {nombre} ({index + 1}/{total})")
                            
                        except Exception as e:
                            st.error(f"Error procesando {row.get('nombre', 'desconocido')}: {e}")
                    
                    progress_bar.progress(1.0)
                    status_text.text("¡Completado!")
                
                st.success(f"✅ ¡{total} diplomas generados exitosamente!")
                
                # Crear archivo ZIP con todos los diplomas
                with st.spinner('📦 Creando archivo ZIP para descarga...'):
                    zip_path = crear_zip_diplomas(output_dir)
                    
                    if zip_path and os.path.exists(zip_path):
                        st.success("✅ Archivo ZIP creado correctamente")
                        
                        # Botón de descarga del ZIP
                        with open(zip_path, 'rb') as f:
                            st.download_button(
                                label="📥 Descargar todos los diplomas (ZIP)",
                                data=f,
                                file_name=os.path.basename(zip_path),
                                mime="application/zip",
                                type="primary",
                                use_container_width=True
                            )
                    else:
                        st.error("❌ No se pudo crear el archivo ZIP")
                
                st.balloons()
                
                # Mostrar ubicación de archivos
                st.info(f"📁 Los diplomas se guardaron en: `{output_dir}/`")
                
                # Mostrar preview del primer diploma generado
                if os.path.exists(f"{output_dir}/png"):
                    png_files = [f for f in os.listdir(f"{output_dir}/png") if f.endswith('_portada.png')]
                    if png_files:
                        st.subheader("Vista previa del primer diploma generado:")
                        col1, col2 = st.columns(2)
                        with col1:
                            preview_portada = Image.open(f"{output_dir}/png/{png_files[0]}")
                            st.image(preview_portada, caption="Portada", use_column_width=True)
                        with col2:
                            contraportada_file_name = png_files[0].replace('_portada.png', '_contraportada.png')
                            if os.path.exists(f"{output_dir}/png/{contraportada_file_name}"):
                                preview_contra = Image.open(f"{output_dir}/png/{contraportada_file_name}")
                                st.image(preview_contra, caption="Contraportada", use_column_width=True)
                
            except Exception as e:
                st.error(f"❌ Error durante la generación: {e}")
                st.exception(e)
    else:
        st.warning("⚠️ Completa todos los pasos anteriores antes de generar")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 <strong>Pasos:</strong> 1) Cargar archivos 2) Configurar coordenadas 3) Personalizar colores 4) Generar</p>
    <p>Cada módulo tiene 30 horas fijas | Total: 120 horas</p>
</div>
""", unsafe_allow_html=True)