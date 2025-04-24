#!/usr/bin/env python3
import os
import re
import glob
import argparse
import json

def numeric_sort_key(path: str):
    base = os.path.splitext(os.path.basename(path))[0]
    m = re.match(r"(\d+)", base)
    return int(m.group(1)) if m else base

def extract_metrics(file_path: str) -> dict:
    metrics = {
        "All Objects Within Room Bounds": None,
        "Objects Not Overlap": None,
        "Overall Layout Quality": None,
        "Functionality of the Layout": None,
        "Ergonomic Placements": None,
        "Readiness to Pay": None,
    }
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    rating_section = re.split(r"###\s*Ratings:", content, flags=re.IGNORECASE)
    if len(rating_section) < 2:
        print(f"Ratings section not found in {file_path}")
        return None
    ratings_text = rating_section[1]
    
    for key in metrics.keys():
        pattern = re.compile(re.escape(key) + r":\s*([\d.]+)", re.IGNORECASE)
        m = pattern.search(ratings_text)
        if m:
            try:
                metrics[key] = float(m.group(1))
            except ValueError:
                metrics[key] = 0.0
        else:
            print(f"Warning: '{key}' not found in {file_path}. Setting to 0.")
            metrics[key] = 0.0
    
    total = sum(metrics.values())
    final_grade = total / 6.0  
    metrics["Final Grade"] = final_grade
    
    return metrics

def main():
    parser = argparse.ArgumentParser(description="Collect metrics from evaluation files and build a summary table.")
    parser.add_argument("--eval_dir", type=str, required=True, help="Path to evaluations folder containing evaluation text files")
    parser.add_argument("--output_file", type=str, default="metrics.txt", help="Filename for the summary table (saved in the evaluations folder)")
    args = parser.parse_args()
    
    eval_dir = args.eval_dir
    output_file = os.path.join(eval_dir, args.output_file)
    file_pattern = os.path.join(eval_dir, "*.txt")
    eval_files = sorted(glob.glob(file_pattern), key=numeric_sort_key)
    
    if not eval_files:
        print(f"No evaluation files found in {eval_dir}")
        return
        
    rows = []
    
    for file_path in eval_files:
        print(f"Processing {file_path}...")
        metrics = extract_metrics(file_path)
        if metrics is not None:
            row = {"File": os.path.basename(file_path)}
            row.update(metrics)
            rows.append(row)
    
    if not rows:
        print("No valid metrics found.")
        return
    
    columns = [
        "File",
        "All Objects Within Room Bounds": None,
        "Objects Not Overlap": None,
        "Overall Layout Quality": None,
        "Functionality of the Layout": None,
        "Ergonomic Placements": None,
        "Readiness to Pay": None,
        "Final Grade"
    ]
    
    averages = {"File": "AVERAGE"}
    for col in columns[1:]:
        avg = sum(row[col] for row in rows) / len(rows)
        averages[col] = avg
    
   
    col_widths = {}
    for col in columns:
        max_len = max(len(str(row.get(col, ""))) for row in rows + [averages])
        col_widths[col] = max(len(col), max_len) + 2  # add some padding
    
    header = "".join(str(col).ljust(col_widths[col]) for col in columns)
    sep = "-" * len(header)
    table_lines = [header, sep]
    
    for row in rows:
        line = "".join(str(round(row.get(col), 3) if isinstance(row.get(col), float) else row.get(col)).ljust(col_widths[col]) for col in columns)
        table_lines.append(line)
    
    avg_line = "".join(str(round(averages.get(col), 3) if isinstance(averages.get(col), float) else averages.get(col)).ljust(col_widths[col]) for col in columns)
    table_lines.append(sep)
    table_lines.append(avg_line)
    
    table_text = "\n".join(table_lines)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(table_text)
    
    print(f"Metrics table saved to {output_file}")
    print("\n" + table_text)

if __name__ == "__main__":
    main()