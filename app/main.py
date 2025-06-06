import pandas as pd
import smtplib
import time
import threading
from tkinter import Tk, filedialog, Text, ttk, Label, Button, PhotoImage
from tkinter.scrolledtext import ScrolledText
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURAÇÕES ---
EMAIL_REMETENTE = 'emailremetente@email.com'
SENHA = 'suasenha@suasenha'
ASSUNTO = 'ASSUNTO DO EMAIL'
LOGO_URL = 'https://sualogo.com/substitua/com/url.png'

class EmailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("E-mail Sender")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f6ff")
        self.root.iconbitmap("mail.ico")  

        style = ttk.Style()
        style.theme_use("clam")

        # --- Cabeçalho ---
        Label(root, text="Envio de E-mails", 
              font=("Helvetica", 16, "bold"), fg="#26599b", bg="#f0f6ff").pack(pady=10)

        # --- Botões ---
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        self.btn_carregar = ttk.Button(button_frame, text="📂 Carregar CSV", command=self.carregar_csv)
        self.btn_carregar.grid(row=0, column=0, padx=10)

        self.btn_enviar = ttk.Button(button_frame, text="📧 Iniciar Envio", command=self.iniciar_envio)
        self.btn_enviar.grid(row=0, column=1, padx=10)

        # --- Área de status ---
        self.status = ScrolledText(root, height=20, width=85, font=("Courier", 10))
        self.status.pack(padx=10, pady=10)

        # --- Inicializa dados ---
        self.lista_pessoas = pd.DataFrame()

    def carregar_csv(self):
        caminho = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if caminho:
            try:
                df = pd.read_csv(caminho)
                self.lista_pessoas = df.dropna(subset=['email', 'nome'])
                self.status.insert("end", f"✅ CSV carregado com {len(self.lista_pessoas)} registros válidos.\n")
                self.status.see("end")
            except Exception as e:
                self.status.insert("end", f"[ERRO] Falha ao carregar CSV: {e}\n")

    def iniciar_envio(self):
        if self.lista_pessoas.empty:
            self.status.insert("end", "⚠️ Carregue um arquivo CSV primeiro!\n")
            return
        threading.Thread(target=self.enviar_emails).start()

    def enviar_emails(self):
        self.status.insert("end", "🔐 Conectando ao servidor SMTP...\n")
        self.status.see("end")
        try:
            servidor = smtplib.SMTP('smtp.gmail.com', 587)
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, SENHA)
        except Exception as e:
            self.status.insert("end", f"[ERRO] Falha na autenticação SMTP: {e}\n")
            return

        TAMANHO_LOTE = 50
        total_enviados = 0

        for i in range(0, len(self.lista_pessoas), TAMANHO_LOTE):
            lote = self.lista_pessoas.iloc[i:i+TAMANHO_LOTE]
            for _, pessoa in lote.iterrows():
                nome = pessoa['nome']
                destino = pessoa['email']

                CORPO_HTML = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
                        <div style="max-width: 600px; margin: auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h2 style="color: #2c3e50;">Confirmação de Inscrição</h2>
                        <p style="font-size: 16px; color: #333;">
                            Olá, <strong>{nome}</strong>,
                        </p>
                        <p style="font-size: 16px; color: #333;">
                           Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong> Sed euismod!
                        </p>
                        <p style="font-size: 16px; color: #333;">
                            Nulla facilisi. Integer posuere, velit et gravida tincidunt <strong>ex mauris accumsan lacus</strong>. sed facilisis lacus purus sit amet sapien.
                        </p>
                        <p style="font-size: 16px; color: #333;">
                            Donec euismod augue id porta scelerisque, magna sem consequat odio, ut varius metus turpis sed neque: 
                            <a href="https://seulink.com/pasta" style="color: #2980b9;">seulink.com/programacao</a>.
                        </p>
                        <p style="font-size: 16px; color: #333;">
                            Curabitur ac tortor at justo congue porttitor 
                            <a href="email@email.com" style="color: #2980b9;">email@email.com</a> Cras efficitur 
                            <a href="https://seulink.com/pasta" style="color: #2980b9;">https://seulink.com/pasta/contato</a>.
                        </p>
                        <p style="font-size: 16px; color: #333;">
                            sem ut fermentum hendrerit, elit lorem feugiat turpis<br>
                        </p>
                        <p style="font-size: 16px; color: #333;">
                            ESTE É UM E-MAIL AUTOMÁTICO, NÃO RESPONDA.
                        </p>
                        <hr style="margin: 30px 0;">
                        <p style="font-size: 14px; color: #888;">
                             Sit amet egestas nunc velit nec risus.<br>
                            <a href="https://seulink.com/pasta" style="color: #2980b9;">https://seulink.com/pasta/contato</a>
                        </p>
                        <div style="text-align: center; margin-top: 20px;">
                            <img src="{LOGO_URL}" alt="Logo" style="max-width: 150px; opacity: 0.7;">
                        </div>
                        </div>
                    </body>
                    </html>
                    """

                msg = MIMEMultipart('alternative')
                msg['From'] = EMAIL_REMETENTE
                msg['To'] = destino
                msg['Subject'] = ASSUNTO
                msg.attach(MIMEText(CORPO_HTML, 'html'))

                try:
                    servidor.sendmail(EMAIL_REMETENTE, destino, msg.as_string())
                    total_enviados += 1
                    self.status.insert("end", f"[{total_enviados}] E-mail enviado para {nome} <{destino}>\n")
                    self.status.see("end")
                except Exception as e:
                    self.status.insert("end", f"[ERRO] Falha ao enviar para {destino}: {e}\n")
                    self.status.see("end")

            self.status.insert("end", "--- Aguardando 60 segundos antes do próximo lote... ---\n")
            self.status.see("end")
            time.sleep(60)

        servidor.quit()
        self.status.insert("end", f"\n✅ Envio finalizado. Total de e-mails enviados com sucesso: {total_enviados}\n")
        self.status.see("end")


# --- RODAR A INTERFACE ---
if __name__ == "__main__":
    root = Tk()
    app = EmailSenderApp(root)
    root.mainloop()
