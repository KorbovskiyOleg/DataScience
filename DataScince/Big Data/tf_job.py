from mrjob.job import MRJob
from mrjob.step import MRStep
import os
import re

WORD_RE = re.compile(r"[A-Za-zА-Яа-я0-9]+")


class TFJob(MRJob):

    def mapper(self, _, line):
        filename = os.environ.get('map_input_file', 'unknown')
        filename = os.path.basename(filename)

        for word in WORD_RE.findall(line.lower()):
            yield (filename, word), 1

    def reducer(self, key, values):
        yield key, sum(values)


if __name__ == '__main__':
    TFJob.run()




