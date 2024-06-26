const order_tbody = document.getElementById('order_tbody');

const card_sales = document.getElementById("card_sales");
const card_count = document.getElementById("card_count");
const cash_sales = document.getElementById("cash_sales");
const cash_count = document.getElementById("cash_count");
const cancel_sales = document.getElementById("cancel_sales");
const cancel_count = document.getElementById("cancel_count");
const total_sales = document.getElementById("total_sales");
const total_count = document.getElementById("total_count");


const alert_div = document.getElementById("alert_div");
let order_alert_cnt = 0; 
let order_alert_cnt_txt = '';

let cancel_alert_cnt = 0; 
let cancel_alert_cnt_txt = '';

const notificationSocket = new WebSocket(
    `wss://www.coleslaw.co.kr/ws/shop/${shop_id}/order/`
);  
notificationSocket.onopen = function(e) {
    console.log('Socket Open');
};

notificationSocket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.message_type == 'ORDER'){
      order_audio.play();

      order_alert_cnt += 1;
      if(order_alert_cnt > 100){
        order_alert_cnt_txt = `99+`;
      }
      else{
        order_alert_cnt_txt = `${order_alert_cnt}`;
      }
      alert_div.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          <strong>${data.title}</strong> ${data.message}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
          <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-success">
            ${order_alert_cnt_txt}
          </span>
        </div>
      `;
      getMainOrders();
      getMainSales();
    }
    else if (data.message_type == 'CANCEL'){
      cancel_audio.play();

      cancel_alert_cnt += 1;
      if(cancel_alert_cnt > 100){
        cancel_alert_cnt_txt = `99+`;
      }
      else{
        cancel_alert_cnt_txt = `${cancel_alert_cnt}`;
      }
      alert_div.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
          <strong>${data.title}</strong> ${data.message}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
          <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
            ${cancel_alert_cnt_txt}
          </span>
        </div>
      `;
      getMainOrders();
      getMainSales();
    }
};
notificationSocket.onclose = (e) => {
    console.error('Socket closed unexpectedly');
};


function getMainSales(){
  $.ajax({
      type: "GET",
      url: `/shop-manage/${shop_id}/main/sales/`,
      headers: {
          'X-CSRFToken': csrftoken
      },
      success: function(data) {
        card_sales.innerText = numberWithCommas(data.card_sales);
        card_count.innerText = numberWithCommas(data.card_count);
        cash_sales.innerText = numberWithCommas(data.cash_sales);
        cash_count.innerText = numberWithCommas(data.cash_count);
        cancel_sales.innerText = numberWithCommas(data.cancel_sales);
        cancel_count.innerText = numberWithCommas(data.cancel_count);
        total_sales.innerText = numberWithCommas(data.total_sales);
        total_count.innerText = numberWithCommas(data.total_count);
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

function getMainOrders(){
  $.ajax({
      type: "GET",
      url: `/shop-manage/${shop_id}/main/orders/`,
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
                <td><a href="javascript:;" data-bs-toggle="modal" data-bs-target="#orderGoodsModal" data-order-id="${data.order_list[i].id}">${truncateStr(data.order_list[i].order_name, 16)}</a></td>
                <td>${numberWithCommas(data.order_list[i].final_price)}</td>
                <td>${data.order_list[i].order_membername}</td>
                <td>${data.order_list[i].order_phone}</td>
                <td>${data.order_list[i].createdAt}</td>
                <td>`;
                if(data.order_list[i].status != '2'){
                  tag += 
                  `<select class="form-select" onchange="changeStatus(${data.order_list[i].id}, this)">
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
                  tag += `주문취소`;
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

getMainOrders();

function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

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
      url: `/shop-manage/${shop_id}/order-manage/`,
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
              alert('로그인 해주세요.');
          }
          else if(error.status == 403){
              alert('권한이 없습니다!');
          }
          else{
              getMainOrders();
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

function truncateStr(str, n){
  return (str.length > n) ? str.slice(0, n-1) + '&hellip;' : str;
};