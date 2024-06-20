const alert_div = document.getElementById("alert_div");
let alert_cnt = 0; 
let alert_cnt_txt = '';

const notificationSocket = new WebSocket(
    `wss://www.coleslaw.co.kr/ws/shop/${shop_id}/order/`
);  
notificationSocket.onopen = function(e) {
    console.log('Socket Open');
};

notificationSocket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    alert_cnt += 1;
    if(alert_cnt > 100){
      alert_cnt_txt = `99+`;
    }
    else{
      alert_cnt_txt = `${alert_cnt}`;
    }
    alert_div.innerHTML = '';
    alert_div.innerHTML = `
      <div class="alert alert-success alert-dismissible fade show" role="alert">
        <strong>주문!</strong> ${data.message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-success">
          ${alert_cnt_txt}
        </span>
      </div>
    `;
};
notificationSocket.onclose = (e) => {
    console.error('Socket closed unexpectedly');
};