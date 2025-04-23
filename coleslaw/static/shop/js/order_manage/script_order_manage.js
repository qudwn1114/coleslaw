const order_tbody = document.getElementById('order_tbody');

const search_form = document.getElementById('search-form');
const order_date_no = document.getElementById('order_date_no');
const orderGoodsModalBody = document.getElementById('orderGoodsModalBody');

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

function changeStatus(id, elem){
    if (!confirm("상태를 수정하시겠습니까?")) {
        getMainOrders();
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
            getMainOrders();
        },
        error: function(error) {
            elem.disabled=false;
            if(error.status == 401){
                customAlert('로그인 해주세요.');
            }
            else if(error.status == 403){
                customAlert('권한이 없습니다!');
            }
            else{
                getMainOrders();
                customAlert(error.status + JSON.stringify(error.responseJSON));
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
            getMainOrders();
        },
        error: function(error) {
            elem.disabled=false;
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
}

function changeStatusModal(id, elem){
    if (!confirm("상태를 수정하시겠습니까?")) {
        loadModal(id);
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
            loadModal(id);
            getMainOrders();
        },
        error: function(error) {
            elem.disabled=false;
            if(error.status == 401){
                customAlert('로그인 해주세요.');
            }
            else if(error.status == 403){
                customAlert('권한이 없습니다!');
            }
            else{
                loadModal(id);
                customAlert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
}

function sendOrderCompleteModal(id, elem){
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
            loadModal(id);
            getMainOrders();
        },
        error: function(error) {
            elem.disabled=false;
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
}


// 모달 열릴때
$('#orderGoodsModal').on('show.bs.modal', function(event) {
    const elem = event.relatedTarget
    const order_id = elem.getAttribute('data-order-id');
    loadModal(order_id);
});

function loadModal(order_id){
    $.ajax({
        type: "GET",
        url: `/shop-manage/${shop_id}/order-goods/${order_id}/`,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(data) {
            let tag = '';
            orderGoodsModalBody.innerHTML = '...';
            tag += `<h5>[주문번호] ${data.order_no} | [주문일시] ${data.createdAt}</h5><hr>`;
            for(let i =0; i<data.order_goods.length; i++){
                tag += `<h6>[제품명] ${data.order_goods[i].name_kr} <br>`
                if(data.order_goods[i].option_kr){
                    tag += `[옵션] ${data.order_goods[i].option_kr} <br>`;
                } 
                tag += `[수량] ${data.order_goods[i].quantity}</h6><hr>`
            }
            tag += `<h6>총 금액 : ${numberWithCommas(data.final_price)} 원</h6>`;
            if(data.status != '2'){
                tag += 
                `<select class="form-select" onchange="changeStatusModal(${data.id}, this)"` 
                if(data.status == '1'){
                  tag += `style="color:#28A745"`;
                }
                tag+=`>
                  <option value="1"`
                  if(data.status == '1'){
                    tag += `selected`
                  }
                  tag += `>결제완료</option>
                  <option value="3" 
                  `;
                  if(data.status == '3'){
                    tag += `selected`
                  }
                  tag += `>준비중</option>
                  <option value="4"`;
                  if(data.status == '4'){
                    tag += `selected`
                  }
                  tag += `>주문완료</option>
                  <option value="5"`;
                  if(data.status == '5'){
                    tag += `selected`
                  }
                  tag += `>수령완료</option>
                  </select>`;
              }
              else{
                tag += `<span class="text-danger">주문취소</span>`;
              }
              if(data.status == '4' && data.order_complete_sms == false){
                tag += `<button class="btn btn-outline-primary w-100" onclick="sendOrderCompleteModal('${data.id}', this);">수령문자요청</button>`
              }
            orderGoodsModalBody.innerHTML = tag;
        },
        error: function(error) {
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
}



function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}


function xlsxDownload(type){
    if(!confirm("엑셀저장하시겠습니까?")){
        return false;
    }
    let url_search = new URLSearchParams(window.location.search);
    url_search.set(type, true);
    window.location.href = `?${url_search.toString()}`;
}


function getMainOrders(){
    let url_search = new URLSearchParams(window.location.search);
    $.ajax({
        type: "GET",
        url: `/shop-manage/${shop_id}/main/orders/?${url_search.toString()}`,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(data) {
          let tag = '';
          if(data.order_list){
            for(let i=0; i<data.order_list.length; i++){
              tag += 
              `<tr>
                  <td>${data.order_list[i].order_no}</td>
                  <td><a href="javascript:;" data-bs-toggle="modal" data-bs-target="#orderGoodsModal" data-order-id="${data.order_list[i].id}">${truncateStr(data.order_list[i].order_name_kr, 16)}</a></td>
                  <td>${numberWithCommas(data.order_list[i].final_price)}</td>
                  <td>${data.order_list[i].order_membername}</td>
                  <td>${data.order_list[i].order_phone}</td>
                  <td>${data.order_list[i].createdAt}</td>
                  <td>`;
                  if(data.order_list[i].status != '2'){
                    tag += 
                    `<select class="form-select" onchange="changeStatus(${data.order_list[i].id}, this)"` 
                    if(data.order_list[i].status == '1'){
                      tag += `style="color:#28A745"`;
                    }
                    tag+=`>
                      <option value="1"`
                      if(data.order_list[i].status == '1'){
                        tag += `selected`
                      }
                      tag += `>결제완료</option>
                      <option value="3" 
                      `;
                      if(data.order_list[i].status == '3'){
                        tag += `selected`
                      }
                      tag += `>준비중</option>
                      <option value="4"`;
                      if(data.order_list[i].status == '4'){
                        tag += `selected`
                      }
                      tag += `>주문완료</option>
                      <option value="5"`;
                      if(data.order_list[i].status == '5'){
                        tag += `selected`
                      }
                      tag += `>수령완료</option>
                      </select>`;
                  }
                  else{
                    tag += `<span class="text-danger">주문취소</span>`;
                  }
                  if(data.order_list[i].status == '4' && data.order_list[i].order_complete_sms == false){
                    tag += `<button class="btn btn-outline-primary w-100" onclick="sendOrderComplete('${data.order_list[i].id}', this);">수령문자요청</button>`
                  }
                tag += `</td>
                </tr>`;
            }
          }
          else{
            tag = `<tr>
                  <td colspan='7'>주문내역이 없습니다.</td>
                </tr>`;
          }
          order_tbody.innerHTML = tag;
  
          console.log(data);
        },
        error: function(error) {
            if(error.status == 401){
                console.log('로그인 해주세요.')
            }
            else if(error.status == 403){
              console.log('권한이 없습니다.')
            }
            else{
                console.log(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
  }

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function truncateStr(str, n){
    return (str.length > n) ? str.slice(0, n-1) + '&hellip;' : str;
};