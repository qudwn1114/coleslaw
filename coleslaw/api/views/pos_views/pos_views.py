from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.db.models import CharField, F, Value as V, Func, Case, When, Prefetch, Sum
from django.db import transaction, IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from system_manage.views.system_manage_views.auth_views import validate_phone
from django.utils import timezone, dateformat
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from system_manage.models import ShopTable, Goods, GoodsOption, GoodsOptionDetail, Shop, Checkout, CheckoutDetail, CheckoutDetailOption
from api.views.sms_views.sms_views import send_sms

import traceback, json, datetime, uuid, logging

class ShopPosListView(View):
    '''
        shop pos list api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        try:
            queryset = ShopTable.objects.filter(shop=shop, table_no__lte=0).annotate(
                ).order_by('id').values(
                    'table_no',
                    'name',
                )

            return_data = {
                'data': list(queryset),
                'resultCd': '0000',
                'msg': '가맹점 pos 리스트',
                'totalCnt' : queryset.count()
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': [],
                'msg': '오류!',
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")



class ShopTableAddView(View):
    '''
        상품담기
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableAddView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        goods_id = request.POST['goods_id']
        quantity = int(request.POST['quantity'])
        optionList = request.POST['optionList']
        optionList = json.loads(optionList)
        optionList.sort()

        if quantity <= 0:
            return_data = {'data': {},'msg': 'quantity must larger than 0','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            goods = Goods.objects.get(pk=goods_id, shop=shop_table.shop)
        except:
            return_data = {'data': {},'msg': 'Goods ID 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if goods.soldout:
            return_data = {'data': {},'msg': '품절 상품입니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        optionName = ''
        optionPrice = 0
        for i in optionList:
            try:
                goods_option_detail = GoodsOptionDetail.objects.get(pk=i, goods_option__goods=goods)
            except:
                return_data = {'data': {},'msg': 'Goods Option Error','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            if goods_option_detail.soldout:
                return_data = {'data': {},'msg': f'옵션 {goods_option_detail.name_kr} 품절','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            
            optionName += f'{goods_option_detail.name_kr} / '
            optionPrice += goods_option_detail.price
            
        if optionName:
            optionName = optionName.strip().rstrip('/')

        data = {}
        discount_price = 0
        if shop_table.cart:
            is_new = True
            cart_list = json.loads(shop_table.cart)
            additional_price = 0
            for i in cart_list:
                if i['goodsId'] == goods.pk:
                    # 이미 담긴 상품일때
                    if i['optionList'] == optionList and i['discount'] == 0:
                        is_new = False
                        i['quantity'] += quantity
                        additional_price = quantity * (i['price'] + i['optionPrice'])
                        discount_price = quantity * i['discount']
                        break

            if is_new:
                cart={}
                cart['goodsId'] = goods.pk
                cart['name_kr'] = goods.name_kr
                cart['price'] = goods.sale_price
                cart['discount'] = 0
                cart['quantity'] = quantity
                cart['optionName'] = optionName
                cart['optionPrice'] = optionPrice
                cart['optionList'] = optionList
                cart_list.append(cart)

                additional_price = quantity * (goods.sale_price + optionPrice)

            data['cart_list'] = cart_list
            data['cart_cnt'] = len(cart_list)
            data['cart_total_price'] = shop_table.total_price + additional_price - discount_price
            data['cart_total_discount'] = shop_table.total_discount + discount_price
            data['cart_total_additional'] = shop_table.total_additional
            
            cart_list = json.dumps(cart_list, ensure_ascii=False)
            shop_table.cart = cart_list
            shop_table.total_price += additional_price
            shop_table.total_discount -= discount_price
            shop_table.save()

            return_data = {'data': data,'msg': '상품이 추가 되었습니다.','resultCd': '0000'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

            
        else:
            cart={}
            cart['goodsId'] = goods.pk
            cart['name_kr'] = goods.name_kr
            cart['price'] = goods.sale_price
            cart['discount'] = 0
            cart['quantity'] = quantity
            cart['optionName'] = optionName
            cart['optionPrice'] = optionPrice
            cart['optionList'] = optionList

            cart_list = [cart]
            data['cart_list'] = cart_list
            data['cart_cnt'] = len(cart_list)
            data['cart_total_price'] = (goods.sale_price + optionPrice) * quantity
            data['cart_total_discount'] = 0
            data['cart_total_additional'] = shop_table.total_additional

            cart_list = json.dumps(cart_list, ensure_ascii=False)
            shop_table.total_price = (goods.sale_price + optionPrice) * quantity
            shop_table.total_discount = 0
            shop_table.cart = cart_list
            shop_table.save()
            
            return_data = {'data': data,'msg': '상품이 담겼습니다.','resultCd': '0000'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        

class ShopTableUpdateView(View):
    '''
        수량 수정
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableUpdateView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        index = int(request.POST['index'])
        quantity = int(request.POST['quantity'])

        if quantity <= 0:
            return_data = {'data': {},'msg': 'quantity 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if shop_table.cart:
            cart_list = json.loads(shop_table.cart)
            try:
                price = cart_list[index]['price']
                optionPrice = cart_list[index]['optionPrice']
                discount = cart_list[index]['discount']
                adjusted_quantity = quantity - cart_list[index]['quantity']
                cart_list[index]['quantity'] = quantity
                total_price = shop_table.total_price + ((price+optionPrice-discount)* adjusted_quantity)
                total_discount = shop_table.total_discount + (discount*adjusted_quantity)
            except IndexError:
                return_data = {'data': {},'msg': 'Index Error','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            if total_price < 0:
                for i in cart_list:
                    i['discount'] = 0
                total_price += total_discount
                total_discount = 0

            data = {}
            data['cart_list'] = cart_list
            data['cart_cnt'] = len(cart_list)
            data['cart_total_price'] = total_price
            data['cart_total_discount'] = total_discount
            data['cart_total_additional'] = shop_table.total_additional


            cart_list = json.dumps(cart_list, ensure_ascii=False)
            shop_table.cart = cart_list
                
            shop_table.total_discount = total_discount
            shop_table.total_price = total_price
            shop_table.save()

            return_data = {'data': data,'msg': '상품 수량이 업데이트 되었습니다.','resultCd': '0000'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        else:
            return_data = {'data': {},'msg': '상품이 없습니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        

class ShopTableDeleteView(View):
    '''
        상품 삭제
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableDeleteView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        index = int(request.POST['index'])
        if shop_table.cart:
            cart_list = json.loads(shop_table.cart)
            try:
                price = cart_list[index]['price'] * cart_list[index]['quantity']
                discount = cart_list[index]['discount'] * cart_list[index]['quantity']
                optionPrice = cart_list[index]['optionPrice'] * cart_list[index]['quantity']

                total_price = shop_table.total_price - (price + optionPrice) + discount
                total_discount = shop_table.total_discount - discount

                if total_price < total_discount:
                    for i in cart_list:
                        i['discount'] = 0

                    total_price += total_discount    
                    total_discount = 0
                    
                del cart_list[index]
            except IndexError:
                return_data = {'data': {},'msg': 'Index Error','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
                        
            data = {}
            data['cart_list'] = cart_list
            data['cart_cnt'] = len(cart_list)
            data['cart_total_price'] = total_price
            data['cart_total_discount'] = total_discount
            data['cart_total_additional'] = shop_table.total_additional            

            cart_list = json.dumps(cart_list, ensure_ascii=False)
            shop_table.cart = cart_list              
            shop_table.total_discount = total_discount
            shop_table.total_price = total_price
            shop_table.save()

            return_data = {'data': data,'msg': '상품이 제거되었습니다.','resultCd': '0000'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        else:
            return_data = {'data': {},'msg': '상품이 없습니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        

class ShopTableClearView(View):
    '''
        전체 삭제
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableClearView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        data = {}
        shop_table.cart = None
        shop_table.total_price = 0
        shop_table.total_discount = 0
        shop_table.total_additional = 0
        shop_table.save()

        data['cart_list'] = []
        data['cart_cnt'] = 0
        data['cart_total_price'] = 0
        data['cart_total_discount'] = 0
        data['cart_total_addtional'] = 0

        return_data = {'data': data,'msg': '상품이 모두 제거되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    


class ShopTableGoodsDiscountView(View):
    '''
        상품 할인
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableGoodsDiscountView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        index = int(request.POST['index'])
        discount = int(request.POST['discount'])

        discount = int(request.POST['discount'])
        if shop_table.total_price < discount:
            return_data = {'data': {},'msg': '결제 금액보다 할인금액을 높게 설정할 수 없습니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if shop_table.cart:
            cart_list = json.loads(shop_table.cart)
            try:
                item = cart_list[index]
            except IndexError:
                return_data = {'data': {},'msg': 'Index Error','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            
            if item['price'] + item['optionPrice'] < item['discount'] + discount:
                return_data = {'data': {},'msg': '상품 금액보다 할인금액을 높게 설정할 수 없습니다.','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
            
            cart_list[index]['discount'] += discount

            total_price = shop_table.total_price - (discount * cart_list[index]['quantity'])
            total_discount = shop_table.total_discount + (discount * cart_list[index]['quantity'])
            
            data = {}
            data['cart_list'] = cart_list
            data['cart_cnt'] = len(cart_list)
            data['cart_total_price'] = total_price
            data['cart_total_discount'] = total_discount
            data['cart_total_additional'] = shop_table.total_additional

            cart_list = json.dumps(cart_list, ensure_ascii=False)
            shop_table.cart = cart_list                
            shop_table.total_discount = total_discount
            shop_table.total_price = total_price
            shop_table.save()

            return_data = {'data': data,'msg': '상품 할인이 업데이트 되었습니다.','resultCd': '0000'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        else:
            return_data = {'data': {},'msg': '상품이 없습니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
    

class ShopTableDiscountView(View):
    '''
        테이블 할인
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableDiscountView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        discount = int(request.POST['discount'])

        if shop_table.total_price < discount:
            return_data = {'data': {},'msg': '결제 금액보다 할인금액을 높게 설정할 수 없습니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        total_price = shop_table.total_price - discount
        total_discount = shop_table.total_discount + discount

        shop_table.total_price = total_price
        shop_table.total_discount = total_discount
        
        shop_table.save()

        data = {}
        data['cart_total_price'] = total_price
        data['cart_total_discount'] = total_discount

        return_data = {'data': data,'msg': '할인이 적용 되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopTableDiscountCancelView(View):
    '''
        테이블 할인취소
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableDiscountCancelView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if shop_table.cart:
            cart_list = json.loads(shop_table.cart)
            for i in cart_list:
                i['discount'] = 0
        else:
            cart_list = []
        
        total_price = shop_table.total_price
        total_discount = shop_table.total_discount
        new_total_price = total_price + total_discount

        data = {}
        data['cart_total_price'] = new_total_price
        data['cart_total_discount'] = 0
        data['cart_list'] = cart_list
        data['cart_cnt'] = len(cart_list)
        

        cart_list = json.dumps(cart_list, ensure_ascii=False)
        shop_table.cart = cart_list                
        shop_table.total_price = new_total_price
        shop_table.total_discount = 0
        shop_table.save()


        return_data = {'data': data,'msg': '할인이 취소 되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopTableAdditionalView(View):
    '''
        테이블 추가 요금
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableAdditionalView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        additional = int(request.POST['additional'])

        if additional <= 0:
            return_data = {'data': {},'msg': '추가금액은 0원보다 커야합니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        total_price = shop_table.total_price + additional
        total_additional = shop_table.total_discount + additional

        shop_table.total_price = total_price
        shop_table.total_additional = total_additional
        shop_table.save()

        data = {}
        data['cart_total_price'] = total_price
        data['cart_total_additional'] = total_additional

        return_data = {'data': data,'msg': '추가요금이 적용 되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    

class ShopTableAdditionalCancelView(View):
    '''
        테이블 추가 취소
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableAdditionalCancelView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop_id=shop_id)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        total_price = shop_table.total_price
        total_additional = shop_table.total_additional
        new_total_price = total_price - total_additional

        shop_table.total_price = new_total_price
        shop_table.total_additional = 0
        shop_table.save()

        data = {}
        data['cart_total_price'] = new_total_price
        data['total_additional'] = 0

        return_data = {'data': data,'msg': '추가요금이 취소 되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    
    

class ShopTableCheckoutView(View):
    '''
        shop table checkout
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopTableCheckoutView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        table_no = int(kwargs.get('table_no'))
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")

        try:
            shop_table = ShopTable.objects.get(table_no=table_no, shop=shop)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if shop_table.cart:
            cart_list = json.loads(shop_table.cart)
            if not cart_list:
                if shop_table.total_price == 0:
                    return_data = {'data': {},'msg': '결제 금액이 부족합니다.','resultCd': '0001'}
                    return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                    return HttpResponse(return_data, content_type = "application/json")
        else:
            cart_list = []
            if shop_table.total_price == 0:
                return_data = {'data': {},'msg': '결제 금액이 부족합니다.','resultCd': '0001'}
                return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
                return HttpResponse(return_data, content_type = "application/json")
        
        if shop_table.shop_member:
            shop_member_id = shop_table.shop_member.pk
        else:
            shop_member_id = None

        code = uuid.uuid4().hex
        try:
            with transaction.atomic():
                final = 0
                checkout = Checkout.objects.create(
                    agency = shop.agency,
                    shop = shop,
                    code = code,
                    table_no = shop_table.table_no,
                    shop_member = shop_table.shop_member
                )
                goods_total_discount = 0
                for i in cart_list:
                    total = 0
                    goodsId = i['goodsId']
                    goodsName = i['name_kr']
                    goodsPrice = i['price']
                    discount = i['discount']
                    quantity = i['quantity']
                    optionName = i['optionName']
                    optionPrice = i['optionPrice']
                    optionList = i['optionList']

                    try:
                        goods = Goods.objects.get(pk=goodsId, shop=shop)
                    except:
                        raise ValueError(f'{goodsId} Goods ID error')
                    if goods.sale_price != goodsPrice:
                        raise ValueError(f'{goodsId} Goods prcie error')
                    if quantity <= 0:
                        raise ValueError(f'{goodsId} Goods quantity error')
                    
                    price = goodsPrice + optionPrice - discount
                    total = price * quantity
                    goods_total_discount = discount * quantity

                    checkout_detail = CheckoutDetail.objects.create(
                        checkout = checkout,
                        goods = goods,
                        quantity = quantity,
                        price = price,
                        sale_price = goodsPrice,
                        sale_option_price = optionPrice,
                        total_price = total
                    )
                    # 옵션있을경우 옵션 유효 체크
                    if optionList:
                        option_total = 0
                        checkout_option_bulk_list = []
                        for j in optionList:
                            try:
                                goods_option_detail = GoodsOptionDetail.objects.get(pk=j)
                            except:
                                raise ValueError(f'{goodsId} Goods Option Error')
                            option_total += goods_option_detail.price
                            checkout_option_bulk_list.append(CheckoutDetailOption(checkout_detail=checkout_detail, goods_option_detail=goods_option_detail))

                        if option_total != optionPrice:
                            raise ValueError(f'{goodsId} Goods Option Price error')
                        
                        CheckoutDetailOption.objects.bulk_create(checkout_option_bulk_list)

                    # 총결제금액 합산
                    final += total
            final -= shop_table.total_discount
            if final < 0:
                raise ValueError('Final Price Error')

            checkout.final_price = final
            checkout.final_additional = shop_table.total_additional
            checkout.final_discount = shop_table.total_discount - goods_total_discount
            checkout.save()
                    
            return_data = {
                'data': {
                    'shop_member_id' : shop_member_id,
                    'shop_id':shop.pk,
                    'checkout_id':checkout.pk,
                    'code':checkout.code,
                    'final_price':final,
                    'final_additional':shop_table.total_additional,
                    'final_discount':shop_table.total_discount
                },
                'msg': '주문정보 생성완료',
                'resultCd': '0000',
            }

        except ValueError as e:
            return_data = {
                'data': {},
                'msg': str(e),
                'resultCd': '0001',
            }
        except:
            return_data = {
                'data': {},
                'msg': traceback.format_exc(),
                'resultCd': '0001',
            }

        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
