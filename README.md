# Scholarship-Data-Evaluation-App

Scholarship Data Evaluation Tool
User Manual
Tool Link: https://o2-cholarship-data-evaluation-app2.streamlit.app/
Purpose of the Tool
The Scholarship Data Evaluation Tool is developed to evaluate student response data when scholarship exam data
cannot be processed directly on servers or through Excel due to data volume or complexity.
In such cases, OSCAN software is used to scan OMR sheets and generate a Student Response file. However,
OSCAN does not generate a student marks file automatically. This tool evaluates student responses against answer
keys and generates an evaluated marks file.
Supported File Formats
• CSV
• XLSX
• XLSM
How to Use the Tool
Step 1: Upload Student Response File
Upload the Student Response file generated from OSCAN. This file is referred to as the Answer Options file and
contains student responses along with identifiers such as Class, Paper, and Roll Number.
Step 2: Upload Answer Key Files
Upload the required Answer Key files for the exam. The tool automatically determines how many answer keys are
required based on the number of classes and papers.
Criteria
Description
Answer Key Count
Number of Classes × Number of Papers
Example
Answer Key Naming Convention
Each answer key file must follow the format:
C<ClassNumber>P<PaperNumber>
Examples: C1P1, C1P2, C2P1, C2P2
Step 3: Start Evaluation
2 Classes × 2 Papers = 4 Answer Keys
After uploading the Student Response file and all required Answer Key files, click Start Evaluation. The tool
evaluates responses and calculates student-wise marks.
Step 4: Download Evaluated Output
Once evaluation is complete, download the Evaluated Student Response file (Answer Marks file) for further analysis
and reporting.
Output Generated
• Evaluated Student Response File (Answer Marks File)
• Ready for scholarship analysis, reporting, and verification
Important Notes
• Ensure all required answer keys are uploaded
• Follow answer key naming conventions strictly
• Use supported file formats only
