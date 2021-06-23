class SearchOperator:
    LIKE = 'LIKE'
    LIKE_BEGIN = 'LIKE_BEGIN'
    EQUAL = 'EQ'
    GREATER_EQUAL = 'GE'
    LESS_EQUAL = 'LE'
    GREATER = 'GT'
    LESS = 'LT'
    IN_LIST = 'LIST'
    SIMILAR_EQUAL = 'SEQ'

    def get_list(self):
        return ['LIKE', 'LIKE_BEGIN', 'EQ', 'GE', 'LE', 'GT', 'LT', 'LIST', 'SEQ']
