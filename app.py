import streamlit as st
import pandas as pd
import os
import io

# ---------- Helper Functions ----------
def parse_options(option_str):
    """Normalize options like '1,2', '2.0' → {'1','2'}."""
    if pd.isna(option_str):
        return set()
    option_str = str(option_str).strip()
    tokens = [o.strip() for o in option_str.split(",")] if "," in option_str else [option_str]

    normalized = set()
    for t in tokens:
        if t == "":
            continue
        try:
            num = float(t)
            normalized.add(str(int(num)) if num.is_integer() else str(num))
        except ValueError:
            normalized.add(t)
    return normalized


def evaluate_answer(student_ans, correct_ans, q_type, marks):
    """Return marks according to question type."""
    student_set = parse_options(student_ans)
    correct_set = parse_options(correct_ans)

    if q_type == "AND":
        return marks if student_set == correct_set else 0
    elif q_type == "OR":
        return marks if (student_set & correct_set) else 0
    else:  # NORMAL
        return marks if student_set == correct_set else 0


def read_uploaded_file(file):
    """Reads uploaded file (CSV or Excel) and returns a pandas DataFrame."""
    filename = file.name.lower()
    try:
        if filename.endswith(".csv"):
            return pd.read_csv(file)
        elif filename.endswith((".xls", ".xlsx")):
            return pd.read_excel(file)
        else:
            st.error(f"❌ Unsupported file format for {filename}. Please upload CSV or Excel.")
            return None
    except Exception as e:
        st.error(f"⚠️ Error reading {filename}: {e}")
        return None


def evaluate(students_df, answer_keys):
    """Evaluate student responses against answer keys."""
    all_question_cols = [c for c in students_df.columns if c.startswith("Q_")]
    results = []

    for idx, student in students_df.iterrows():
        student_class = str(student.get("Class", "")).strip()
        student_paper = str(student.get("Paper", "")).strip()
        row_result = student.copy()

        if (student_class, student_paper) not in answer_keys:
            # Invalid combination → give zero marks
            for q_col in all_question_cols:
                row_result[q_col] = 0
            row_result["Total_Marks"] = 0
            results.append(row_result)
            continue

        ans_df = answer_keys[(student_class, student_paper)]
        ans_df["QUESTION_NO"] = ans_df["QUESTION_NO"].astype(str)
        total_marks = 0

        for _, row in ans_df.iterrows():
            q_no = str(row["QUESTION_NO"]).strip()
            correct_ans = row["ANSWER_KEY"]
            marks = row["MARKS"]
            q_type = str(row.get("QUESTION_TYPE", "")).strip().upper() or "NORMAL"

            q_col = f"Q_{q_no}"
            if q_col in students_df.columns:
                awarded = evaluate_answer(student[q_col], correct_ans, q_type, marks)
                row_result[q_col] = awarded
                total_marks += awarded
            else:
                st.warning(f"Missing column '{q_col}' for Question {q_no} in student file.")

        row_result["Total_Marks"] = total_marks
        results.append(row_result)

    final_df = pd.DataFrame(results)
    return final_df


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Dynamic Student Evaluation Tool", layout="wide")

st.title("📊 Dynamic Student Evaluation System")
st.markdown("Upload student responses and corresponding answer keys (Excel or CSV) to automatically evaluate marks.")

# --- Upload Student File ---
st.header("Step 1: Upload Student Response File")
student_file = st.file_uploader("Upload the student file (CSV or Excel)", type=["csv", "xls", "xlsx"])

# --- Input Classes and Papers ---
st.header("Step 2: Enter Class & Paper Count")
num_classes = st.number_input("Number of Classes", min_value=1, max_value=20, value=2, step=1)
num_papers = st.number_input("Number of Papers per Class", min_value=1, max_value=20, value=2, step=1)

# --- Upload Answer Keys ---
st.header("Step 3: Upload Answer Key Files (CnPn.csv / .xlsx)")
st.markdown(f"👉 You need to upload **{int(num_classes * num_papers)} answer key files**, named as `C1P1.csv`, `C1P2.xlsx`, ... etc.")

uploaded_keys = st.file_uploader(
    "Upload all answer key files together",
    type=["csv", "xls", "xlsx"],
    accept_multiple_files=True
)

# --- Evaluate Button ---
if st.button("🚀 Evaluate Now"):
    if not student_file:
        st.error("Please upload the student response file first.")
    elif not uploaded_keys:
        st.error("Please upload all answer key files.")
    else:
        with st.spinner("Processing and evaluating..."):
            students_df = read_uploaded_file(student_file)
            if students_df is None:
                st.stop()

            # Load all uploaded answer keys dynamically
            answer_keys = {}
            for file in uploaded_keys:
                filename = file.name
                try:
                    cls = filename.split("C")[1].split("P")[0]
                    pap = filename.split("P")[1].split(".")[0]
                    df = read_uploaded_file(file)
                    if df is not None:
                        answer_keys[(cls.strip(), pap.strip())] = df
                        st.success(f"✅ Loaded {filename}")
                except Exception as e:
                    st.error(f"❌ Error reading {filename}: {e}")

            # Run evaluation
            evaluated_df = evaluate(students_df, answer_keys)

            # Display results
            st.success("✅ Evaluation complete!")
            st.dataframe(evaluated_df.head(50))

            # Convert to downloadable Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                evaluated_df.to_excel(writer, index=False, sheet_name="Evaluated Results")
            st.download_button(
                label="⬇️ Download Evaluated File (Excel)",
                data=output.getvalue(),
                file_name="evaluated_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

st.markdown("---")
st.caption("Developed by Omkar • Excel-Compatible Dynamic Evaluation Tool")
