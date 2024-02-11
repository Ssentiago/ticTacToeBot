from aiogram.filters import Filter


class FilterCellsCBData(Filter):
    def __init__(self, obj):
        self.obj = eval(obj.data)

    def __call__(self, *args, **kwargs):
        return self.obj.__class__ == tuple
