import re
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def normalize_phone(phone: str) -> str:
    """Normaliza telefone para formato numérico: apenas dígitos, com DDI/DDD caso necessário."""
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    # Se tiver 10 ou 11 dígitos, retornamos assim; senão, retorna como está
    if len(digits) in (10, 11):
        return digits
    return digits

def enviar_email_confirmacao(nome: str, email: str, token: str = '', nome_local: str = '') -> bool:
    """Envia um e-mail simples de confirmação (SMTP).
    As configurações esperadas no ambiente:
    EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, FROM_EMAIL
    Retorna True se enviado com sucesso, False caso contrário.
    """
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT', 587))
    user = os.getenv('EMAIL_USER')
    pwd = os.getenv('EMAIL_PASS')
    from_addr = os.getenv('FROM_EMAIL') or user

    if not (host and user and pwd and from_addr and email):
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = f'Confirmação de acesso - {nome_local or "Tracecom"}'
        msg['From'] = from_addr
        msg['To'] = email
        body = f"Olá {nome},\n\nSeu acesso foi registrado para {nome_local}.\n\nObrigado!\nTracecom\n"
        msg.set_content(body)

        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(user, pwd)
            smtp.send_message(msg)
        return True
    except Exception as e:
        # Em produção, coloque logging apropriado aqui
        return False
