const order_date_no = document.getElementById('order_date_no');
const orderGoodsModalBody = document.getElementById('orderGoodsModalBody');

$('input[name="dates"]').daterangepicker({
    autoApply: true,
    autoUpdateInput: false,
    maxDate: new Date()
});

$('input[name="dates"]').on('apply.daterangepicker', function(ev, picker) {
    $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
});

$('input[name="dates"]').on('cancel.daterangepicker', function(ev, picker) {
    let startDate = moment().format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val('');
    order_date_no.value= '0';
});
//오늘
document.getElementById('order_date1').addEventListener('click', function(){
    let startDate = moment().format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '1';
})
//일주일
document.getElementById('order_date2').addEventListener('click', function(){
    let startDate = moment().subtract(7,'d').format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '2';
})
//1개월
document.getElementById('order_date3').addEventListener('click', function(){
    let startDate = moment().subtract(1, 'months').format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '3';
})
//3개월
document.getElementById('order_date4').addEventListener('click', function(){
    let startDate = moment().subtract(3, 'months').format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '4';
})
//1년
document.getElementById('order_date5').addEventListener('click', function(){
    let startDate = moment().subtract(1, 'years').format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '5';
})
//전체
document.getElementById('order_date6').addEventListener('click', function(){
    let startDate = moment().format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val('');
    order_date_no.value= '6';
})

function changeStatus(id, elem){
    if (!confirm("상태를 수정하시겠습니까?")) {
        location.reload();
        return;
    }
    let data = {
        order_id : id,
        order_status : elem.value
    };
    elem.disabled=true;
    $.ajax({
        type: "PUT",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify(data),
        datatype: "JSON",
        success: function(data) {
            location.reload();
        },
        error: function(error) {
            elem.disabled=false;
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                location.reload();
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
}

function sendOrderComplete(id, elem){
    if (!confirm("완료 문자를 보내시겠습니까?")) {
        return;
    }
    let data = {
        order_id : id
    };
    elem.disabled=true;
    $.ajax({
        type: "POST",
        url: `/shop-manage/${shop_id}/order-complete-sms/`,
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: data,
        datatype: "JSON",
        success: function(data) {
            location.reload();
        },
        error: function(error) {
            elem.disabled=false;
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
}

// 모달 열릴때
$('#orderGoodsModal').on('show.bs.modal', function(event) {
    const elem = event.relatedTarget
    const order_id = elem.getAttribute('data-order-id');
    $.ajax({
        type: "GET",
        url: `/shop-manage/${shop_id}/order-goods/${order_id}/`,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(data) {
            let tag = '';
            orderGoodsModalBody.innerHTML = '...';
            tag += `<h5>[주문일시] ${data.createdAt}</h5><hr>`;
            for(let i =0; i<data.order_goods.length; i++){
                tag += `<h6>[제품명] ${data.order_goods[i].name} <br>`
                if(data.order_goods[i].option){
                    tag += `[옵션] ${data.order_goods[i].option} <br>`;
                } 
                tag += `[수량] ${data.order_goods[i].quantity}</h6><hr>`
            }
            tag += `<h6>총 금액 : ${numberWithCommas(data.final_price)} 원</h6>`
            orderGoodsModalBody.innerHTML = tag;
            console.log(data);
        },
        error: function(error) {
            elem.disabled=false;
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
});

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}