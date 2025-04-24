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
        customAlert('기간을 3개월 이내로만 설정 하실 수 있습니다.', ()=>{
            document.getElementById('order_date1').click();
        });
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

//이번달
document.getElementById('order_date1').addEventListener('click', function(){
    let startDate = moment().date(1).startOf('day').format('MM/DD/YYYY')
    let endDate = moment().format('MM/DD/YYYY')
    $('input[name="dates').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value= '1';
    search_form.submit();
})

//지난달
document.getElementById('order_date2').addEventListener('click', function(){
    let startDate = moment().subtract(1, 'months').startOf('month').format('MM/DD/YYYY'); // 지난 달 1일
    let endDate = moment().subtract(1, 'months').endOf('month').format('MM/DD/YYYY'); // 지난 달 마지막 날
    $('input[name="dates"]').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates"]').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value = '2';
    search_form.submit();
})
//지지난달
document.getElementById('order_date3').addEventListener('click', function(){
    let startDate = moment().subtract(2, 'months').startOf('month').format('MM/DD/YYYY'); // 지지난 달 1일
    let endDate = moment().subtract(2, 'months').endOf('month').format('MM/DD/YYYY'); // 지지난 달 마지막 날
    $('input[name="dates"]').data('daterangepicker').setStartDate(startDate);
    $('input[name="dates"]').data('daterangepicker').setEndDate(endDate);
    $('input[name="dates"]').val(startDate + ' - ' + endDate);
    order_date_no.value = '3';
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
