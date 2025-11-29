from mrjob.job import MRJob
import math
import json
import sys


class TFIDFJob(MRJob):

    def configure_args(self):
        super().configure_args()
        self.add_passthru_arg('--total_docs', type=int)

    def mapper(self, _, line):
        try:
            # Формат: JSON_KEY\tVALUE
            if '\t' in line:
                key_str, value_str = line.strip().split('\t', 1)

                # Парсим ключ и значение как JSON
                key = json.loads(key_str)  # ["filename", "word"]
                value = json.loads(value_str)  # count

                filename, word = key
                tf = value

                yield word, (filename, tf)

        except Exception as e:
            # Выводим ошибки в stderr для отладки
            print(f"ERROR: {e} in line: {line}", file=sys.stderr)

    def reducer(self, word, values):
        values = list(values)
        df = len(values)  # document frequency
        N = self.options.total_docs

        # Вычисляем IDF
        idf = math.log(N / df) if df > 0 and N > 0 else 0

        for filename, tf in values:
            tfidf = tf * idf
            yield filename, (word, round(tfidf, 4))


if __name__ == '__main__':
    TFIDFJob.run()



