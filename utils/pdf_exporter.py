from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import pandas as pd
import io

class PDFExporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()
    
    def _crear_estilos_personalizados(self):
        """Crear estilos personalizados para el PDF"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
    
    def generar_reporte_completo(self, df, filename=None, incluir_estadisticas=True):
        """Generar reporte PDF completo con todas las encuestas"""
        if filename is None:
            filename = f"reporte_encuestas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Crear buffer para el PDF
        buffer = io.BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.5*inch
        )
        
        # Contenido del documento
        story = []
        
        # Título principal
        titulo = Paragraph("Reporte de Encuestas de Reportes Corporativos", self.styles['CustomTitle'])
        story.append(titulo)
        
        # Fecha de generación
        fecha_gen = Paragraph(
            f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            self.styles['CustomBody']
        )
        story.append(fecha_gen)
        story.append(Spacer(1, 0.3*inch))
        
        # Estadísticas generales si se solicitan
        if incluir_estadisticas and not df.empty:
            story.append(Paragraph("Resumen Ejecutivo", self.styles['CustomHeading']))
            
            stats_data = [
                ['Métrica', 'Valor'],
                ['Total de Reportes', str(len(df))],
                ['Departamentos Únicos', str(df['departamento'].nunique() if 'departamento' in df.columns else 0)],
                ['Sistemas Únicos', str(df['sistema_origen'].nunique() if 'sistema_origen' in df.columns else 0)],
                ['Reportes Críticos', str(len(df[df['criticidad'] == 'Alto']) if 'criticidad' in df.columns else 0)],
                ['Reportes Automatizados', str(len(df[df['automatizado'] == 'Sí']) if 'automatizado' in df.columns else 0)]
            ]
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Tabla de encuestas
        story.append(PageBreak())
        story.append(Paragraph("Listado Detallado de Reportes", self.styles['CustomHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        if not df.empty:
            # Preparar datos para la tabla
            columnas_mostrar = [
                'nombre_reporte', 'persona_responsable', 'departamento',
                'periodicidad_reporte', 'criticidad', 'automatizado'
            ]
            
            # Filtrar columnas que existen
            columnas_existentes = [col for col in columnas_mostrar if col in df.columns]
            
            if columnas_existentes:
                df_tabla = df[columnas_existentes].copy()
                
                # Preparar headers
                headers_map = {
                    'nombre_reporte': 'Reporte',
                    'persona_responsable': 'Responsable',
                    'departamento': 'Departamento',
                    'periodicidad_reporte': 'Periodicidad',
                    'criticidad': 'Criticidad',
                    'automatizado': 'Automatizado'
                }
                
                headers = [headers_map.get(col, col) for col in columnas_existentes]
                
                # Convertir dataframe a lista de listas
                tabla_data = [headers]
                
                for _, row in df_tabla.iterrows():
                    fila = []
                    for col in columnas_existentes:
                        valor = str(row[col]) if pd.notna(row[col]) else ''
                        # Limitar longitud de texto
                        if len(valor) > 30:
                            valor = valor[:27] + '...'
                        fila.append(valor)
                    tabla_data.append(fila)
                
                # Calcular anchos de columna
                num_cols = len(columnas_existentes)
                col_width = 6.5 * inch / num_cols
                col_widths = [col_width] * num_cols
                
                # Crear tabla
                tabla = Table(tabla_data, colWidths=col_widths)
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                story.append(tabla)
        else:
            story.append(Paragraph("No hay datos disponibles", self.styles['CustomBody']))
        
        # Pie de página
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            "Sistema de Gestión de Reportes Corporativos",
            self.styles['CustomBody']
        ))
        
        # Construir PDF
        doc.build(story)
        
        # Obtener contenido del buffer
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content, filename
    
    def generar_reporte_individual(self, encuesta_data, filename=None):
        """Generar reporte PDF de una encuesta individual"""
        if filename is None:
            nombre_reporte = encuesta_data.get('nombre_reporte', 'reporte')
            nombre_reporte = nombre_reporte.replace(' ', '_')[:30]
            filename = f"reporte_{nombre_reporte}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Título
        titulo = Paragraph(
            f"Detalle de Reporte: {encuesta_data.get('nombre_reporte', 'N/A')}",
            self.styles['CustomTitle']
        )
        story.append(titulo)
        story.append(Spacer(1, 0.2*inch))
        
        # Información general
        story.append(Paragraph("Información General", self.styles['CustomHeading']))
        
        info_general = [
            ['Campo', 'Valor'],
            ['Nombre del Reporte', str(encuesta_data.get('nombre_reporte', 'N/A'))],
            ['Periodicidad', str(encuesta_data.get('periodicidad_reporte', 'N/A'))],
            ['Sistema de Origen', str(encuesta_data.get('sistema_origen', 'N/A'))],
            ['Responsable', str(encuesta_data.get('persona_responsable', 'N/A'))],
            ['Email', str(encuesta_data.get('email_responsable', 'N/A'))],
            ['Departamento', str(encuesta_data.get('departamento', 'N/A'))],
            ['Criticidad', str(encuesta_data.get('criticidad', 'N/A'))],
            ['Automatizado', str(encuesta_data.get('automatizado', 'N/A'))],
        ]
        
        tabla_info = Table(info_general, colWidths=[2.5*inch, 4*inch])
        tabla_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey)
        ]))
        
        story.append(tabla_info)
        story.append(Spacer(1, 0.3*inch))
        
        # Información de auditoría
        story.append(Paragraph("Información de Auditoría", self.styles['CustomHeading']))
        
        auditoria_text = str(encuesta_data.get('auditoria_utilizacion', 'N/A'))
        story.append(Paragraph(auditoria_text, self.styles['CustomBody']))
        story.append(Spacer(1, 0.2*inch))
        
        if encuesta_data.get('periodicidad_auditoria'):
            story.append(Paragraph(
                f"Periodicidad de Auditoría: {encuesta_data.get('periodicidad_auditoria')}",
                self.styles['CustomBody']
            ))
            story.append(Spacer(1, 0.2*inch))
        
        # Descripción
        if encuesta_data.get('descripcion_reporte'):
            story.append(Paragraph("Descripción del Reporte", self.styles['CustomHeading']))
            desc_text = str(encuesta_data.get('descripcion_reporte', ''))
            story.append(Paragraph(desc_text, self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Stakeholders
        if encuesta_data.get('stakeholders'):
            story.append(Paragraph("Stakeholders/Usuarios", self.styles['CustomHeading']))
            stake_text = str(encuesta_data.get('stakeholders', ''))
            story.append(Paragraph(stake_text, self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Observaciones
        if encuesta_data.get('observaciones'):
            story.append(Paragraph("Observaciones", self.styles['CustomHeading']))
            obs_text = str(encuesta_data.get('observaciones', ''))
            story.append(Paragraph(obs_text, self.styles['CustomBody']))
        
        # Pie de página
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            self.styles['CustomBody']
        ))
        
        doc.build(story)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content, filename
    
    def generar_reporte_por_departamento(self, df, departamento, filename=None):
        """Generar reporte PDF filtrado por departamento"""
        df_filtrado = df[df['departamento'] == departamento].copy()
        
        if filename is None:
            dept_safe = departamento.replace(' ', '_')
            filename = f"reporte_{dept_safe}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return self.generar_reporte_completo(df_filtrado, filename, incluir_estadisticas=True)
