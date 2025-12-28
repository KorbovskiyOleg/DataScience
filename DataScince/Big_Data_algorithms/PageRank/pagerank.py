#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MapReduce реализация алгоритма PageRank с использованием mrjob
Формат входных данных: node_id\tout_link1,out_link2,...\tcurrent_rank
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
import json


def mapper_distribute_rank(_, line):
    """
    Mapper: Распределяет ранг страницы по исходящим ссылкам
    Вход: node\tout_links\tcurrent_rank
    Выход: (target_node, rank_contribution) и (node, graph_info)
    """
    if not line.strip():
        return

    parts = line.strip().split('\t')
    if len(parts) < 2:
        return

    node = parts[0]
    out_links_str = parts[1] if parts[1] else ''
    current_rank = float(parts[2]) if len(parts) > 2 and parts[2] else 1.0

    out_links = [link.strip() for link in out_links_str.split(',') if link.strip()]
    num_links = len(out_links) if out_links else 1

    # Сохраняем информацию о графе (структуру связей)
    # Используем JSON для передачи структурированных данных
    graph_info = json.dumps({
        'type': 'graph',
        'out_links': out_links_str,
        'current_rank': current_rank
    })
    yield node, graph_info

    # Распределяем ранг по исходящим ссылкам
    if out_links:
        rank_per_link = current_rank / num_links
        rank_info = json.dumps({
            'type': 'rank',
            'value': rank_per_link
        })
        for link in out_links:
            yield link, rank_info


class PageRankIteration(MRJob):
    """
    MapReduce реализация одной итерации PageRank
    """
    
    def configure_args(self):
        super(PageRankIteration, self).configure_args()
        self.add_passthru_arg(
            '--damping',
            type=float,
            default=0.85,
            help='Damping factor (обычно 0.85)'
        )

    def reducer_collect_rank(self, node, values):
        """
        Reducer: Собирает входящие ранги и вычисляет новый PageRank
        Выход: node\tout_links\tnew_rank
        """
        graph_data = None
        total_incoming_rank = 0.0
        
        for value_str in values:
            try:
                value = json.loads(value_str)
                
                if value.get('type') == 'graph':
                    # Сохраняем структуру графа
                    graph_data = value.get('out_links', '')
                elif value.get('type') == 'rank':
                    # Суммируем входящие ранги
                    total_incoming_rank += float(value.get('value', 0.0))
            except (json.JSONDecodeError, ValueError, KeyError):
                # Если не JSON, пытаемся обработать как старый формат
                if isinstance(value_str, str) and value_str.startswith('graph'):
                    # Старый формат
                    pass
                else:
                    try:
                        total_incoming_rank += float(value_str)
                    except ValueError:
                        pass
        
        # Вычисляем новый PageRank
        # Формула: PR(A) = (1-d) + d * (сумма входящих рангов)
        damping = float(self.options.damping)
        new_rank = (1 - damping) + damping * total_incoming_rank
        
        # Формируем выход для следующей итерации
        out_links = graph_data if graph_data else ''
        # Используем пустую строку вместо None, чтобы избежать вывода "None" или "null"
        yield '', f"{node}\t{out_links}\t{new_rank}"
    
    def steps(self):
        """Определение шагов MapReduce"""
        return [
            MRStep(
                mapper=mapper_distribute_rank,
                reducer=self.reducer_collect_rank
            )
        ]


if __name__ == '__main__':
    PageRankIteration.run()

