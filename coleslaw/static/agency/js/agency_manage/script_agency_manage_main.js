const card_sales = document.getElementById("card_sales");
const card_count = document.getElementById("card_count");
const cash_sales = document.getElementById("cash_sales");
const cash_count = document.getElementById("cash_count");
const cancel_sales = document.getElementById("cancel_sales");
const cancel_count = document.getElementById("cancel_count");
const total_sales = document.getElementById("total_sales");
const total_count = document.getElementById("total_count");

getMainSales();

function getMainSales(){
  $.ajax({
      type: "GET",
      url: `/agency-manage/${agency_id}/main/sales/`,
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


function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}