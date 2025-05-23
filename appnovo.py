import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import os

# --------- CONFIGURAÇÃO INICIAL ---------
st.set_page_config(page_title="FluencyPass - Oral Assessment", layout="centered")

# Logo carregada com tratamento de erro
try:
    img = Image.open("logo.png")
    st.image(img)
except Exception as e:
    st.warning(f"Could not load logo image: {e}")

st.markdown("""
<h1 style='text-align: center; color: #2c3e50;'>Oral Assessment Tool</h1>
<p style='text-align: center;'>Evaluate speaking levels and provide feedback to students</p>
<hr>
""", unsafe_allow_html=True)

# --------- FUNÇÕES AUXILIARES ---------
criterios = {
    "Vocabulary": ["R", "S", "A"],
    "Fluency": ["R", "S", "A"],
    "Accuracy": ["R", "S", "A"],
    "Pronunciation": ["R", "S", "A"],
    "Communication": ["R", "S", "A"]
}

pontuacao = {"R": 1, "S": 2, "A": 3}

feedbacks_pt = {
    "Vocabulary": {
        "R": "Vocabulário básico em desenvolvimento, com espaço para expansão.",
        "S": "Vocabulário funcional, mas ainda com limitações para manter conversas mais longas.",
        "A": "Bom domínio de vocabulário para contextos cotidianos."
    },
    "Fluency": {
        "R": "Fala ainda se desenvolvendo, com pausas comuns e hesitações.",
        "S": "Fluência razoável, apesar de pausas ocasionais.",
        "A": "Discurso fluente, com ritmo consistente."
    },
    "Accuracy": {
        "R": "Erros frequentes, mas a comunicação básica é possível.",
        "S": "Erros gramaticais ocasionais, mas a mensagem geralmente é clara.",
        "A": "Boa precisão gramatical, com poucas falhas."
    },
    "Pronunciation": {
        "R": "Pronúncia em desenvolvimento, às vezes exigindo repetição.",
        "S": "Pronúncia compreensível, com sotaque perceptível.",
        "A": "Pronúncia clara e inteligível, com boa entonação."
    },
    "Communication": {
        "R": "Consegue iniciar comunicação, mas ainda precisa de suporte.",
        "S": "Consegue se comunicar com algum suporte.",
        "A": "Comunicação clara e autônoma."
    }
}

feedbacks_en = {
    "Vocabulary": {
        "R": "Limited vocabulary that hinders communication.",
        "S": "Functional vocabulary with occasional gaps.",
        "A": "Broad vocabulary appropriate for everyday contexts."
    },
    "Fluency": {
        "R": "Hesitant speech with frequent pauses.",
        "S": "Generally fluent with some hesitations.",
        "A": "Consistent and fluid speech."
    },
    "Accuracy": {
        "R": "Frequent grammatical errors affect comprehension.",
        "S": "Some errors in complex structures.",
        "A": "Minor errors, overall clear language use."
    },
    "Pronunciation": {
        "R": "Difficult to understand due to pronunciation issues.",
        "S": "Generally clear pronunciation.",
        "A": "Clear and understandable pronunciation."
    },
    "Communication": {
        "R": "Struggles to express ideas clearly.",
        "S": "Communicates effectively with minor issues.",
        "A": "Confident and clear communication."
    }
}

def determinar_nivel(total):
    if total <= 6:
        return "A1"
    elif total <= 10:
        return "A2"
    elif total <= 12:
        return "B1"
    else:
        return "B2 or higher"

def gerar_pdf_bytes(nome, email, nivel, data, selections, comentario):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    if os.path.exists("logo.png"):
        try:
            pdf.image("logo.png", x=10, y=8, w=40)
            pdf.ln(25)
        except RuntimeError:
            pass

    is_pt = nivel in ["A1", "A2"]
    feedbacks = feedbacks_pt if is_pt else feedbacks_en

    titulo = "Relatório de Avaliação Oral do Aluno" if is_pt else "Student Oral Assessment Report"
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=titulo, ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=(f"Nome do Aluno: {nome}" if is_pt else f"Student Name: {nome}"), ln=True)
    pdf.cell(0, 10, txt=f"Email: {email}", ln=True)
    pdf.cell(0, 10, txt=(f"Data da Avaliação: {data}" if is_pt else f"Date of Assessment: {data}"), ln=True)
    pdf.cell(0, 10, txt=(f"Nível Estimado: {nivel}" if is_pt else f"Estimated Level: {nivel}"), ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=("Feedback Detalhado:" if is_pt else "Detailed Feedback:"), ln=True)
    pdf.set_font("Arial", size=12)
    for criterio, nota in selections.items():
        pdf.multi_cell(0, 10, txt=f"{criterio}: {feedbacks[criterio][nota]}")

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=("Comentário do Professor:" if is_pt else "Teacher's Comment:"), ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, comentario)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=("Recomendações:" if is_pt else "Recommendations:"), ln=True)
    pdf.set_font("Arial", size=12)
    recomendacoes = (
        "Recomendamos que você participe dos Group Talks, agende Private Talks, escute o podcast FluencyCast, "
        "realize os módulos da plataforma Class e aproveite os recursos da comunidade, como vocabulário das aulas e vídeos complementares."
        if is_pt else
        "We recommend that the student joins Group Talks, schedules Private Talks, listens to the FluencyCast podcast, "
        "completes Class modules, and engages with the FluencyPass community resources, including vocabulary and lesson materials."
    )
    pdf.multi_cell(0, 10, recomendacoes)

    return pdf.output(dest='S').encode('latin1')

# --------- FORMULÁRIO ---------
st.markdown("## 👨‍🏫 Teacher Access")
email_teacher = st.text_input("Teacher Email:")

if email_teacher:
    opcao = st.radio("Choose an action:", ["📄 View History", "📝 New Oral Test"])

    if opcao == "📄 View History":
        try:
            df = pd.read_csv("avaliacoes.csv")
            df_filtered = df[df["Teacher Email"] == email_teacher]

            filtro_email_aluno = st.text_input("Filter by Student Email (optional):").strip().lower()
            if filtro_email_aluno:
                df_filtered = df_filtered[df_filtered["Student Email"].str.lower().str.contains(filtro_email_aluno)]

            if not df_filtered.empty:
                st.dataframe(df_filtered, use_container_width=True)
            else:
                st.info("No assessments found for the given filters.")
        except FileNotFoundError:
            st.warning("No records available yet.")

    elif opcao == "📝 New Oral Test":
        with st.form("oral_test_form"):
            nome_aluno = st.text_input("Student Name:")
            email_aluno = st.text_input("Student Email:")
            selections = {}
            for criterio, opcoes in criterios.items():
                selections[criterio] = st.radio(f"{criterio}", opcoes, horizontal=True)
            comentario_professor = st.text_area("Teacher's Comment (optional):")
            submitted = st.form_submit_button("Evaluate")

        if submitted:
            if nome_aluno.strip() == "" or email_aluno.strip() == "":
                st.error("Please fill out all fields.")
            else:
                total = sum([pontuacao[selections[c]] for c in criterios])
                nivel = determinar_nivel(total)
                data_atual = datetime.now().strftime("%Y-%m-%d %H:%M")

                st.success(f"✅ Estimated Level: {nivel}")
                for c in criterios:
                    st.markdown(f"- **{c}**: {feedbacks_en[c][selections[c]]}")

                df_new = pd.DataFrame([{
                    "Teacher Email": email_teacher,
                    "Student Name": nome_aluno,
                    "Student Email": email_aluno,
                    "Date": data_atual,
                    **selections,
                    "Total": total,
                    "Level": nivel,
                    "Teacher Comment": comentario_professor
                }])

                try:
                    df_existing = pd.read_csv("avaliacoes.csv")
                    df = pd.concat([df_existing, df_new], ignore_index=True)
                except FileNotFoundError:
                    df = df_new

                df.to_csv("avaliacoes.csv", index=False)

                # PDF generation + download button
                pdf_bytes = gerar_pdf_bytes(
                    nome_aluno, email_aluno, nivel, data_atual, selections, comentario_professor
                )
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"Relatorio_{nome_aluno.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
