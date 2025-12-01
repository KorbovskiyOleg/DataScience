from mrjob.job import MRJob
import json
import sys


class TFSearchJob(MRJob):

    def configure_args(self):
        super().configure_args()
        self.add_passthru_arg('--query', type=str, help='Search query')

    def mapper(self, _, line):
        try:
            # Формат: JSON_KEY\tVALUE (такой же как в tfidf_job.py)
            if '\t' in line:
                key_str, value_str = line.strip().split('\t', 1)

                # Парсим ключ и значение как JSON
                key = json.loads(key_str)  # ["filename", "word"]
                value = json.loads(value_str)  # count (TF)

                filename, word = key
                tf = value

                # Получаем поисковый запрос
                query_words = [w.lower() for w in self.options.query.split() if w.isalpha()]

                # Если слово из запроса есть в документе
                if word.lower() in query_words:
                    yield filename, (word, tf)

        except Exception as e:
            print(f"ERROR: {e} in line: {line}", file=sys.stderr)

    def reducer(self, filename, values):
        values = list(values)
        total_tf = 0
        found_words = []

        for word, tf in values:
            total_tf += tf
            found_words.append(word)

        # Средний TF по найденным словам
        if found_words:
            avg_tf = total_tf / len(found_words)
            yield filename, (avg_tf, found_words)


if __name__ == '__main__':
    TFSearchJob.run()