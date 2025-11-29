import subprocess
import os
import glob

DATA_DIR = "data"
TF_OUTPUT = "tf_output.txt"
TFIDF_OUTPUT = "tfidf_output.txt"


def run_cmd(cmd):
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    txt_files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    if not txt_files:
        print("Нет входных файлов!")
        return

    # 1. TF
    run_cmd(["python", "tf_job.py", DATA_DIR + "/*.txt", ">", TF_OUTPUT])

    # 2. TF-IDF
    total_docs = str(len(txt_files))
    run_cmd(["python", "tfidf_job.py", TF_OUTPUT, "--total_docs", total_docs, ">", TFIDF_OUTPUT])

    print("Готово!")
    print("Результаты в", TFIDF_OUTPUT)


if __name__ == "__main__":
    main()
