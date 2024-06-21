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

function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}