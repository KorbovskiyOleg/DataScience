#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TF*IDF MapReduce Implementation
Реализация алгоритма TF*IDF с использованием MRJob

Алгоритм состоит из нескольких шагов:
1. Подсчет TF (Term Frequency) - частота термина в документе
2. Подсчет DF (Document Frequency) - количество документов с термином  
3. Вычисление IDF = log(N/DF), где N - общее количество документов
4. Вычисление TF*IDF = TF * IDF
5. Ранжирование документов по среднему TF*IDF для поискового запроса
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
import re
import math
import os


class MRTFIDF(MRJob):
    """
    Основной класс для вычисления TF*IDF
    """
    
    def configure_args(self):
        super(MRTFIDF, self).configure_args()
        self.add_passthru_arg('--num-docs', type=int, default=1,
                             help='Общее количество документов')
        self.add_passthru_arg('--query', type=str, default='',
                             help='Поисковый запрос (слова через пробел)')
    
    # ========== ШАГ 1: Подсчет TF (Term Frequency) ==========
    def mapper_tf(self, _, line):
        """Извлекает слова из строки и выдает (doc_id, word) -> 1"""
        # Получаем имя файла из контекста MRJob
        # В Hadoop используется переменная окружения map_input_file
        # В локальном режиме MRJob эмулирует это поведение
        file_path = os.environ.get('map_input_file', '')
        
        # Если переменная окружения не установлена, пытаемся получить другим способом
        if not file_path:
            # В локальном режиме MRJob может не устанавливать эту переменную
            # Используем имя по умолчанию или пытаемся получить из опций
            try:
                if hasattr(self, 'options') and hasattr(self.options, 'input_paths'):
                    if self.options.input_paths:
                        file_path = self.options.input_paths[0] if isinstance(self.options.input_paths, list) else str(self.options.input_paths)
            except:
                pass
        
        # Извлекаем имя файла из пути
        if file_path:
            doc_id = os.path.basename(file_path)
        else:
            # Если не удалось получить имя файла, используем значение по умолчанию
            doc_id = 'unknown'
        
        # Разбиваем строку на слова (только буквы и цифры)
        words = re.findall(r'\b\w+\b', line.lower())
        
        for word in words:
            if len(word) > 0:
                yield (doc_id, word), 1
    
    def reducer_tf(self, key, values):
        """Подсчитывает частоту термина в документе (TF)"""
        doc_id, word = key
        tf = sum(values)
        # Выдаем в формате: (doc_id, word) -> tf
        yield (doc_id, word), tf
    
    # ========== ШАГ 2: Подсчет DF и вычисление TF*IDF ==========
    def mapper_df(self, key, value):
        """
        Преобразует (doc_id, word) -> tf в word -> (doc_id, tf)
        для группировки по словам и вычисления DF
        """
        (doc_id, word), tf = key, value
        yield word, (doc_id, tf)
    
    def reducer_tfidf(self, word, doc_tf_pairs):
        """
        Вычисляет DF, IDF и TF*IDF для каждого документа
        """
        num_docs = self.options.num_docs
        
        # Собираем все пары (doc_id, tf) для данного слова
        doc_tf_list = list(doc_tf_pairs)
        
        # Вычисляем DF (количество уникальных документов с этим словом)
        unique_docs = set(doc_id for doc_id, _ in doc_tf_list)
        df = len(unique_docs)
        
        # Вычисляем IDF
        if df > 0:
            idf = math.log(float(num_docs) / df)
        else:
            idf = 0
        
        # Вычисляем TF*IDF для каждого документа
        for doc_id, tf in doc_tf_list:
            tfidf = tf * idf
            yield (doc_id, word), tfidf
    
    # ========== ШАГ 3: Ранжирование по поисковому запросу ==========
    def mapper_query_score(self, key, value):
        """Фильтрует TF*IDF по словам из поискового запроса"""
        (doc_id, word), tfidf = key, value
        
        query_words = self.options.query.lower().split()
        if word in query_words:
            yield doc_id, tfidf
    
    def reducer_query_score(self, doc_id, tfidf_values):
        """Вычисляет средний TF*IDF для документа по запросу"""
        query_words = self.options.query.lower().split()
        if len(query_words) == 0:
            return
        
        tfidf_list = list(tfidf_values)
        # Средний TF*IDF = сумма TF*IDF по словам запроса / количество слов в запросе
        avg_tfidf = sum(tfidf_list) / len(query_words)
        
        yield None, (avg_tfidf, doc_id)
    
    # ========== ШАГ 4: Сортировка результатов ==========
    def reducer_sort(self, _, values):
        """Сортирует документы по среднему TF*IDF (по убыванию)"""
        results = list(values)
        # Сортируем по убыванию TF*IDF
        results.sort(reverse=True)
        
        for avg_tfidf, doc_id in results:
            yield doc_id, avg_tfidf
    
    def steps(self):
        """Определяет последовательность шагов MapReduce"""
        return [
            # Шаг 1: Подсчет TF
            MRStep(mapper=self.mapper_tf,
                   reducer=self.reducer_tf),
            # Шаг 2: Подсчет DF и вычисление TF*IDF
            MRStep(mapper=self.mapper_df,
                   reducer=self.reducer_tfidf),
            # Шаг 3: Ранжирование по запросу
            MRStep(mapper=self.mapper_query_score,
                   reducer=self.reducer_query_score),
            # Шаг 4: Сортировка
            MRStep(reducer=self.reducer_sort)
        ]


if __name__ == '__main__':
    MRTFIDF.run()
