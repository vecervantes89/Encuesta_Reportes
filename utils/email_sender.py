import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailSender:
    def __init__(self):
        # Configuración de email desde variables de entorno
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_usuario = os.getenv("EMAIL_USER", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.email_remitente = os.getenv("EMAIL_FROM", self.email_usuario)
    
    def enviar_confirmacion(self, email_destinatario, nombre_reporte):
        """Enviar email de confirmación al usuario que completó la encuesta"""
        try:
            if not self.email_usuario or not self.email_password:
                print("Configuración de email no disponible - saltando envío de confirmación")
                return False
            
            # Crear mensaje
            mensaje = MIMEMultipart()
            mensaje['From'] = self.email_remitente
            mensaje['To'] = email_destinatario
            mensaje['Subject'] = "Confirmación - Encuesta de Reportes Corporativos Completada"
            
            # Cuerpo del email
            cuerpo_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2E86AB; border-bottom: 2px solid #2E86AB; padding-bottom: 10px;">
                            ✅ Encuesta Completada Exitosamente
                        </h2>
                        
                        <p>Estimado/a colaborador/a,</p>
                        
                        <p>Confirmamos que hemos recibido correctamente su encuesta sobre el reporte corporativo:</p>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #2E86AB; margin: 20px 0;">
                            <strong>📋 Reporte:</strong> {nombre_reporte}<br>
                            <strong>📅 Fecha de envío:</strong> {datetime.now().strftime("%d/%m/%Y a las %H:%M")}
                        </div>
                        
                        <p>Su información será procesada y utilizada para mejorar la gestión de reportes corporativos en nuestra organización.</p>
                        
                        <h3 style="color: #2E86AB;">Próximos Pasos:</h3>
                        <ul>
                            <li>Su respuesta ha sido registrada en nuestro sistema</li>
                            <li>Los datos serán revisados por el equipo de auditoría</li>
                            <li>Recibirá actualizaciones si necesitamos información adicional</li>
                        </ul>
                        
                        <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <strong>💡 Información Importante:</strong><br>
                            Si necesita realizar alguna modificación o tiene dudas sobre su respuesta, 
                            por favor contacte al administrador del sistema lo antes posible.
                        </div>
                        
                        <p>Gracias por su colaboración y por contribuir a mejorar nuestros procesos de reporte.</p>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                        
                        <p style="color: #666; font-size: 12px;">
                            Este es un mensaje automático del Sistema de Gestión de Reportes Corporativos.<br>
                            Por favor no responda directamente a este correo.
                        </p>
                        
                        <p style="color: #666; font-size: 12px;">
                            <strong>Confidencialidad:</strong> La información proporcionada será tratada de forma estrictamente confidencial 
                            y utilizada únicamente para fines de mejora de procesos internos.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            mensaje.attach(MIMEText(cuerpo_html, 'html'))
            
            # Conectar y enviar
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_usuario, self.email_password)
            
            texto = mensaje.as_string()
            server.sendmail(self.email_remitente, email_destinatario, texto)
            server.quit()
            
            print(f"Email de confirmación enviado a {email_destinatario}")
            return True
            
        except Exception as e:
            print(f"Error al enviar email de confirmación: {str(e)}")
            return False
    
    def enviar_notificacion_admin(self, datos_encuesta):
        """Enviar notificación al administrador sobre nueva encuesta"""
        try:
            email_admin = os.getenv("ADMIN_EMAIL", "")
            
            if not email_admin or not self.email_usuario or not self.email_password:
                print("Configuración de email admin no disponible")
                return False
            
            # Crear mensaje
            mensaje = MIMEMultipart()
            mensaje['From'] = self.email_remitente
            mensaje['To'] = email_admin
            mensaje['Subject'] = f"Nueva Encuesta Recibida - {datos_encuesta.get('nombre_reporte', 'Reporte sin nombre')}"
            
            # Cuerpo del email para admin
            cuerpo_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #dc3545; border-bottom: 2px solid #dc3545; padding-bottom: 10px;">
                            🔔 Nueva Encuesta de Reporte Recibida
                        </h2>
                        
                        <p>Se ha recibido una nueva encuesta en el sistema de gestión de reportes corporativos.</p>
                        
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #495057;">📋 Detalles del Reporte:</h3>
                            
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold; width: 40%;">Nombre del Reporte:</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{datos_encuesta.get('nombre_reporte', 'N/A')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Responsable:</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{datos_encuesta.get('persona_responsable', 'N/A')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Email:</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{datos_encuesta.get('email_responsable', 'N/A')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Departamento:</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{datos_encuesta.get('departamento', 'N/A')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Criticidad:</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{datos_encuesta.get('criticidad', 'N/A')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Periodicidad:</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{datos_encuesta.get('periodicidad_reporte', 'N/A')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Sistema Origen:</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{datos_encuesta.get('sistema_origen', 'N/A')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Fecha de Envío:</td>
                                    <td style="padding: 8px;">{datos_encuesta.get('fecha_envio', 'N/A')}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                            <strong>⚠️ Acción Requerida:</strong><br>
                            Revise la nueva encuesta en el panel de administración del sistema.
                        </div>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="#" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                                🔗 Ir al Panel de Administración
                            </a>
                        </p>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                        
                        <p style="color: #666; font-size: 12px;">
                            Este es un mensaje automático del Sistema de Gestión de Reportes Corporativos.<br>
                            Mensaje generado el {datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")}
                        </p>
                    </div>
                </body>
            </html>
            """
            
            mensaje.attach(MIMEText(cuerpo_html, 'html'))
            
            # Conectar y enviar
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_usuario, self.email_password)
            
            texto = mensaje.as_string()
            server.sendmail(self.email_remitente, email_admin, texto)
            server.quit()
            
            print(f"Notificación admin enviada a {email_admin}")
            return True
            
        except Exception as e:
            print(f"Error al enviar notificación admin: {str(e)}")
            return False
    
    def enviar_recordatorio_masivo(self, lista_emails, asunto_personalizado=None):
        """Enviar recordatorio masivo para completar encuestas"""
        try:
            if not self.email_usuario or not self.email_password:
                print("Configuración de email no disponible")
                return False
            
            asunto = asunto_personalizado or "Recordatorio - Complete la Encuesta de Reportes Corporativos"
            enviados_exitosos = 0
            
            # Plantilla del recordatorio
            cuerpo_html = """
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #28a745; border-bottom: 2px solid #28a745; padding-bottom: 10px;">
                            📋 Recordatorio - Encuesta de Reportes Corporativos
                        </h2>
                        
                        <p>Estimado/a colaborador/a,</p>
                        
                        <p>Le recordamos que necesitamos su colaboración para completar la encuesta sobre los reportes corporativos utilizados en su área de trabajo.</p>
                        
                        <div style="background-color: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                            <strong>📝 ¿Qué información necesitamos?</strong>
                            <ul style="margin: 10px 0;">
                                <li>Nombre del reporte</li>
                                <li>Periodicidad de generación</li>
                                <li>Sistema de origen</li>
                                <li>Persona responsable</li>
                                <li>Auditorías donde se utiliza</li>
                                <li>Y otros detalles relevantes</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px;">
                                📋 Completar Encuesta Ahora
                            </a>
                        </div>
                        
                        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <strong>⏰ Tiempo estimado:</strong> Solo toma entre 5-10 minutos completar la encuesta.<br>
                            <strong>🔒 Confidencialidad:</strong> Toda la información será tratada de forma confidencial.
                        </div>
                        
                        <p><strong>¿Por qué es importante su participación?</strong></p>
                        <ul>
                            <li>Mejora la gestión de reportes corporativos</li>
                            <li>Optimiza procesos de auditoría</li>
                            <li>Identifica oportunidades de automatización</li>
                            <li>Fortalece el control interno</li>
                        </ul>
                        
                        <p>Si ya completó la encuesta, puede ignorar este mensaje. Gracias por su colaboración.</p>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                        
                        <p style="color: #666; font-size: 12px;">
                            Para dudas o soporte técnico, contacte al administrador del sistema.<br>
                            Este es un mensaje automático - Por favor no responda directamente.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Enviar a cada email de la lista
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_usuario, self.email_password)
            
            for email in lista_emails:
                try:
                    mensaje = MIMEMultipart()
                    mensaje['From'] = self.email_remitente
                    mensaje['To'] = email
                    mensaje['Subject'] = asunto
                    
                    mensaje.attach(MIMEText(cuerpo_html, 'html'))
                    
                    texto = mensaje.as_string()
                    server.sendmail(self.email_remitente, email, texto)
                    enviados_exitosos += 1
                    
                except Exception as e:
                    print(f"Error enviando a {email}: {str(e)}")
            
            server.quit()
            
            print(f"Recordatorios enviados exitosamente: {enviados_exitosos}/{len(lista_emails)}")
            return enviados_exitosos > 0
            
        except Exception as e:
            print(f"Error en envío masivo: {str(e)}")
            return False
    
    def test_configuracion(self):
        """Probar la configuración de email"""
        try:
            if not self.email_usuario or not self.email_password:
                return False, "Credenciales de email no configuradas"
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_usuario, self.email_password)
            server.quit()
            
            return True, "Configuración de email correcta"
            
        except Exception as e:
            return False, f"Error en configuración: {str(e)}"
