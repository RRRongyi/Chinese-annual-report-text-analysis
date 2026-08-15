import argparse
import math
import re
from pathlib import Path

import jieba
import pandas as pd


def read_list(path):
    if not path:
        return set()
    last_error = None
    for encoding in ("utf-8-sig", "gb18030", "gbk"):
        try:
            with open(path, encoding=encoding) as f:
                return {x.strip() for x in f if x.strip()}
        except UnicodeDecodeError as exc:
            last_error = exc
    raise last_error


def clean_text(text):
    text = str(text or "")
    text = re.sub(r"<[^>]+>|https?://\S+|www\.\S+|\S+@\S+", " ", text)
    text = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9。！？；.!?;]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text):
    return [x.strip() for x in re.split(r"[。！？；.!?;]+", text) if x.strip()]


def valid_tokens(text, stopwords):
    out = []
    for word in jieba.lcut(text):
        word = word.strip()
        if word and word not in stopwords and re.search(r"[\u4e00-\u9fa5A-Za-z0-9]", word):
            if not (len(word) == 1 and re.search(r"[\u4e00-\u9fa5]", word)):
                out.append(word)
    return out


def analyze(text, target, stopwords):
    text = clean_text(text)
    ss = split_sentences(text)
    tokens = valid_tokens(text, stopwords)
    target_count = sum(x in target for x in tokens)
    # Sentence frequency only asks whether a target term occurs in a sentence.
    # Direct phrase matching avoids re-running jieba for every sentence.
    target_ss = sum(any(term in s for term in target) for s in ss)
    total_words, total_ss = len(tokens), len(ss)
    return {
        "total_words": total_words,
        "target_words": target_count,
        "log_target_words": math.log1p(target_count),
        "target_word_ratio": target_count / total_words if total_words else 0,
        "total_sentences": total_ss,
        "target_sentences": target_ss,
        "log_target_sentences": math.log1p(target_ss),
        "target_sentence_ratio": target_ss / total_ss if total_ss else 0,
    }


def records_from_input(path):
    p = Path(path)
    if p.is_file() and p.suffix.lower() in {".xlsx", ".xls", ".csv"}:
        df = pd.read_csv(p) if p.suffix.lower() == ".csv" else pd.read_excel(p)
        text_col = next((c for c in ["text", "content", "正文", "文本"] if c in df), None)
        if text_col is None:
            raise ValueError("Excel/CSV必须包含 text、content、正文或文本列")
        return [(str(r.get("company", r.get("企业", ""))), r.get("year", r.get("年份", "")), str(r[text_col]), p.name) for _, r in df.iterrows()]
    files = sorted(x for x in p.rglob("*") if x.suffix.lower() == ".txt")
    rows = []
    for f in files:
        text = f.read_text(encoding="utf-8-sig", errors="replace")
        year = next(iter(re.findall(r"(?:19|20)\d{2}", f.stem)), "")
        rows.append((f.stem, year, text, f.name))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--target-dict", required=True)
    ap.add_argument("--stopwords")
    ap.add_argument("--protect-dict", "--user-dict", dest="protect_dict")
    ap.add_argument("--output", default="text_analysis_results.xlsx")
    args = ap.parse_args()
    target, stop = read_list(args.target_dict), read_list(args.stopwords)
    for word in read_list(args.protect_dict):
        jieba.add_word(word)
    results = []
    for company, year, text, name in records_from_input(args.input):
        try:
            results.append({"company": company, "year": year, "file_name": name, "status": "ok", **analyze(text, target, stop)})
        except Exception as e:
            results.append({"company": company, "year": year, "file_name": name, "status": "error", "error_message": str(e)})
    pd.DataFrame(results).to_excel(args.output, index=False)
    print(f"完成：{len(results)} 个文件，结果已保存至 {args.output}")


if __name__ == "__main__":
    main()
