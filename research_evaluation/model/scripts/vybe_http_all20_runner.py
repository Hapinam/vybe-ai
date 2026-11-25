#!/usr/bin/env python3
"""Run the unchanged VYBE local HTTP 12-case benchmark across remaining Ollama models.
Uses the original vybe_http_local_qwen_v1.py as-is. No Azure/GitHub mutations.
"""
import argparse
import csv
import json
import pathlib
import subprocess
import sys
import urllib.request

MODELS = [
    'granite4.2:8b-q4_K_M', 'pplx-decider:latest', 'd1:latest',
    'kev:latest', 'clef-flash:latest', 'nimble:latest', 'd3:4b',
    'tev1:4b', 'phi4-reasoning:14b-plus-q8_0',
    'deepseek-r1:14b-qwen-distill-q8_0', 'nemotron-3.5-bolt:e4b',
    'nemotron-3-nano:4b', 'qwen3.8:27b', 'gemma4:26b',
    'nemotron-3-nano-gpu:latest', 'gpt-oss:20b',
    'ministral-3:14b-instruct-2512-q4_K_M',
    'gemma4:12b-it-q4_K_M', 'qwen3.5:9b',
]
QWEN = 'qwen3-coder:30b'
FIELDS = ['case_id','model','question','expected_tool','expected_supported','http_status',
          'selected_tool','supported','generation_mode','evidence_ids','answer',
          'observed_calls','selection_error','latency_s','verdict']

def rows_from(path, model):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 12 or [r['case_id'] for r in rows] != [f'H{i:02d}' for i in range(1,13)]:
        raise ValueError(f'{path}: expected exactly H01-H12, got {len(rows)} rows')
    if any(r['model'] != model for r in rows):
        raise ValueError(f'{path}: wrong model in results')
    return rows

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True)
    p.add_argument('--timeout', type=int, default=180)
    p.add_argument('--script', default='vybe_http_local_qwen_v1.py', help='Unmodified original HTTP benchmark')
    p.add_argument('--qwen-csv', default='vybe_http_local_qwen_v1_results.csv')
    p.add_argument('--outdir', default='vybe_http_all20_results')
    p.add_argument('--rerun', action='store_true', help='Rerun existing complete model CSVs')
    args = p.parse_args()
    script = pathlib.Path(args.script).resolve()
    if not script.is_file(): p.error(f'Missing original benchmark: {script}')
    outdir = pathlib.Path(args.outdir).resolve(); outdir.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen('http://127.0.0.1:11434/api/tags', timeout=5) as r:
            tags = json.load(r)
        installed = {m['name'] for m in tags.get('models', [])}
    except Exception as e:
        p.error(f'Cannot reach Ollama: {e}')
    all_rows = []
    errors = []
    qwen_csv = pathlib.Path(args.qwen_csv).resolve()
    if qwen_csv.is_file():
        try: all_rows.extend(rows_from(qwen_csv, QWEN))
        except Exception as e: errors.append(f'Qwen previous CSV invalid: {e}')
    else:
        errors.append(f'Qwen previous CSV missing: {qwen_csv}; Qwen will not be rerun')

    for i, model in enumerate(MODELS, 1):
        path = outdir / f'model_{i:02d}.csv'
        if model not in installed:
            errors.append(f'{model}: NOT_INSTALLED (skipped; no automatic pull)')
            print(f'[{i:02d}/19] SKIP not installed: {model}', flush=True)
            continue
        if path.is_file() and not args.rerun:
            try:
                rows = rows_from(path, model)
                all_rows.extend(rows)
                print(f'[{i:02d}/19] REUSE {model}: {sum(r["verdict"]=="PASS" for r in rows)}/12', flush=True)
                continue
            except Exception as e:
                errors.append(f'{model}: prior file invalid ({e}); rerunning')
        print(f'\n[{i:02d}/19] RUN {model}', flush=True)
        cmd = [sys.executable, str(script), '--repo', args.repo, '--model', model,
               '--timeout', str(args.timeout), '--output', str(path)]
        try:
            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                errors.append(f'{model}: benchmark exited {result.returncode}')
            if path.is_file():
                rows = rows_from(path, model)
                all_rows.extend(rows)
                print(f'[{i:02d}/19] DONE {model}: {sum(r["verdict"]=="PASS" for r in rows)}/12', flush=True)
            else:
                errors.append(f'{model}: no CSV produced')
        except KeyboardInterrupt:
            print('\nInterrupted; completed model CSVs preserved. Rerun same command to resume.', flush=True)
            break
        except Exception as e:
            errors.append(f'{model}: {type(e).__name__}: {e}')
            print(f'[{i:02d}/19] ERROR {model}: {e}', flush=True)
    combined = outdir / 'vybe_http_all20_combined.csv'
    with combined.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(all_rows)
    summary = outdir / 'vybe_http_all20_summary.csv'
    with summary.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['model','cases','pass','review','http_non_200','selection_errors','warm_median_s'])
        for model in [QWEN] + MODELS:
            rows = [r for r in all_rows if r['model']==model]
            if not rows: continue
            times = sorted(float(r['latency_s']) for r in rows if r['case_id']!='H01' and r['latency_s'])
            median = times[len(times)//2] if len(times)%2 else (times[len(times)//2-1]+times[len(times)//2])/2 if times else ''
            w.writerow([model,len(rows),sum(r['verdict']=='PASS' for r in rows),sum(r['verdict']!='PASS' for r in rows),
                        sum(r['http_status']!='200' for r in rows),sum(bool(r['selection_error']) for r in rows),median])
    log = outdir / 'vybe_http_all20_run_notes.txt'
    log.write_text('\n'.join(errors) if errors else 'No runner-level errors.', encoding='utf-8')
    print(f'\nCombined: {combined}\nSummary: {summary}\nRun notes: {log}\nRows: {len(all_rows)}/240', flush=True)
    print('LIMITS: HTTP FastAPI with temporary local Ollama adapter; synthetic match; no Azure or frontend; PASS is not a security certification.', flush=True)

if __name__ == '__main__': main()
