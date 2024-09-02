const search_form = document.getElementById('search-form');
const order_date_no = document.getElementById('order_date_no');


$('input[name="dates"]').daterangepicker({
    autoApply: true,
    autoUpdateInput: false,
    maxDate: new Date(),
});

$('input[name="dates"]').on('apply.daterangepicker', function(ev, picker) {
    let startDate = picker.startDate.format('MM/DD/YYYY');
    let endDate = picker.endDate.format('MM/DD/YYYY');
    
    let _startDate = new Date(startDate);
    let _endDate = new Date(endDate);

    if(_startDate - subtractMonth(_endDate, 3) < 0){
        alert('기간을 3개월 이내로만 설정 하실 수 있습니다.');
        document.getElementById('order_date1').click();
        return;
    }
    $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
    order_date_no.value= '0';
    search_form.submit();
});


function subtractMonth(date, months) {
    let d = date.getDate();
    date.setMonth(date.getMonth() - months);
    if (date.getDate() != d) {
      date.setDate(0);
    }
    return date;
}

//오늘
document.getElementById('order_date1').addEventListener('click', function(){
    let startDate = moment().format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '1';
    search_form.submit();
});

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

function xlsxDownload(type){
    if(!confirm("엑셀저장하시겠습니까?")){
        return false;
    }
    let url_search = new URLSearchParams(window.location.search);
    url_search.set(type, true);
    window.location.href = `?${url_search.toString()}`;
}