import streamlit as st
import pandas as pd
import io
import re

# ---------- Helper Functions ----------

def normalize_number(value):
    """Convert 1.0 -> 1 , remove spaces"""
    try:
        return str(int(float(value)))
    except:
        return str(value).strip()


def parse_options(option_str):
    """Normalize answers like '1,2', '2.0', ' 3 '"""

    if pd.isna(option_str):
        return set()

    option_str = str(option_str).strip()

    tokens = option_str.split(",") if "," in option_str else [option_str]

    normalized = set()

    for t in tokens:

        t = t.strip()

        if t == "":
            continue

        try:
            normalized.add(str(int(float(t))))
        except:
            normalized.add(t)

    return normalized


def evaluate_answer(student_ans, correct_ans, q_type, marks):

    student_set = parse_options(student_ans)
    correct_set = parse_options(correct_ans)

    if q_type == "AND":
        return marks if student_set == correct_set else 0

    elif q_type == "OR":
        return marks if student_set & correct_set else 0

    else:
        return marks if student_set == correct_set else 0


def read_uploaded_file(file):

    filename = file.name.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(file)

    if filename.endswith((".xls", ".xlsx")):
        return pd.read_excel(file)

    st.error("Unsupported file format")
    return None


def detect_question_columns(df):
    """
    Detect Q columns automatically
    Supports Q1, Q_1, Question1
    """

    q_map = {}

    for col in df.columns:

        match = re.search(r'(\d+)', str(col))

        if match:
            q_no = match.group(1)
            q_map[q_no] = col

    return q_map


def evaluate(students_df, answer_keys):

    question_map = detect_question_columns(students_df)

    results = []

    for _, student in students_df.iterrows():

        student_class = normalize_number(student.get("Class"))
        student_paper = normalize_number(student.get("Paper"))

        row_result = student.copy()

        if (student_class, student_paper) not in answer_keys:

            for q_col in question_map.values():
                row_result[q_col] = 0

            row_result["Total_Marks"] = 0
            results.append(row_result)
            continue

        ans_df = answer_keys[(student_class, student_paper)]

        total_marks = 0

        for _, row in ans_df.iterrows():

            q_no = normalize_number(row["QUESTION_NO"])

            correct_ans = row["ANSWER_KEY"]

            marks = row["MARKS"]

            q_type = str(row.get("QUESTION_TYPE", "NORMAL")).strip().upper()

            if q_no in question_map:

                q_col = question_map[q_no]

                student_ans = student[q_col]

                awarded = evaluate_answer(student_ans, correct_ans, q_type, marks)

                row_result[q_col] = awarded

                total_marks += awarded

        row_result["Total_Marks"] = total_marks

        results.append(row_result)

    return pd.DataFrame(results)


# ---------- Streamlit UI ----------

st.set_page_config(
    page_title="Scholarship Data Evaluation Tool",
    layout="wide"
)

st.title("📊 Scholarship Data Evaluation Tool")

st.markdown(
    "Upload **Answer Options File**, upload **Answer Keys**, and generate evaluated marks."
)

# Step 1

st.header("Step 1: Upload Answer Options File")

student_file = st.file_uploader(
    "Upload Student Answer Options",
    type=["csv", "xls", "xlsx"]
)

# Step 2

st.header("Step 2: Enter Class & Paper Count")

num_classes = st.number_input(
    "Number of Classes",
    min_value=1,
    max_value=20,
    value=2
)

num_papers = st.number_input(
    "Number of Papers per Class",
    min_value=1,
    max_value=20,
    value=2
)

# Step 3

st.header("Step 3: Upload Answer Key Files")

st.markdown(
    f"Upload **{int(num_classes * num_papers)} files** named like `C1P1.xlsx`, `C1P2.csv`"
)

uploaded_keys = st.file_uploader(
    "Upload all answer key files",
    type=["csv", "xls", "xlsx"],
    accept_multiple_files=True
)

# Evaluate

if st.button("🚀 Evaluate Now"):

    if not student_file:

        st.error("Upload student answer file first.")

    elif not uploaded_keys:

        st.error("Upload answer key files.")

    else:

        with st.spinner("Evaluating responses..."):

            students_df = read_uploaded_file(student_file)

            if students_df is None:
                st.stop()

            answer_keys = {}

            for file in uploaded_keys:

                filename = file.name

                try:

                    cls = filename.split("C")[1].split("P")[0]
                    pap = filename.split("P")[1].split(".")[0]

                    cls = normalize_number(cls)
                    pap = normalize_number(pap)

                    df = read_uploaded_file(file)

                    if df is not None:

                        answer_keys[(cls, pap)] = df

                        st.success(f"Loaded {filename}")

                except Exception as e:

                    st.error(f"Error loading {filename}")

            evaluated_df = evaluate(students_df, answer_keys)

            st.success("Evaluation Complete")

            st.dataframe(evaluated_df.head(50))

            output = io.BytesIO()

            with pd.ExcelWriter(output, engine="openpyxl") as writer:

                evaluated_df.to_excel(writer, index=False)

            st.download_button(
                "⬇️ Download Evaluated File",
                data=output.getvalue(),
                file_name="evaluated_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


st.markdown("---")

st.caption("Developed by Omkar • Scholarship Evaluation Tool")
