import streamlit as st
import pandas as pd
from PIL import Image
import os
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

# Inicializar session state para mantener configuraciones
if 'generator' not in st.session_state:
    st.session_state.generator = None
if 'df' not in st.session_state:
    st.session_state.df = None

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Sección de archivos
    st.subheader("📁 Archivos")
    
    portada_file = st.file_uploader("Template Portada (PNG)", type=['png'], key='portada')
    contraportada_file = st.file_uploader("Template Contraportada (PNG)", type=['png'], key='contraportada')
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

# Función para convertir hex a RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Área principal
col1, col2 = st.columns([1, 1])

with col1:
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

with col2:
    st.subheader("👁️ Vista Previa de Templates")
    
    if portada_file is not None:
        st.write("**Portada:**")
        portada_image = Image.open(portada_file)
        st.image(portada_image, use_container_width=True)
    
    if contraportada_file is not None:
        st.write("**Contraportada:**")
        contraportada_image = Image.open(contraportada_file)
        st.image(contraportada_image, use_container_width=True)

# Sección de generación
st.markdown("---")
st.subheader("🚀 Generar Diplomas")

col_gen1, col_gen2 = st.columns([3, 1])

with col_gen1:
    if portada_file and contraportada_file and csv_file:
        st.success("✅ Todos los archivos cargados. Listo para generar diplomas.")
    else:
        st.warning("⚠️ Necesitas cargar todos los archivos (Portada, Contraportada y CSV)")

with col_gen2:
    generate_btn = st.button("🎓 Generar Diplomas", type="primary", use_container_width=True)

# Proceso de generación
if generate_btn:
    if not (portada_file and contraportada_file and csv_file):
        st.error("❌ Por favor carga todos los archivos necesarios")
    else:
        try:
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
            
            # Aplicar personalizaciones
            generator.set_font_config('nombre', 
                                     size=nombre_size, 
                                     color=hex_to_rgb(nombre_color))
            generator.set_font_config('folio', 
                                     size=folio_size, 
                                     color=hex_to_rgb(folio_color))
            generator.set_font_config('modulos', 
                                     size=modulos_size, 
                                     color=hex_to_rgb(modulos_color))
            generator.set_font_config('total_horas', 
                                     size=total_size, 
                                     color=hex_to_rgb(total_color))
            generator.set_font_config('promedio_final', 
                                     size=promedio_size, 
                                     color=hex_to_rgb(promedio_color))
            
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
            st.balloons()
            
            # Mostrar ubicación de archivos
            st.info(f"📁 Los diplomas se guardaron en: `{output_dir}/`")
            
            # Mostrar preview del primer diploma generado
            if os.path.exists(f"{output_dir}/png"):
                png_files = [f for f in os.listdir(f"{output_dir}/png") if f.endswith('_portada.png')]
                if png_files:
                    st.subheader("Vista previa del primer diploma generado:")
                    preview_img = Image.open(f"{output_dir}/png/{png_files[0]}")
                    st.image(preview_img, width=400)
            
        except Exception as e:
            st.error(f"❌ Error durante la generación: {e}")
            st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 <strong>Tip:</strong> Ajusta los colores y tamaños en el panel lateral antes de generar</p>
    <p>Cada módulo tiene 30 horas fijas | Total: 120 horas</p>
</div>
""", unsafe_allow_html=True)