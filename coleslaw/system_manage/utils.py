from django.http.response import HttpResponse
from django.db.models.query import QuerySet
from PIL import ImageOps, Image, ImageFile

from io import BytesIO
import urllib.parse
import pandas as pd

ImageFile.LOAD_TRUNCATED_IMAGES = True

def resize_with_padding(img, expected_size=(1280, 1280), fill=(255,255,255)):
    '''
        Pillow > 10.0.0 (Image.Resampling.LANCZOS)
        Pillow < 10.0.0 (Image.ANTIALIAS)
    '''

    img.thumbnail((expected_size[0], expected_size[1]), Image.Resampling.LANCZOS)

    delta_width = expected_size[0] - img.size[0]
    delta_height = expected_size[1] - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2

    padding = (
        pad_width,
        pad_height,
        delta_width - pad_width,
        delta_height - pad_height,
    )
    img = img.convert("RGBA")
    return ImageOps.expand(img, padding, fill=fill)

class ResponseToXlsx:
    def __init__(self,columns:list, queryset:QuerySet):
        self.table = pd.DataFrame(queryset)
        self.table.columns = columns

    def addData(self,index:int, column:str, data:list):
        self.table.insert(index,column,data)

    def download(self, filename:str):
        with BytesIO() as b:
            writer = pd.ExcelWriter(b,engine="xlsxwriter")
            self.table.to_excel(writer, sheet_name=filename, index=False)
            writer.close()

            response = HttpResponse(b.getvalue())
            response["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s.xlsx' % urllib.parse.quote(filename.encode('utf-8'))

        return response    