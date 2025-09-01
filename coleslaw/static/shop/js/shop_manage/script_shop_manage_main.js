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
              console.log(i18n.login_required)
          }
          else if(error.status == 403){
            console.log(i18n.no_permission)
          }
          else{
              console.log(error.status + JSON.stringify(error.responseJSON));
          }
      },
  });
}

function getMainOrders(){
  let paginate_by = '10';
  order_tbody.innerHTML = `<tr style="height: 600px;"><td class="text-center" colspan='7' style="vertical-align: middle;"><span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span> Loading...</td></tr>`;
  $.ajax({
      type: "GET",
      url: `/shop-manage/${shop_id}/main/orders/?paginate_by=${paginate_by}&detail=true`,
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
                <td>
                  <a href="javascript:;" data-bs-toggle="modal" data-bs-target="#orderGoodsModal" data-order-id="${data.order_list[i].id}">${truncateStr(data.order_list[i].order_name_kr, 16)}</a>
                  <br>
                  `;
                  for(let j=0; j<data.order_list[i].order_goods.length; j++){
                    let goods_name = data.order_list[i].order_goods[j].name_kr;
                    let goods_option = data.order_list[i].order_goods[j].option_kr;
                    let goods_quantity = data.order_list[i].order_goods[j].quantity;
                    let menu = goods_name;
                    if(goods_quantity > 1){
                      menu += ` x ${goods_quantity}`;
                    }
                    if(goods_option){
                      menu += `<br><small>&nbsp;&nbsp;&#8627;	(${goods_option})</small>`;
                    }
                    tag += `<span>- ${menu}</span><br>`;
                  }
                tag +=  
                `</td>
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
                    tag += `>${i18n.paid}</option>
                    <option value="3" 
                    `;
                    if(data.order_list[i].status == '3'){
                      tag += `selected`
                    }
                    tag += `>${i18n.preparing}</option>
                    <option value="4"`;
                    if(data.order_list[i].status == '4'){
                      tag += `selected`
                    }
                    tag += `>${i18n.completed}</option>
                    <option value="5"`;
                    if(data.order_list[i].status == '5'){
                      tag += `selected`
                    }
                    tag += `>${i18n.received}</option>
                    </select>`;
                }
                else{
                  tag += `<span class="text-danger">${i18n.cancelled}</span>`;
                }
                if(data.order_list[i].status == '4' && data.order_list[i].order_complete_sms == false){
                  tag += `<button class="btn btn-outline-primary w-100" onclick="sendOrderComplete('${data.order_list[i].id}', this);">${i18n.request_sms}</button>`
                }
              tag += `</td>
              </tr>`;
          }
        }
        else{
          tag = `<tr>
                <td colspan='7'>${i18n.empty}</td>
              </tr>`;
        }
        order_tbody.innerHTML = tag;

        console.log(data);
      },
      error: function(error) {
          if(error.status == 401){
              console.log(i18n.login_required)
          }
          else if(error.status == 403){
            console.log(i18n.no_permission)
          }
          else{
              console.log(error.status + JSON.stringify(error.responseJSON));
          }
      },
  });
}

getMainOrders();

function changeStatus(id, elem){
  customConfirm(i18n.confirm_update)
  .then((result) => {
      if (!result) {
        getMainOrders();
          return false;
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
                  customAlert(i18n.login_required);
              }
              else if(error.status == 403){
                  customAlert(i18n.no_permission);
              }
              else{
                  customAlert(error.status + JSON.stringify(error.responseJSON), ()=>{
                    getMainOrders();
                  });
              }
          },
      });
  });
}

function sendOrderComplete(id, elem){
  customConfirm(confirm_send_sms)
  .then((result) => {
      if (!result) { 
          return false;
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
                customAlert(i18n.login_required);
            }
            else if(error.status == 403){
                customAlert(i18n.no_permission);
            }
            else{
                customAlert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
  });
}


function changeStatusModal(id, elem){
  customConfirm(i18n.confirm_update)
  .then((result) => {
      if (!result) {
          loadModal(id);
          return false;
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
            loadModal(id);
            getMainOrders();
        },
        error: function(error) {
            elem.disabled=false;
            if(error.status == 401){
                customAlert(i18n.login_required);
            }
            else if(error.status == 403){
                customAlert(i18n.no_permission);
            }
            else{
                customAlert(error.status + JSON.stringify(error.responseJSON), ()=>{
                  loadModal(id);
                });
            }
        },
    });
  });
}

function sendOrderCompleteModal(id, elem){
  customConfirm(confirm_send_sms)
  .then((result) => {
      if (!result) {
          return false;
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
                customAlert(i18n.login_required);
            }
            else if(error.status == 403){
                customAlert(i18n.no_permission);
            }
            else{
                customAlert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
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
        tag += `<h5>[${i18n.order_no}] ${data.order_no} | [${i18n.order_date}] ${data.createdAt}</h5><hr>`;
        for(let i =0; i<data.order_goods.length; i++){
            tag += `<h6>[${i18n.product_name}] ${data.order_goods[i].name_kr} <br>`
            if(data.order_goods[i].option_kr){
                tag += `[${i18n.option}] ${data.order_goods[i].option_kr} <br>`;
            } 
            tag += `[${i18n.quantity}] ${data.order_goods[i].quantity}</h6><hr>`
        }
        tag += `<h6>${i18n.total_price} : ${numberWithCommas(data.final_price)} ${i18n.currency}</h6>`
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
            tag += `>${i18n.paid}</option>
            <option value="3" 
            `;
            if(data.status == '3'){
              tag += `selected`
            }
            tag += `>${i18n.preparing}</option>
            <option value="4"`;
            if(data.status == '4'){
              tag += `selected`
            }
            tag += `>${i18n.completed}</option>
            <option value="5"`;
            if(data.status == '5'){
              tag += `selected`
            }
            tag += `>${i18n.received}</option>
            </select>`;
        }
        else{
          tag += `<span class="text-danger">${i18n.cancelled}</span>`;
        }
        if(data.status == '4' && data.order_complete_sms == false){
          tag += `<button class="btn btn-outline-primary w-100" onclick="sendOrderCompleteModal('${data.id}', this);">${i18n.request_sms}</button>`
        }
        orderGoodsModalBody.innerHTML = tag;
    },
    error: function(error) {
        if(error.status == 401){
            customAlert(i18n.login_required);
        }
        else if(error.status == 403){
            customAlert(i18n.no_permission);
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

function truncateStr(str, n){
  return (str.length > n) ? str.slice(0, n-1) + '&hellip;' : str;
};