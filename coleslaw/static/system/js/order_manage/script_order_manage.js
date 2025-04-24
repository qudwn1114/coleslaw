const search_form = document.getElementById('search-form');
const order_date_no = document.getElementById('order_date_no');

function SetNum(obj){
    val=obj.value;
    re=/[^0-9]/gi;
    obj.value=val.replace(re,""); 
}

function setAgency(){
    search_form.submit();
}

function setShop(){
    search_form.submit();
}

function setOrderType(){
    search_form.submit();
}

$('input[name="dates"]').daterangepicker({
    autoApply: true,
    autoUpdateInput: false,
    maxDate: new Date()
});

$('input[name="dates"]').on('apply.daterangepicker', function(ev, picker) {
    $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
    order_date_no.value= '0';
    search_form.submit();
});

$('input[name="dates"]').on('cancel.daterangepicker', function(ev, picker) {
    let startDate = moment().format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val('');
    order_date_no.value= '0';
    search_form.submit();
});

//오늘
document.getElementById('order_date1').addEventListener('click', function(){
    let startDate = moment().format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '1';
    search_form.submit();
})
//일주일
document.getElementById('order_date2').addEventListener('click', function(){
    let startDate = moment().subtract(7,'d').format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '2';
    search_form.submit();
})
//1개월
document.getElementById('order_date3').addEventListener('click', function(){
    let startDate = moment().subtract(1, 'months').format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '3';
    search_form.submit();
})
//3개월
document.getElementById('order_date4').addEventListener('click', function(){
    let startDate = moment().subtract(3, 'months').format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '4';
    search_form.submit();
})
//1년
document.getElementById('order_date5').addEventListener('click', function(){
    let startDate = moment().subtract(1, 'years').format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '5';
    search_form.submit();
})
//전체
document.getElementById('order_date6').addEventListener('click', function(){
    let startDate = moment().format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val('');
    order_date_no.value= '6';
    search_form.submit();
})

function xlsxDownload(type){
    customConfirm("엑셀저장하시겠습니까?")
        .then((result) => {
            if (!result) {
            return false;
            }
            let url_search = new URLSearchParams(window.location.search);
            url_search.set(type, true);
            window.location.href = `?${url_search.toString()}`;
        });
}

function createOrderPayment(elem, id){
    customConfirm("주문결제를 생성하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
        }
        elem.disabled = true;
    $.ajax({
        type: "POST",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data:{
            id : id
        },
        datatype: "JSON",
        success: function(data) {
            customAlert(data.message, ()=>{
                location.reload();
            });
        },
        error: function(error) {
            elem.disabled = false;
            if(error.status == 401){
                customAlert('로그인 해주세요.');
            }
            else if(error.status == 403){
                customAlert('권한이 없습니다!');
            }
            else{
                customAlert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
    });
}
