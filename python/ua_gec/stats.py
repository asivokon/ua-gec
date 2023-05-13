#!/usr/bin/env python3
import argparse
import collections

from functools import cache


class CorpusStatistics:
    """Compute corpus statistics. """

    def __init__(self, corpus):
        self.corpus = corpus
        self.stats = {}
        self.layer = self.corpus.annotation_layer.value
        self.compute()

    def compute(self):
        all_docs = self.corpus.get_documents()  # annotated by all annotators
        docs = [doc for doc in all_docs if doc.meta.annotator_id == 1]  # unique source docs

        self.stats["Total"] = {}
        self.stats["Total"]["All"] = self._subset_stats(docs)
        self.stats["By gender"] = self._breakdown(docs, "gender")
        self.stats["By region"] = self._breakdown(docs, "region")
        self.stats["By native"] = self._breakdown(docs, "is_native")
        self.stats["By occupation"] = self._breakdown(docs, "occupation")
        self.stats["By submission type"] = self._breakdown(docs, "submission_type")
        self.stats["By translation lang"] = self._breakdown(docs, "source_language")
        self.stats["Number of errors (by 2 annotators)"] = self._count_errors(all_docs)
        self.stats["Error rate"] = self._error_rate(all_docs)
        del self.stats['By translation lang']['']

    def _subset_stats(self, docs):
        stats = {}
        stats["Documents"] = len(docs)
        stats["Sentences"] = sum(self.count_source_sentences(doc) for doc in docs)
        stats["Tokens"] = sum(self.count_tokens(doc) for doc in docs)
        stats["Unique users"] = len(set(doc.meta.author_id for doc in docs))

        return stats

    def reset_stats(self):
        pass

    def pretty_print(self):
        for top_key, subset in sorted(self.stats.items()):
            print(f"# {top_key}")
            for key, value in subset.items():
                print(f"{key:<30} {value}")
            print()

    def print_tables(self):
        self._error_types_table()

    def _error_types_table(self):
        stats = self.stats["Number of errors (by 2 annotators)"]
        total_errors = stats["TOTAL"]
        all_docs = self.corpus.get_documents()  # annotated by all annotators
        total_tokens = sum(self.count_tokens(doc) for doc in all_docs)

        # header
        print(r"""\begin{table}[ht]
\centering
\begin{tabular}{lrcc}
\hline \textbf{Error type} & \textbf{Total}  & \textbf{\%} & \textbf{\raisebox{4pt}[13pt][8pt]{\vtop{\hbox{Per 1000}\hbox{tokens}}}} \\ \hline""")

        def print_row(error_type, count):
            pct = count / total_errors * 100
            per_1000_tokens = count / total_tokens * 1000
            print(f"{error_type:<30} & {count:>6,} & {pct:.1f} & {per_1000_tokens:.1f} \\\\")


        # high-level categories
        hl_fluency = sum(value for key, value in stats.items() if key.startswith("F/"))
        hl_grammar = sum(value for key, value in stats.items() if key.startswith("G/"))
        print_row("Grammar (all)", hl_grammar)
        print_row("Fluency (all)", hl_fluency)
        print_row("Spelling", stats["Spelling"])
        print_row("Punctuation", stats["Punctuation"])
        print(r"\hline")

        # detailed categories
        for key, value in sorted(stats.items()):
            if key in ("Spelling", "Punctuation"):
                continue
            print_row(key, value)

        # footer
        print(r"""\hline
\end{tabular}
\caption{\label{error-categories} Error distribution by category }
\end{table}""")

    @cache
    def count_source_sentences(self, doc):
        with open(f"./data/{self.layer}/{doc.meta.partition}/source-sentences-tokenized/{doc.doc_id}.src.txt") as f:
            content = f.read()
            sents = [s for s in content.split("\n") if s.strip()]
            return len(sents)

    @cache
    def count_tokens(self, doc):
        with open(f"./data/{self.layer}/{doc.meta.partition}/source-sentences-tokenized/{doc.doc_id}.src.txt") as f:
            content = f.read()
            tokens = content.split()
            return len(tokens)

    def _breakdown(self, docs, field):
        """Compute statistics with breakdown by `field`.

        Returns:
            dict: field_class (str) => stats (dict[str, int])
        """

        result = {}
        values = sorted({getattr(doc.meta, field) for doc in docs})

        for value in values:
            subset = [doc for doc in docs if getattr(doc.meta, field) == value]
            result[value] = self._subset_stats(subset)

        return result
    
    def _count_errors(self, docs):
        """Compute number of error annotations in the given docs. """

        errors = collections.Counter()
        for doc in docs:
            for ann in doc.annotated.get_annotations():
                try:
                    errors[ann.meta["error_type"]] += 1
                except KeyError:
                    print(doc.doc_id)
                    print(ann)
                    errors["MISSING"] += 1
                    #raise
                    continue
                errors["TOTAL"] += 1
        return dict(sorted(errors.items()))
    
    def _error_rate(self, docs):
        """Compute average number of errors per token.

        When a document is annotated with two annotators, take average of the two.
        """

        total_errors = 0
        total_tokens = 0
        for doc in docs:
            total_errors += len(doc.annotated.get_annotations())
            total_tokens += self.count_tokens(doc)

        return {
            "Total errors": total_errors,
            "Total tokens": total_tokens,
            "Error rate": round(total_errors / total_tokens, 4),
        }



def main(args):
    from ua_gec import Corpus
    corpus = Corpus(args.partition, args.layer)
    stats = CorpusStatistics(corpus)

    if not args.tables:
        stats.pretty_print()
    else:
        stats.print_tables()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("partition", choices=["all", "train", "test"])
    parser.add_argument("layer", choices=["gec-fluency", "gec-only"])
    parser.add_argument("--tables", action="store_true", help="Print latex tables")
    args = parser.parse_args()
    main(args)
