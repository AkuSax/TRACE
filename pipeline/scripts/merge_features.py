# A robust script to merge all generated features into a single matrix.
import argparse
import pandas as pd
from functools import reduce

def load_and_rename(file_path, id_col, prefix):
    """Loads a TSV, sets index, and prefixes columns."""
    df = pd.read_csv(file_path, sep='\t')
    df = df.rename(columns={id_col: 'sample_id'})
    df = df.set_index('sample_id')
    df.columns = [f"{prefix}_{c}" for c in df.columns]
    return df

def main(args):
    """Merges all feature files into a single matrix."""
    # Start with the main sample sheet
    base_df = pd.read_csv(args.sample_sheet, sep='\t').set_index('sample_id')
    all_dfs = [base_df]

    # Process each type of feature file
    if args.frag_summaries:
        # Conceptual: parse frag_summary files
        pass # Add parsing logic here
    
    if args.ichor_summaries:
        # ichorCNA params.txt is not a clean TSV, requires custom parsing
        ichor_data = []
        for f in args.ichor_summaries:
            sample_id = f.split('/')[-3]
            tf = 0.0
            with open(f) as fh:
                for line in fh:
                    if "Tumor Fraction" in line:
                        tf = float(line.strip().split(': ')[1])
                        break
            ichor_data.append({'sample_id': sample_id, 'ichor_TF': tf})
        if ichor_data:
            all_dfs.append(pd.DataFrame(ichor_data).set_index('sample_id'))

    if args.meth_props:
        meth_dfs = [load_and_rename(f, 'sample_id', 'meth_prop') for f in args.meth_props]
        if meth_dfs:
            all_dfs.append(pd.concat(meth_dfs))

    if args.meth_qc:
        qc_dfs = [load_and_rename(f, 'sample_id', 'meth_qc') for f in args.meth_qc]
        if qc_dfs:
            all_dfs.append(pd.concat(qc_dfs))
            
    if args.dl_features:
        dl_dfs = [load_and_rename(f, 'sample_id', 'dl') for f in args.dl_features]
        if dl_dfs:
            all_dfs.append(pd.concat(dl_dfs))

    # Merge all dataframes on the sample_id index
    # Using reduce for a clean, sequential join
    final_df = reduce(lambda left, right: pd.merge(left, right, on='sample_id', how='left'), all_dfs)

    # Add pipeline version for provenance
    final_df['trace_pipeline_version'] = args.version
    
    final_df.to_csv(args.output, sep='\t', index=True)
    print(f"Successfully merged {len(final_df)} samples into {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature Merger for TRACE.")
    parser.add_argument("--sample_sheet", required=True)
    parser.add_argument("--frag_summaries", nargs='*')
    parser.add_argument("--ichor_summaries", nargs='*')
    parser.add_argument("--meth_props", nargs='*')
    parser.add_argument("--meth_qc", nargs='*')
    parser.add_argument("--dl_features", nargs='*')
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args)